-- =============================================================================
-- Second Brain OS — Test Data Generator (Enterprise)
-- Usage: psql -h <host> -d <db> -U <user> -f scripts/generate-test-data.sql
-- =============================================================================
-- Wraps all inserts in a transaction. Rolls back on any failure.
-- Idempotent: safe to re-run (DELETE before INSERT).

BEGIN;

-- Clean existing test data in dependency order (children first)
DELETE FROM chat_messages;
DELETE FROM daily_briefings;
DELETE FROM weekly_reviews;
DELETE FROM habit_logs;
DELETE FROM sleep_logs;
DELETE FROM time_entries;
DELETE FROM income_entries;
DELETE FROM opportunities;
DELETE FROM resources;
DELETE FROM ideas;
DELETE FROM projects;
DELETE FROM habits;
DELETE FROM courses;
DELETE FROM tasks;
DELETE FROM goals;
DELETE FROM learning_progress;
DELETE FROM memory;
DELETE FROM users;

-- Seed user (UUID matches typical test auth user)
INSERT INTO users (id, email, full_name, avatar_url, preferences, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'test@secondbrain.os',
  'Test User',
  'https://api.dicebear.com/9.x/avataaars/svg?seed=test',
  '{"theme": "dark", "accent_color": "#6366F1", "notifications_enabled": true}'::jsonb,
  NOW(),
  NOW()
);

-- Tasks (15 - mix of pending/done/recurring)
INSERT INTO tasks (id, user_id, title, description, priority, status, category, due_date, estimated_minutes, is_recurring, recurring_frequency, created_at, updated_at) VALUES
  ('t-001', '00000000-0000-0000-0000-000000000001', 'Complete ML assignment', 'Finish the neural network implementation', 'high', 'pending', 'academic', NOW() + INTERVAL '2 days', 180, false, NULL, NOW(), NOW()),
  ('t-002', '00000000-0000-0000-0000-000000000001', 'Review PR for project X', 'Code review the authentication module', 'urgent', 'pending', 'project', NOW() + INTERVAL '1 day', 60, false, NULL, NOW(), NOW()),
  ('t-003', '00000000-0000-0000-0000-000000000001', 'Buy groceries', 'Weekly groceries from the list', 'low', 'completed', 'personal', NOW() - INTERVAL '1 day', 45, true, 'weekly', NOW() - INTERVAL '2 days', NOW()),
  ('t-004', '00000000-0000-0000-0000-000000000001', 'Study for DBMS exam', 'Chapter 5-8 revision', 'high', 'pending', 'academic', NOW() + INTERVAL '5 days', 240, false, NULL, NOW(), NOW()),
  ('t-005', '00000000-0000-0000-0000-000000000001', 'Update resume', 'Add latest internship experience', 'medium', 'pending', 'career', NOW() + INTERVAL '7 days', 90, false, NULL, NOW(), NOW()),
  ('t-006', '00000000-0000-0000-0000-000000000001', 'Morning workout', '30 min cardio', 'medium', 'pending', 'health', NOW() + INTERVAL '0 days', 30, true, 'daily', NOW(), NOW()),
  ('t-007', '00000000-0000-0000-0000-000000000001', 'Fix login bug', 'Session expires incorrectly on Safari', 'urgent', 'pending', 'project', NOW() + INTERVAL '0 days', 120, false, NULL, NOW(), NOW()),
  ('t-008', '00000000-0000-0000-0000-000000000001', 'Read Clean Architecture', 'Chapter 7-9', 'low', 'pending', 'learning', NOW() + INTERVAL '14 days', 90, false, NULL, NOW(), NOW()),
  ('t-009', '00000000-0000-0000-0000-000000000001', 'Prepare presentation', 'AI in Healthcare overview', 'high', 'completed', 'academic', NOW() - INTERVAL '1 day', 150, false, NULL, NOW() - INTERVAL '3 days', NOW()),
  ('t-010', '00000000-0000-0000-0000-000000000001', 'Pay electricity bill', 'Due on 25th', 'medium', 'pending', 'personal', NOW() + INTERVAL '3 days', 10, false, NULL, NOW(), NOW()),
  ('t-011', '00000000-0000-0000-0000-000000000001', 'Write blog post', 'How I built Second Brain OS', 'medium', 'pending', 'personal', NOW() + INTERVAL '10 days', 180, false, NULL, NOW(), NOW()),
  ('t-012', '00000000-0000-0000-0000-000000000001', 'Apply for internships', 'Target 5 applications this week', 'high', 'pending', 'career', NOW() + INTERVAL '4 days', 120, false, NULL, NOW(), NOW()),
  ('t-013', '00000000-0000-0000-0000-000000000001', 'Set up CI/CD pipeline', 'GitHub Actions for the project', 'high', 'completed', 'project', NOW() - INTERVAL '2 days', 90, false, NULL, NOW() - INTERVAL '4 days', NOW()),
  ('t-014', '00000000-0000-0000-0000-000000000001', 'Practice DSA', 'Solve 3 medium LeetCode problems', 'medium', 'pending', 'academic', NOW() + INTERVAL '0 days', 120, true, 'daily', NOW(), NOW()),
  ('t-015', '00000000-0000-0000-0000-000000000001', 'Call dentist', 'Schedule annual checkup', 'low', 'pending', 'personal', NOW() + INTERVAL '7 days', 15, false, NULL, NOW(), NOW());

