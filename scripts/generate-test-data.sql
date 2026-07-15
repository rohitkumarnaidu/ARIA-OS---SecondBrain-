-- =============================================================================
-- Second Brain OS — Test Data Generator
-- Usage: psql -h <host> -d <db> -U <user> -f scripts/generate-test-data.sql
-- =============================================================================
-- Generates test data for all 18 tables scoped to test-user-id.
-- Idempotent: safe to re-run (DELETE before INSERT).

BEGIN;

DO $$
DECLARE
    uid CONSTANT TEXT := 'test-user-id';
    now_ts TIMESTAMPTZ := NOW();
BEGIN

-- Clean existing test data in dependency order (children first)
DELETE FROM chat_messages WHERE user_id = uid;
DELETE FROM daily_briefings WHERE user_id = uid;
DELETE FROM weekly_reviews WHERE user_id = uid;
DELETE FROM habit_logs WHERE user_id = uid;
DELETE FROM sleep_logs WHERE user_id = uid;
DELETE FROM time_logs WHERE user_id = uid;
DELETE FROM income_logs WHERE user_id = uid;
DELETE FROM opportunities WHERE user_id = uid;
DELETE FROM resources WHERE user_id = uid;
DELETE FROM ideas WHERE user_id = uid;
DELETE FROM projects WHERE user_id = uid;
DELETE FROM habits WHERE user_id = uid;
DELETE FROM courses WHERE user_id = uid;
DELETE FROM tasks WHERE user_id = uid;
DELETE FROM goals WHERE user_id = uid;
DELETE FROM learning_progress WHERE user_id = uid;
DELETE FROM aria_memory WHERE user_id = uid;
DELETE FROM users_profile WHERE user_id = uid;

-- 1. users_profile
INSERT INTO users_profile (id, user_id, name, email, created_at, updated_at)
VALUES (
    gen_random_uuid()::text,
    uid,
    'Test User',
    'test@secondbrain.os',
    now_ts, now_ts
);

-- 2. tasks (5)
INSERT INTO tasks (id, user_id, title, description, priority, status, category, due_date, estimated_minutes, is_recurring, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'Complete ML assignment', 'Finish the neural network implementation', 'high', 'pending', 'study', now_ts + INTERVAL '2 days', 180, false, now_ts, now_ts),
    (gen_random_uuid()::text, uid, 'Review PR for project X', 'Code review the auth module', 'urgent', 'pending', 'project', now_ts + INTERVAL '1 day', 60, false, now_ts, now_ts),
    (gen_random_uuid()::text, uid, 'Buy groceries', 'Weekly groceries from the list', 'low', 'completed', 'personal', now_ts - INTERVAL '1 day', 45, true, now_ts - INTERVAL '2 days', now_ts),
    (gen_random_uuid()::text, uid, 'Study for DBMS exam', 'Chapter 5-8 revision', 'high', 'pending', 'study', now_ts + INTERVAL '5 days', 240, false, now_ts, now_ts),
    (gen_random_uuid()::text, uid, 'Update resume', 'Add latest internship experience', 'medium', 'pending', 'personal', now_ts + INTERVAL '7 days', 90, false, now_ts, now_ts);

-- 3. courses (3)
INSERT INTO courses (id, user_id, title, platform, url, total_videos, completed_videos, deadline, why_enrolled, status, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'Machine Learning Specialization', 'Coursera', 'https://coursera.org/ml', 120, 45, now_ts + INTERVAL '90 days', 'Career growth in AI', 'in_progress', now_ts - INTERVAL '30 days', now_ts),
    (gen_random_uuid()::text, uid, 'System Design Interview', 'YouTube', 'https://youtube.com/playlist', 30, 30, now_ts - INTERVAL '5 days', 'Interview prep', 'completed', now_ts - INTERVAL '60 days', now_ts),
    (gen_random_uuid()::text, uid, 'React Native - The Practical Guide', 'Udemy', 'https://udemy.com/rn-guide', 200, 78, now_ts + INTERVAL '60 days', 'Mobile app development', 'in_progress', now_ts - INTERVAL '20 days', now_ts);

-- 4. goals (3)
INSERT INTO goals (id, user_id, title, description, roadmap_type, target_date, hours_per_day, days_per_week, intensity, status, progress, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'Learn React Native', 'Build a production-ready mobile app', 'career_skills', now_ts + INTERVAL '90 days', 2.0, 5, 'high', 'active', 30, now_ts - INTERVAL '30 days', now_ts),
    (gen_random_uuid()::text, uid, 'Get AWS Certified', 'Solutions Architect Associate', 'certification', now_ts + INTERVAL '180 days', 1.5, 4, 'medium', 'active', 15, now_ts - INTERVAL '14 days', now_ts),
    (gen_random_uuid()::text, uid, 'Run a Marathon', 'Complete full marathon by year end', 'fitness', now_ts + INTERVAL '180 days', 1.0, 6, 'medium', 'active', 10, now_ts - INTERVAL '7 days', now_ts);

-- 5. habits (5)
INSERT INTO habits (id, user_id, name, frequency, time_target_minutes, is_active, current_streak, best_streak, consistency_percentage, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'Morning Meditation', 'daily', 15, true, 7, 14, 85.0, now_ts - INTERVAL '30 days', now_ts),
    (gen_random_uuid()::text, uid, 'Read Technical Books', 'daily', 30, true, 12, 21, 78.5, now_ts - INTERVAL '60 days', now_ts),
    (gen_random_uuid()::text, uid, 'Gym Workout', 'weekly', 60, true, 3, 8, 62.0, now_ts - INTERVAL '45 days', now_ts),
    (gen_random_uuid()::text, uid, 'Write Journal', 'daily', 10, true, 5, 15, 72.0, now_ts - INTERVAL '30 days', now_ts),
    (gen_random_uuid()::text, uid, 'Drink 8 Glasses Water', 'daily', 0, true, 4, 10, 65.0, now_ts - INTERVAL '20 days', now_ts);

