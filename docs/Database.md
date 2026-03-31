# Database Schema

## Overview

21 tables in Supabase PostgreSQL database. All tables use `auth.uid() = user_id` as Row Level Security (RLS) policy.

## Tables

### 1. users
User profile and preferences

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  name TEXT,
  email TEXT,
  avatar_url TEXT,
  college TEXT,
  year INTEGER,
  skills TEXT[], -- Array of skill strings
  bio TEXT,
  daily_routine JSONB,
  opportunity_preferences JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. tasks
Task management with smart features

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
  category TEXT DEFAULT 'personal', -- study, project, habit, personal, income
  status TEXT DEFAULT 'pending', -- pending, in_progress, completed, cancelled
  estimated_minutes INTEGER,
  due_date TIMESTAMPTZ,
  goal_id UUID,
  project_id UUID,
  completed_at TIMESTAMPTZ,
  rescheduled_from UUID,
  missed_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. subtasks
Subtasks for breaking down complex tasks

```sql
CREATE TABLE subtasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  is_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. task_dependencies
Task dependency relationships

```sql
CREATE TABLE task_dependencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  depends_on_id UUID REFERENCES tasks(id) ON DELETE CASCADE
);
```

### 5. courses
Course tracking from multiple platforms

```sql
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  platform TEXT NOT NULL, -- udemy, coursera, nptel, youtube, college, other
  url TEXT,
  total_videos INTEGER,
  completed_videos INTEGER DEFAULT 0,
  deadline TIMESTAMPTZ,
  why_enrolled TEXT,
  status TEXT DEFAULT 'not_started', -- not_started, in_progress, completed, abandoned
  daily_minutes_needed FLOAT,
  abandonment_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. videos
YouTube video storage

```sql
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  url TEXT NOT NULL,
  title TEXT,
  thumbnail_url TEXT,
  ai_summary TEXT,
  goal_ids UUID[],
  status TEXT DEFAULT 'pending', -- pending, watched, archived
  saved_at TIMESTAMPTZ DEFAULT NOW(),
  watched_at TIMESTAMPTZ,
  expiry_date TIMESTAMPTZ
);
```

### 7. resources
Article, book, tool, and repo storage

```sql
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  resource_type TEXT, -- article, book, github, tool, paper, thread, other
  tags TEXT[],
  notes TEXT,
  ai_summary TEXT,
  is_archived BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 8. ideas
Startup/business idea vault

```sql
CREATE TABLE ideas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'raw', -- raw, researching, validating, building, archived
  market_research TEXT,
  competitors TEXT,
  feasibility_notes TEXT,
  validation_plan TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 9. goals
Goal and roadmap tracking

```sql
CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  description TEXT,
  roadmap_type TEXT, -- career_skills, business_launch, exam_prep, study_learning, project, health, financial, custom
  target_date TIMESTAMPTZ,
  hours_per_day FLOAT DEFAULT 2.0,
  days_per_week FLOAT DEFAULT 5.0,
  intensity TEXT DEFAULT 'medium', -- low, medium, high
  status TEXT DEFAULT 'active', -- active, completed, paused, abandoned
  progress INTEGER DEFAULT 0,
  is_hard_deadline BOOLEAN DEFAULT FALSE,
  nodes JSONB, -- Array of roadmap nodes
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 10. opportunities
Internships, hackathons, fellowships

```sql
CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  company TEXT,
  url TEXT NOT NULL,
  opportunity_type TEXT, -- internship, hackathon, open_source, fellowship, freelance, competition
  description TEXT,
  skills_required TEXT[],
  deadline TIMESTAMPTZ,
  skill_match FLOAT,
  status TEXT DEFAULT 'new', -- new, saved, applied, rejected, accepted
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 11. income_entries
Income tracking per entry

```sql
CREATE TABLE income_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  source_type TEXT NOT NULL,
  amount FLOAT NOT NULL,
  platform TEXT,
  description TEXT,
  date DATE NOT NULL,
  hours_spent FLOAT,
  effective_hourly_rate FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 12. projects
Project tracking with phases

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT NOT NULL,
  description TEXT,
  phase TEXT DEFAULT 'planning', -- planning, design, build, test, launch, maintain
  github_url TEXT,
  live_url TEXT,
  income_source_id UUID,
  next_action TEXT,
  blocker TEXT,
  last_commit_date TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 13. subjects
Academic subjects

```sql
CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  code TEXT,
  credits INTEGER,
  semester TEXT,
  exam_date TIMESTAMPTZ,
  target_marks FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 14. marks
Academic marks logging

```sql
CREATE TABLE marks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
  exam_type TEXT, -- assignment, midterm, final, practical
  marks_obtained FLOAT,
  max_marks FLOAT,
  date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 15. habits
Habit tracking

```sql
CREATE TABLE habits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  frequency TEXT NOT NULL, -- daily, weekdays, custom
  custom_days INTEGER[], -- For custom frequency
  time_target_minutes INTEGER,
  goal_id UUID,
  is_active BOOLEAN DEFAULT TRUE,
  current_streak INTEGER DEFAULT 0,
  best_streak INTEGER DEFAULT 0,
  consistency_percentage FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 16. habit_logs
Daily habit completion logs

```sql
CREATE TABLE habit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  habit_id UUID REFERENCES habits(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 17. sleep_logs
Sleep tracking

```sql
CREATE TABLE sleep_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  bedtime TIMESTAMPTZ NOT NULL,
  wake_time TIMESTAMPTZ NOT NULL,
  quality_rating INTEGER, -- 1-5
  duration_hours FLOAT,
  sleep_score INTEGER, -- 0-100
  sleep_debt FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 18. time_entries
Time tracking sessions

```sql
CREATE TABLE time_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  task_id UUID,
  description TEXT,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ,
  duration_minutes INTEGER,
  is_deep_work BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 19. chat_messages
ARIA conversation history

```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  role TEXT NOT NULL, -- user, assistant
  content TEXT NOT NULL,
  action_taken TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 20. aria_memory
ARIA's long-term memory about user

```sql
CREATE TABLE aria_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  category TEXT NOT NULL, -- preferences, facts, patterns, decisions
  content TEXT NOT NULL,
  importance INTEGER DEFAULT 5, -- 1-10
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 21. daily_logs
Evening reflection logs

```sql
CREATE TABLE daily_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  date DATE NOT NULL,
  entry TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Row Level Security (RLS)

Every table has RLS enabled with this standard policy:

```sql
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see own data" ON table_name
  FOR ALL
  USING (auth.uid() = user_id);
```

---

## Indexes

```sql
-- Tasks indexes
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Goals indexes
CREATE INDEX idx_goals_user_status ON goals(user_id, status);

-- Time entries indexes
CREATE INDEX idx_time_entries_user_date ON time_entries(user_id, start_time);

-- Sleep logs indexes
CREATE INDEX idx_sleep_logs_user_date ON sleep_logs(user_id, created_at);
```

---

## Realtime

Enable realtime on tables that need live updates:

```sql
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE chat_messages;
```