-- Courses (4)
INSERT INTO courses (id, user_id, title, platform, url, total_videos, completed_videos, deadline, why_enrolled, status, created_at, updated_at) VALUES
  ('c-001', '00000000-0000-0000-0000-000000000001', 'Machine Learning Specialization', 'Coursera', 'https://coursera.org/ml', 120, 45, NOW() + INTERVAL '90 days', 'Career growth in AI', 'in_progress', NOW() - INTERVAL '30 days', NOW()),
  ('c-002', '00000000-0000-0000-0000-000000000001', 'System Design Interview', 'YouTube', 'https://youtube.com/playlist', 30, 30, NOW() - INTERVAL '5 days', 'Interview prep', 'completed', NOW() - INTERVAL '60 days', NOW()),
  ('c-003', '00000000-0000-0000-0000-000000000001', 'React Native - The Practical Guide', 'Udemy', 'https://udemy.com/rn-guide', 200, 78, NOW() + INTERVAL '60 days', 'Mobile app development skills', 'in_progress', NOW() - INTERVAL '20 days', NOW()),
  ('c-004', '00000000-0000-0000-0000-000000000001', 'PostgreSQL Deep Dive', 'YouTube', 'https://youtube.com/pgsql', 40, 0, NOW() + INTERVAL '45 days', 'Database optimization for project', 'not_started', NOW(), NOW());

-- Goals (3)
INSERT INTO goals (id, user_id, title, description, roadmap_type, target_date, hours_per_day, days_per_week, intensity, status, progress, created_at, updated_at) VALUES
  ('g-001', '00000000-0000-0000-0000-000000000001', 'Learn React Native', 'Build a production-ready mobile app', 'career_skills', NOW() + INTERVAL '90 days', 2.0, 5.0, 'high', 'active', 30, NOW() - INTERVAL '30 days', NOW()),
  ('g-002', '00000000-0000-0000-0000-000000000001', 'Get AWS Certified', 'Solutions Architect Associate', 'certification', NOW() + INTERVAL '180 days', 1.5, 4.0, 'medium', 'active', 15, NOW() - INTERVAL '14 days', NOW()),
  ('g-003', '00000000-0000-0000-0000-000000000001', 'Run a Marathon', 'Complete full marathon by year end', 'fitness', NOW() + INTERVAL '180 days', 1.0, 6.0, 'medium', 'active', 10, NOW() - INTERVAL '7 days', NOW());