-- 6. habit_logs (7)
INSERT INTO habit_logs (id, user_id, habit_id, date, completed, minutes_spent, created_at)
SELECT
    gen_random_uuid()::text, uid, h.id, now_ts - (n || ' days')::INTERVAL, true, 15, now_ts
FROM (SELECT id FROM habits WHERE user_id = uid AND name = 'Morning Meditation' LIMIT 1) h
CROSS JOIN generate_series(0, 6) AS n;

-- 7. sleep_logs (3)
INSERT INTO sleep_logs (id, user_id, bedtime, wake_time, quality_rating, duration_hours, sleep_score, sleep_debt, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, (now_ts - INTERVAL '1 day') + TIME '23:30', now_ts + TIME '07:00', 4, 7.5, 78, 0.5, now_ts, now_ts),
    (gen_random_uuid()::text, uid, (now_ts - INTERVAL '2 days') + TIME '00:15', now_ts - INTERVAL '1 day' + TIME '06:30', 3, 6.25, 62, 1.75, now_ts, now_ts),
    (gen_random_uuid()::text, uid, (now_ts - INTERVAL '3 days') + TIME '22:45', now_ts - INTERVAL '2 days' + TIME '06:45', 5, 8.0, 92, 0.0, now_ts, now_ts);

-- 8. income_logs (2)
INSERT INTO income_logs (id, user_id, amount, date, description, hours_spent, created_at) VALUES
    (gen_random_uuid()::text, uid, 500.00, now_ts - INTERVAL '5 days', 'Website redesign for client', 10.0, now_ts - INTERVAL '5 days'),
    (gen_random_uuid()::text, uid, 1200.00, now_ts - INTERVAL '30 days', 'Monthly part-time stipend', NULL, now_ts - INTERVAL '30 days');

-- 9. projects
INSERT INTO projects (id, user_id, title, description, phase, live_url, repo_url, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'Second Brain OS', 'Personal AI productivity system', 'execution', 'https://secondbrain.os', 'https://github.com/user/secondbrain', now_ts - INTERVAL '60 days', now_ts);

-- 10. ideas
INSERT INTO ideas (id, user_id, title, description, stage, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'AI Study Buddy', 'An AI-powered study assistant', 'validating', now_ts - INTERVAL '14 days', now_ts);

-- 11. resources
INSERT INTO resources (id, user_id, title, url, resource_type, tags, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'React Documentation', 'https://react.dev', 'article', ARRAY['react', 'frontend', 'docs'], now_ts, now_ts);

-- 12. opportunities
INSERT INTO opportunities (id, user_id, title, company, url, opportunity_type, match_score, deadline, notes, created_at, updated_at) VALUES
    (gen_random_uuid()::text, uid, 'SWE Intern at Google', 'Google', 'https://google.com/careers', 'internship', 85, now_ts + INTERVAL '30 days', 'Strong match in ML skills', now_ts, now_ts);

-- 13. time_logs
INSERT INTO time_logs (id, user_id, task_id, description, started_at, ended_at, duration_seconds, is_deep_work, created_at) VALUES
    (gen_random_uuid()::text, uid, NULL, 'Working on Second Brain OS', now_ts - INTERVAL '3 hours', now_ts - INTERVAL '2 hours', 3600, TRUE, now_ts);

-- 14. chat_messages
INSERT INTO chat_messages (id, user_id, role, content, agent, created_at) VALUES
    (gen_random_uuid()::text, uid, 'user', 'What does my day look like?', NULL, now_ts - INTERVAL '2 hours'),
    (gen_random_uuid()::text, uid, 'assistant', 'You have 5 pending tasks today. Your highest priority is fixing the login bug.', 'planner', now_ts - INTERVAL '2 hours');

-- 15. daily_briefings
INSERT INTO daily_briefings (id, user_id, date, briefing_data, created_at) VALUES
    (gen_random_uuid()::text, uid, CURRENT_DATE,
     '{"summary":"Productive day ahead","top_priority":"Fix login bug","tasks_count":5,"sleep_score":78}'::jsonb,
     now_ts);

-- 16. weekly_reviews
INSERT INTO weekly_reviews (id, user_id, week_start, review_data, created_at) VALUES
    (gen_random_uuid()::text, uid, date_trunc('week', now_ts)::date,
     '{"summary":"Good week","tasks_completed":12,"focus_score":72,"top_insight":"Increase deep work sessions"}'::jsonb,
     now_ts);

-- 17. aria_memory
INSERT INTO aria_memory (id, user_id, memory_type, content, confidence, created_at) VALUES
    (gen_random_uuid()::text, uid, 'preference', 'Preferred learning style: visual', 0.9, now_ts),
    (gen_random_uuid()::text, uid, 'pattern', 'Focus peak hours: 09:00-12:00', 0.8, now_ts);

-- 18. learning_progress
INSERT INTO learning_progress (id, user_id, date, metrics, created_at) VALUES
    (gen_random_uuid()::text, uid, CURRENT_DATE,
     '{"hours_studied":2.5,"topics_covered":["ML","DBMS"],"quiz_scores":[85,92]}'::jsonb,
     now_ts);

RAISE NOTICE 'Test data inserted for user: %', uid;

END $$;

COMMIT;
