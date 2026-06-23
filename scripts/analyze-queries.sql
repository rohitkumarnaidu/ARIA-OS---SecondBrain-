-- Query Analysis Script for ARIA OS
-- Run in Supabase SQL Editor to identify slow queries and missing indexes

-- 1. Check for sequential scans (missing indexes)
SELECT
    schemaname,
    relname AS table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    n_live_tup AS row_estimate,
    (seq_tup_read / NULLIF(seq_scan, 0))::bigint AS avg_rows_per_seq_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0 AND n_live_tup > 1000
ORDER BY seq_tup_read DESC
LIMIT 20;

-- 2. Check for unused indexes
SELECT
    schemaname,
    tablename AS table_name,
    indexname AS index_name,
    idx_scan AS index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 3. Check index size vs table size ratios
SELECT
    t.schemaname,
    t.tablename AS table_name,
    pg_size_pretty(pg_total_relation_size(t.schemaname || '.' || t.tablename)) AS total_size,
    pg_size_pretty(pg_table_size(t.schemaname || '.' || t.tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(t.schemaname || '.' || t.tablename)) AS index_size,
    ROUND(100.0 * pg_indexes_size(t.schemaname || '.' || t.tablename) /
        NULLIF(pg_total_relation_size(t.schemaname || '.' || t.tablename), 0), 1) AS index_pct
FROM pg_tables t
WHERE t.schemaname = 'public'
ORDER BY pg_total_relation_size(t.schemaname || '.' || t.tablename) DESC;

-- 4. Check for missing indexes on foreign keys
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND NOT EXISTS (
        SELECT 1
        FROM pg_index i
        JOIN pg_class c ON i.indexrelid = c.oid
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE c.relname LIKE 'idx\_%'
        AND a.attname = kcu.column_name
    )
ORDER BY tc.table_name;

-- 5. Find tables without indexes on user_id (critical for RLS performance)
SELECT
    c.relname AS table_name,
    CASE WHEN i.idx_count IS NULL THEN 'NO INDEX ON user_id' ELSE 'OK' END AS status
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN (
    SELECT indrelid, COUNT(*) AS idx_count
    FROM pg_index i
    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
    WHERE a.attname = 'user_id'
    GROUP BY indrelid
) i ON c.oid = i.indrelid
WHERE n.nspname = 'public'
    AND c.relkind = 'r'
    AND c.relname NOT LIKE 'pg_%'
    AND c.relname NOT LIKE '_prisma_%'
ORDER BY c.relname;

-- 6. Check for tables with high bloat (vacuum-needed)
SELECT
    schemaname,
    relname AS table_name,
    n_dead_tup AS dead_rows,
    n_live_tup AS live_rows,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 20;