-- Habits (5)
INSERT INTO habits (id, user_id, name, frequency, time_target_minutes, is_active, current_streak, best_streak, consistency_percentage, created_at, updated_at) VALUES
  ('h-001', '00000000-0000-0000-0000-000000000001', 'Morning Meditation', 'daily', 15, true, 7, 14, 85.0, NOW() - INTERVAL '30 days', NOW()),
  ('h-002', '00000000-0000-0000-0000-000000000001', 'Read Technical Books', 'daily', 30, true, 12, 21, 78.5, NOW() - INTERVAL '60 days', NOW()),
  ('h-003', '00000000-0000-0000-0000-000000000001', 'Gym Workout', 'weekly', 60, true, 3, 8, 62.0, NOW() - INTERVAL '45 days', NOW()),
  ('h-004', '00000000-0000-0000-0000-000000000001', 'Write Journal', 'daily', 10, true, 5, 15, 72.0, NOW() - INTERVAL '30 days', NOW()),
  ('h-005', '00000000-0000-0000-0000-000000000001', 'Drink 8 Glasses Water', 'daily', 0, true, 4, 10, 65.0, NOW() - INTERVAL '20 days', NOW());

-- Habit logs (30 - last 30 days for h-001)
INSERT INTO habit_logs (id, user_id, habit_id, date, completed, minutes_spent, created_at)
SELECT
  gen_random_uuid()::text,
  '00000000-0000-0000-0000-000000000001',
  'h-001',
  CURRENT_DATE - (n || ' days')::INTERVAL,
  CASE WHEN random() > 0.2 THEN true ELSE false END,
  CASE WHEN random() > 0.2 THEN 15 ELSE 0 END,
  NOW()
FROM generate_series(0, 29) AS n;

-- Projects (3)
INSERT INTO projects (id, user_id, title, description, phase, live_url, repo_url, created_at, updated_at) VALUES
  ('p-001', '00000000-0000-0000-0000-000000000001', 'Second Brain OS', 'Personal AI productivity system', 'active', 'https://secondbrain.os', 'https://github.com/user/secondbrain', NOW() - INTERVAL '60 days', NOW()),
  ('p-002', '00000000-0000-0000-0000-000000000001', 'E-commerce Platform', 'Full-stack MERN marketplace', 'active', NULL, 'https://github.com/user/ecom', NOW() - INTERVAL '30 days', NOW()),
  ('p-003', '00000000-0000-0000-0000-000000000001', 'Portfolio Website', 'Personal portfolio with blog', 'completed', 'https://user.dev', 'https://github.com/user/portfolio', NOW() - INTERVAL '90 days', NOW() - INTERVAL '10 days');

-- Ideas (3)
INSERT INTO ideas (id, user_id, title, description, stage, created_at, updated_at) VALUES
  ('i-001', '00000000-0000-0000-0000-000000000001', 'AI Study Buddy', 'An AI-powered study assistant that adapts to learning pace', 'validating', NOW() - INTERVAL '14 days', NOW()),
  ('i-002', '00000000-0000-0000-0000-000000000001', 'Freelance Rate Analyzer', 'Tool that analyzes market rates for tech freelancers', 'raw', NOW() - INTERVAL '5 days', NOW()),
  ('i-003', '00000000-0000-0000-0000-000000000001', 'Habit Gamification Engine', 'Turn habit tracking into an RPG-like experience', 'building', NOW() - INTERVAL '21 days', NOW());

-- Resources (5)
INSERT INTO resources (id, user_id, title, url, resource_type, tags, created_at, updated_at) VALUES
  ('r-001', '00000000-0000-0000-0000-000000000001', 'React Documentation', 'https://react.dev', 'article', ARRAY['react', 'frontend', 'docs'], NOW(), NOW()),
  ('r-002', '00000000-0000-0000-0000-000000000001', 'System Design Primer', 'https://github.com/donnemartin/system-design-primer', 'article', ARRAY['system-design', 'interview'], NOW() - INTERVAL '10 days', NOW()),
  ('r-003', '00000000-0000-0000-0000-000000000001', 'Clean Architecture by Uncle Bob', 'https://amazon.com/clean-architecture', 'book', ARRAY['architecture', 'software-design'], NOW() - INTERVAL '30 days', NOW()),
  ('r-004', '00000000-0000-0000-0000-000000000001', 'Building Microservices', 'https://youtube.com/microservices', 'video', ARRAY['microservices', 'backend'], NOW() - INTERVAL '20 days', NOW()),
  ('r-005', '00000000-0000-0000-0000-000000000001', 'VS Code Setup for Python', 'https://code.visualstudio.com/docs/python', 'article', ARRAY['python', 'tools', 'setup'], NOW() - INTERVAL '7 days', NOW());

-- Opportunities (3)
INSERT INTO opportunities (id, user_id, title, company, url, opportunity_type, match_score, deadline, notes, created_at, updated_at) VALUES
  ('o-001', '00000000-0000-0000-0000-000000000001', 'SWE Intern at Google', 'Google', 'https://google.com/careers', 'internship', 85, NOW() + INTERVAL '30 days', 'Strong match in ML skills', NOW(), NOW()),
  ('o-002', '00000000-0000-0000-0000-000000000001', 'Hackathon: AI for Good', 'Devpost', 'https://devpost.com/ai-for-good', 'hackathon', 70, NOW() + INTERVAL '14 days', 'Team of 4, need a designer', NOW(), NOW()),
  ('o-003', '00000000-0000-0000-0000-000000000001', 'Open Source Contributor', 'GitHub', 'https://github.com/langchain-ai/langchain', 'open_source', 90, NULL, 'Good first issues tagged', NOW(), NOW());

-- Income entries (5)
INSERT INTO income_entries (id, user_id, source_type, amount, date, description, hourly_rate, hours_worked, created_at, updated_at) VALUES
  ('inc-001', '00000000-0000-0000-0000-000000000001', 'freelance', 500.00, NOW() - INTERVAL '5 days', 'Website redesign for client', 50.00, 10.0, NOW() - INTERVAL '5 days', NOW()),
  ('inc-002', '00000000-0000-0000-0000-000000000001', 'freelance', 750.00, NOW() - INTERVAL '12 days', 'API integration project', 75.00, 10.0, NOW() - INTERVAL '12 days', NOW()),
  ('inc-003', '00000000-0000-0000-0000-000000000001', 'part_time', 1200.00, NOW() - INTERVAL '30 days', 'Monthly part-time stipend', NULL, NULL, NOW() - INTERVAL '30 days', NOW()),
  ('inc-004', '00000000-0000-0000-0000-000000000001', 'freelance', 300.00, NOW() - INTERVAL '2 days', 'Bug fix sprint', 60.00, 5.0, NOW() - INTERVAL '2 days', NOW()),
  ('inc-005', '00000000-0000-0000-0000-000000000001', 'scholarship', 2000.00, NOW() - INTERVAL '60 days', 'Semester performance award', NULL, NULL, NOW() - INTERVAL '60 days', NOW());

-- Sleep logs (14 - last 14 days)
INSERT INTO sleep_logs (id, user_id, bedtime, wake_time, quality_rating, duration_hours, sleep_score, sleep_debt, created_at, updated_at)
SELECT
  'sl-' || n,
  '00000000-0000-0000-0000-000000000001',
  (CURRENT_DATE - (n || ' days')::INTERVAL) + TIME '23:30',
  (CURRENT_DATE - (n || ' days')::INTERVAL) + TIME '07:00',
  (random() * 2 + 3)::int,
  7.5 + (random() - 0.5) * 2,
  (65 + random() * 30)::int,
  (random() * 2)::numeric(4,2),
  NOW(),
  NOW()
FROM generate_series(0, 13) AS n;

-- Time entries (10 - deep work sessions)
INSERT INTO time_entries (id, user_id, start_time, end_time, duration_minutes, activity_type, description, created_at)
SELECT
  'te-' || n,
  '00000000-0000-0000-0000-000000000001',
  NOW() - (n || ' hours')::INTERVAL,
  NOW() - ((n - 1) || ' hours')::INTERVAL,
  60,
  CASE WHEN random() > 0.5 THEN 'deep_work' ELSE 'pomodoro' END,
  CASE WHEN random() > 0.5 THEN 'Working on Second Brain OS' ELSE 'Studying ML' END,
  NOW()
FROM generate_series(1, 10) AS n;

-- Chat messages (5 - sample conversation)
INSERT INTO chat_messages (id, user_id, role, content, agent, created_at)
VALUES
  ('cm-001', '00000000-0000-0000-0000-000000000001', 'user', 'What does my day look like?', NULL, NOW() - INTERVAL '2 hours'),
  ('cm-002', '00000000-0000-0000-0000-000000000001', 'assistant', "You have 5 pending tasks today. Your highest priority is fixing the login bug (urgent). You also have a DSA practice session and morning workout scheduled. Your ML assignment is due in 2 days — would you like me to block time for it?", 'planner', NOW() - INTERVAL '2 hours'),
  ('cm-003', '00000000-0000-0000-0000-000000000001', 'user', 'Yes, block 3 hours tomorrow morning for the ML assignment', NULL, NOW() - INTERVAL '2 hours'),
  ('cm-004', '00000000-0000-0000-0000-000000000001', 'assistant', "Done! I've scheduled 9 AM - 12 PM tomorrow for your ML assignment. You currently have a 7-day meditation streak going — great consistency. And your sleep score has been averaging 78 this week, slightly below your target of 85.", 'planner', NOW() - INTERVAL '2 hours'),
  ('cm-005', '00000000-0000-0000-0000-000000000001', 'assistant', 'By the way, I noticed a new SWE Intern opportunity at Google that matches your profile at 85%. Want me to prepare a draft application?', 'opportunity', NOW() - INTERVAL '2 hours');

-- Daily briefing
INSERT INTO daily_briefings (id, user_id, date, briefing_data, created_at)
VALUES (
  'db-001',
  '00000000-0000-0000-0000-000000000001',
  CURRENT_DATE,
  jsonb_build_object(
    'summary', 'Productive day ahead with 6 planned tasks',
    'top_priority', 'Fix login bug',
    'tasks_count', 6,
    'completed_yesterday', 3,
    'streak', 'Meditation 7 days',
    'sleep_score', 78,
    'opportunities', jsonb_build_array(
      jsonb_build_object('title', 'Google SWE Intern', 'match', 85)
    )
  ),
  NOW()
);

-- Edge case: task with very long title (boundary test)
INSERT INTO tasks (id, user_id, title, description, priority, status, category, due_date, estimated_minutes, created_at, updated_at) VALUES
  ('t-016', '00000000-0000-0000-0000-000000000001',
   RPAD('Boundary test title', 200, 'x'),
   NULL, 'low', 'pending', 'test', NULL, NULL, NOW(), NOW());

-- Edge case: task with no due date (null boundary)
INSERT INTO tasks (id, user_id, title, description, priority, status, category, created_at, updated_at) VALUES
  ('t-017', '00000000-0000-0000-0000-000000000001',
   'Open-ended task with no deadline',
   'This task has no due date, no estimated time, and no category',
   'medium', 'pending', NULL, NOW(), NOW());

-- Edge case: sleep log with zero debt
INSERT INTO sleep_logs (id, user_id, bedtime, wake_time, quality_rating, duration_hours, sleep_score, sleep_debt, created_at, updated_at)
VALUES (
  'sl-edge-01', '00000000-0000-0000-0000-000000000001',
  (CURRENT_DATE - INTERVAL '1 day') + TIME '22:00',
  CURRENT_DATE + TIME '06:00',
  5, 8.0, 95, 0.0, NOW(), NOW()
);

-- Edge case: habit with perfect streak
INSERT INTO habits (id, user_id, name, frequency, time_target_minutes, is_active, current_streak, best_streak, consistency_percentage, created_at, updated_at) VALUES
  ('h-edge-01', '00000000-0000-0000-0000-000000000001',
   'Perfect Streak Habit', 'daily', 5, true, 100, 100, 100.0, NOW() - INTERVAL '100 days', NOW());

COMMIT;
