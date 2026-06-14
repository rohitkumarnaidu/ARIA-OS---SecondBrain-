# Database Schema

## Overview

21 tables in Supabase PostgreSQL database. All tables use `auth.uid() = user_id` as Row Level Security (RLS) policy. All tables have RLS enabled with the standard `users_own_data` policy.

---

## Entity-Relationship Diagram

```
users_profile (1) ──── (many) tasks
users_profile (1) ──── (many) courses
users_profile (1) ──── (many) youtube_saves
users_profile (1) ──── (many) resources
users_profile (1) ──── (many) ideas
users_profile (1) ──── (many) goals
users_profile (1) ──── (many) opportunities
users_profile (1) ──── (many) income_sources
users_profile (1) ──── (many) income_logs
users_profile (1) ──── (many) projects
users_profile (1) ──── (many) habits
users_profile (1) ──── (many) sleep_logs
users_profile (1) ──── (many) time_logs
users_profile (1) ──── (many) academic_subjects
users_profile (1) ──── (many) aria_memory
users_profile (1) ──── (many) daily_briefings
users_profile (1) ──── (many) weekly_reviews
users_profile (1) ──── (many) study_sessions
users_profile (1) ──── (many) daily_logs

tasks (1) ──── (many) subtasks
tasks (1) ──── (many) task_dependencies
tasks (1) ──── (many) time_logs
tasks (many) ──── (1) goals (goal_id FK)
tasks (many) ──── (1) projects (project_id FK)
courses (many) ──── (1) goals (related_goal_id FK)
goals (1) ──── (many) roadmaps (linked_roadmap_id)
roadmaps (1) ──── (many) roadmap_updates
income_sources (1) ──── (many) income_logs
income_sources (1) ──── (many) projects (related_income_source_id FK)
habits (1) ──── (1) goals (linked_goal_id FK)
academic_subjects (1) ──── (many) marks
```

---

## Tables

### 1. users_profile
User profile, preferences, and system configuration.

```sql
CREATE TABLE users_profile (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT,
  email TEXT,
  college TEXT,
  year INTEGER,
  branch TEXT,
  skills JSONB DEFAULT '[]', -- Array of {name, level} objects
  opportunity_preferences JSONB DEFAULT '{}', -- {types:[], min_match_score:60, location:null, excluded:[]}
  daily_routine JSONB DEFAULT '{}', -- {study_start_time, hours_available, study_days[]}
  github_username TEXT,
  linkedin_url TEXT,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  bedtime TIME,
  wake_time TIME,
  push_subscription JSONB, -- {endpoint, keys:{p256dh, auth}}
  google_calendar_token JSONB, -- {access_token, refresh_token, expiry_date}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**RLS Policy:**
```sql
ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_own_data" ON users_profile
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
```

---

### 2. tasks
Task management with smart features — auto-reschedule, missed tracking, recurrence.

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  category TEXT DEFAULT 'personal' CHECK (category IN ('study', 'project', 'habit', 'personal', 'income', 'career', 'health')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'missed')),
  estimated_minutes INTEGER,
  actual_minutes INTEGER,
  due_date TIMESTAMPTZ,
  scheduled_start TIMESTAMPTZ,
  source TEXT DEFAULT 'manual' CHECK (source IN ('manual', 'roadmap', 'aria', 'opportunity', 'recurring', 'course')),
  goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  completed_at TIMESTAMPTZ,
  rescheduled_from TIMESTAMPTZ,
  missed_count INTEGER DEFAULT 0,
  recurrence TEXT, -- 'daily', 'weekdays', 'weekly', 'monthly', or custom cron
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE status NOT IN ('completed', 'cancelled');
```

---

### 3. subtasks
Subtasks for breaking down complex tasks.

```sql
CREATE TABLE subtasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  is_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_subtasks_task ON subtasks(task_id);
```

---

### 4. task_dependencies
Task dependency relationships for sequenced execution.

```sql
CREATE TABLE task_dependencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
  depends_on_id UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
  UNIQUE(task_id, depends_on_id)
);
```

**Index:**
```sql
CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_depends ON task_dependencies(depends_on_id);
```

---

### 5. courses
Course tracking from multiple platforms with mandatory deadlines.

```sql
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  platform TEXT NOT NULL CHECK (platform IN ('udemy', 'coursera', 'nptel', 'youtube', 'college', 'other')),
  url TEXT,
  total_videos INTEGER,
  completed_videos INTEGER DEFAULT 0,
  progress_percent INTEGER DEFAULT 0,
  deadline TIMESTAMPTZ NOT NULL, -- Mandatory: no course without a completion date
  why_enrolled TEXT,
  status TEXT DEFAULT 'not_started' CHECK (status IN ('not_started', 'active', 'paused', 'completed', 'abandoned')),
  daily_minutes_needed FLOAT,
  daily_minutes_target INTEGER DEFAULT 30,
  related_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  abandonment_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_courses_user_status ON courses(user_id, status);
CREATE INDEX idx_courses_deadline ON courses(deadline) WHERE status = 'active';
```

---

### 6. youtube_saves (previously "videos")
YouTube knowledge vault with AI summaries and expiry logic.

```sql
CREATE TABLE youtube_saves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  url TEXT NOT NULL,
  title TEXT,
  channel TEXT,
  thumbnail_url TEXT,
  ai_summary TEXT,
  tags TEXT[] DEFAULT '{}',
  related_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'unseen' CHECK (status IN ('unseen', 'scheduled', 'watched', 'archived')),
  saved_at TIMESTAMPTZ DEFAULT NOW(),
  watched_at TIMESTAMPTZ,
  watch_by_date DATE -- saved_at + 60 days
);
```

**Index:**
```sql
CREATE INDEX idx_youtube_user_status ON youtube_saves(user_id, status);
CREATE INDEX idx_youtube_expiry ON youtube_saves(watch_by_date) WHERE status = 'unseen';
```

---

### 7. resources
Article, book, tool, and repo storage with auto-tagging.

```sql
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  resource_type TEXT CHECK (resource_type IN ('article', 'book', 'github', 'tool', 'paper', 'thread', 'other')),
  tags TEXT[] DEFAULT '{}',
  notes TEXT,
  ai_summary TEXT,
  related_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'unread' CHECK (status IN ('unread', 'reading', 'read', 'archived')),
  is_archived BOOLEAN DEFAULT FALSE,
  saved_at TIMESTAMPTZ DEFAULT NOW(),
  last_surfaced_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_resources_user_type ON resources(user_id, resource_type);
CREATE INDEX idx_resources_tags ON resources USING GIN(tags);
CREATE INDEX idx_resources_fts ON resources USING GIN(to_tsvector('english', title || ' ' || COALESCE(notes, '')));
```

---

### 8. ideas
Startup/business idea vault with AI market analysis.

```sql
CREATE TABLE ideas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  idea_type TEXT CHECK (idea_type IN ('startup', 'project', 'content', 'feature', 'other')),
  ai_analysis JSONB DEFAULT '{}', -- {competitors:[], market_size, feasibility, insight}
  status TEXT DEFAULT 'raw' CHECK (status IN ('raw', 'researching', 'validating', 'building', 'archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_ideas_user_status ON ideas(user_id, status);
```

---

### 9. goals
Goal and roadmap tracking with progress percentage.

```sql
CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  roadmap_type TEXT CHECK (roadmap_type IN ('career_skills', 'business_launch', 'exam_prep', 'study_learning', 'project', 'health', 'financial', 'custom')),
  target_date TIMESTAMPTZ,
  why_it_matters TEXT,
  hours_per_day FLOAT DEFAULT 2.0,
  days_per_week FLOAT DEFAULT 5.0,
  intensity TEXT DEFAULT 'medium' CHECK (intensity IN ('low', 'medium', 'high')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'abandoned')),
  progress_percent INTEGER DEFAULT 0,
  is_hard_deadline BOOLEAN DEFAULT FALSE,
  linked_roadmap_id UUID REFERENCES roadmaps(id) ON DELETE SET NULL,
  nodes JSONB DEFAULT '[]', -- Array of roadmap nodes (legacy, use roadmaps table)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_goals_user_status ON goals(user_id, status);
CREATE INDEX idx_goals_target_date ON goals(target_date) WHERE status = 'active';
```

---

### 10. roadmaps
Visual roadmap canvas data (React Flow nodes + edges).

```sql
CREATE TABLE roadmaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  roadmap_type TEXT CHECK (roadmap_type IN ('career_skills', 'business_launch', 'exam_prep', 'study_learning', 'project', 'health', 'financial', 'custom')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'archived')),
  nodes JSONB DEFAULT '[]', -- React Flow nodes array
  edges JSONB DEFAULT '[]', -- React Flow edges array
  hard_deadline DATE,
  hours_per_day FLOAT DEFAULT 2.0,
  days_per_week FLOAT DEFAULT 5.0,
  intensity TEXT DEFAULT 'normal' CHECK (intensity IN ('conservative', 'normal', 'aggressive')),
  last_ai_check_at TIMESTAMPTZ,
  update_frequency TEXT DEFAULT 'weekly' CHECK (update_frequency IN ('daily', 'weekly', 'monthly')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_roadmaps_user ON roadmaps(user_id);
```

---

### 11. roadmap_updates
AI-detected changes to roadmap nodes.

```sql
CREATE TABLE roadmap_updates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  node_label TEXT,
  update_type TEXT CHECK (update_type IN ('critical', 'suggested', 'informational')),
  old_value TEXT,
  new_value TEXT,
  reason TEXT,
  source_url TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'snoozed')),
  detected_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_roadmap_updates_roadmap ON roadmap_updates(roadmap_id);
```

---

### 12. opportunities
Scanned opportunities from Opportunity Radar.

```sql
CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  company TEXT,
  url TEXT NOT NULL,
  opportunity_type TEXT CHECK (opportunity_type IN ('internship', 'hackathon', 'open_source', 'fellowship', 'freelance', 'competition', 'scholarship', 'course')),
  description TEXT,
  skills_required TEXT[],
  deadline TIMESTAMPTZ,
  match_score INTEGER, -- 0-100
  match_reason TEXT,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'saved', 'applied', 'rejected', 'accepted')),
  found_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_opportunities_user_status ON opportunities(user_id, status);
CREATE INDEX idx_opportunities_deadline ON opportunities(deadline) WHERE status IN ('new', 'saved');
CREATE INDEX idx_opportunities_match ON opportunities(match_score) WHERE match_score >= 50;
```

---

### 13. income_sources
Income source definitions.

```sql
CREATE TABLE income_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('freelance', 'content', 'teaching', 'open_source', 'product', 'hackathon', 'internship', 'saas', 'other')),
  platform TEXT,
  monthly_amount DECIMAL DEFAULT 0,
  hours_per_week DECIMAL DEFAULT 0,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'ended')),
  started_at DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_income_sources_user ON income_sources(user_id);
```

---

### 14. income_logs
Individual income entries per source.

```sql
CREATE TABLE income_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  source_id UUID REFERENCES income_sources(id) ON DELETE CASCADE,
  amount DECIMAL NOT NULL,
  date DATE NOT NULL,
  description TEXT,
  hours_spent DECIMAL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_income_logs_user_date ON income_logs(user_id, date);
CREATE INDEX idx_income_logs_source ON income_logs(source_id);
```

---

### 15. projects
Project tracking with phases, blockers, and GitHub integration.

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  tech_stack TEXT[] DEFAULT '{}',
  phase TEXT DEFAULT 'planning' CHECK (phase IN ('planning', 'design', 'build', 'test', 'launch', 'maintain')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'archived')),
  github_url TEXT,
  live_url TEXT,
  next_action TEXT NOT NULL, -- Every project must have a next action
  blocker TEXT,
  related_income_source_id UUID REFERENCES income_sources(id) ON DELETE SET NULL,
  last_commit_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_projects_user_status ON projects(user_id, status);
```

---

### 16. academic_subjects
Academic subjects with marks and at-risk detection.

```sql
CREATE TABLE academic_subjects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  code TEXT,
  credits INTEGER,
  semester TEXT,
  exam_date TIMESTAMPTZ,
  marks_scored DECIMAL,
  max_marks DECIMAL DEFAULT 100,
  grade TEXT,
  at_risk_flag BOOLEAN DEFAULT FALSE,
  related_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_subjects_user_semester ON academic_subjects(user_id, semester);
CREATE INDEX idx_subjects_at_risk ON academic_subjects(at_risk_flag) WHERE at_risk_flag = TRUE;
```

---

### 17. marks
Academic marks per exam/assignment.

```sql
CREATE TABLE marks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID REFERENCES academic_subjects(id) ON DELETE CASCADE NOT NULL,
  exam_type TEXT CHECK (exam_type IN ('assignment', 'midterm', 'final', 'practical', 'quiz', 'other')),
  marks_obtained FLOAT NOT NULL,
  max_marks FLOAT NOT NULL,
  date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_marks_subject ON marks(subject_id);
```

---

### 18. habits
Habit tracking with streaks and goal linking.

```sql
CREATE TABLE habits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekdays', 'weekends', 'weekly', 'custom')),
  custom_days INTEGER[], -- For custom frequency (0=Sun, 1=Mon, ...)
  time_target_minutes INTEGER,
  current_streak INTEGER DEFAULT 0,
  best_streak INTEGER DEFAULT 0,
  consistency_percentage FLOAT DEFAULT 0,
  last_completed_at DATE,
  linked_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_habits_user_status ON habits(user_id, status);
```

---

### 19. habit_logs
Daily habit completion logs.

```sql
CREATE TABLE habit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  habit_id UUID REFERENCES habits(id) ON DELETE CASCADE NOT NULL,
  date DATE NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  minutes_spent INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(habit_id, date)
);
```

**Index:**
```sql
CREATE INDEX idx_habit_logs_habit_date ON habit_logs(habit_id, date);
```

---

### 20. sleep_logs
Sleep tracking with quality rating and sleep debt.

```sql
CREATE TABLE sleep_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  sleep_start TIMESTAMPTZ NOT NULL,
  sleep_end TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER,
  quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
  sleep_score INTEGER CHECK (sleep_score BETWEEN 0 AND 100),
  sleep_debt_minutes INTEGER DEFAULT 0,
  date DATE NOT NULL,
  source TEXT DEFAULT 'manual' CHECK (source IN ('manual', 'google_fit', 'fitbit')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

**Indexes:**
```sql
CREATE INDEX idx_sleep_logs_user_date ON sleep_logs(user_id, date DESC);
CREATE INDEX idx_sleep_logs_score ON sleep_logs(sleep_score) WHERE sleep_score < 50;
```

---

### 21. time_logs
Time tracking sessions per task.

```sql
CREATE TABLE time_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  description TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  duration_seconds INTEGER,
  is_pomodoro BOOLEAN DEFAULT FALSE,
  is_deep_work BOOLEAN DEFAULT FALSE, -- sessions > 90 min uninterrupted
  energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 5),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_time_logs_user_start ON time_logs(user_id, started_at DESC);
CREATE INDEX idx_time_logs_task ON time_logs(task_id);
CREATE INDEX idx_time_logs_deep ON time_logs(is_deep_work) WHERE is_deep_work = TRUE;
```

---

### 22. chat_messages
ARIA conversation history.

```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  action_taken TEXT, -- Description of action executed by ARIA
  metadata JSONB DEFAULT '{}', -- {context_used, model, tokens_used}
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_chat_messages_user_created ON chat_messages(user_id, created_at DESC);
```

---

### 23. aria_memory
ARIA's long-term memory about user.

```sql
CREATE TABLE aria_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  memory_type TEXT NOT NULL CHECK (memory_type IN ('preference', 'fact', 'pattern', 'decision')),
  content TEXT NOT NULL,
  confidence FLOAT DEFAULT 0.8 CHECK (confidence BETWEEN 0 AND 1),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_referenced_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_aria_memory_user_type ON aria_memory(user_id, memory_type);
CREATE INDEX idx_aria_memory_last_ref ON aria_memory(last_referenced_at);
```

---

### 24. daily_briefings
Morning intelligence briefings.

```sql
CREATE TABLE daily_briefings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  date DATE NOT NULL,
  briefing_content JSONB, -- {today_focus, opportunities, course_target, roadmap_check, aria_top_pick, what_to_skip}
  opportunities_shown INTEGER DEFAULT 0,
  aria_top_pick TEXT,
  was_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  was_emailed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

**Index:**
```sql
CREATE INDEX idx_briefings_user_date ON daily_briefings(user_id, date DESC);
```

---

### 25. weekly_reviews
Sunday weekly review reports.

```sql
CREATE TABLE weekly_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  week_start DATE NOT NULL,
  review_content TEXT,
  tasks_completed INTEGER DEFAULT 0,
  tasks_missed INTEGER DEFAULT 0,
  courses_studied_minutes INTEGER DEFAULT 0,
  income_logged DECIMAL DEFAULT 0,
  best_day TEXT,
  aria_pattern_insight TEXT,
  focus_for_next_week TEXT,
  was_emailed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, week_start)
);
```

**Index:**
```sql
CREATE INDEX idx_weekly_reviews_user ON weekly_reviews(user_id, week_start DESC);
```

---

### 26. study_sessions
Focused study sessions for course/subject learning with spaced repetition.

```sql
CREATE TABLE study_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
  subject TEXT,
  topic TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  duration_minutes INTEGER,
  notes TEXT,
  review_due_dates JSONB DEFAULT '[]', -- [now+1d, now+3d, now+7d, now+14d, now+30d]
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
```sql
CREATE INDEX idx_study_sessions_user ON study_sessions(user_id, started_at DESC);
```

---

### 27. daily_logs
Evening reflection logs.

```sql
CREATE TABLE daily_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  date DATE NOT NULL,
  entry TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

**Index:**
```sql
CREATE INDEX idx_daily_logs_user_date ON daily_logs(user_id, date DESC);
```

---

## Row Level Security (RLS)

Every table has RLS enabled with a standard user-scoped policy:

```sql
-- Generic template — apply to ALL tables
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_data" ON table_name
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**Tables requiring RLS (all 27):**
users_profile, tasks, subtasks, task_dependencies, courses, youtube_saves, resources, ideas, goals, roadmaps, roadmap_updates, opportunities, income_sources, income_logs, projects, academic_subjects, marks, habits, habit_logs, sleep_logs, time_logs, chat_messages, aria_memory, daily_briefings, weekly_reviews, study_sessions, daily_logs

**Exception tables (no user_id):**
- `subtasks` — inherits access through `task_id` (parent table RLS)
- `task_dependencies` — inherits through `task_id`
- `marks` — inherits through `subject_id`

---

## Indexes Summary

```sql
-- Tasks
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE status NOT IN ('completed', 'cancelled');

-- Courses
CREATE INDEX idx_courses_user_status ON courses(user_id, status);
CREATE INDEX idx_courses_deadline ON courses(deadline) WHERE status = 'active';

-- Resources
CREATE INDEX idx_resources_user_type ON resources(user_id, resource_type);
CREATE INDEX idx_resources_tags ON resources USING GIN(tags);
CREATE INDEX idx_resources_fts ON resources USING GIN(to_tsvector('english', title || ' ' || COALESCE(notes, '')));

-- Opportunities
CREATE INDEX idx_opportunities_user_status ON opportunities(user_id, status);
CREATE INDEX idx_opportunities_deadline ON opportunities(deadline) WHERE status IN ('new', 'saved');
CREATE INDEX idx_opportunities_match ON opportunities(match_score) WHERE match_score >= 50;

-- Time logs
CREATE INDEX idx_time_logs_user_start ON time_logs(user_id, started_at DESC);
CREATE INDEX idx_time_logs_deep ON time_logs(is_deep_work) WHERE is_deep_work = TRUE;

-- Sleep logs
CREATE INDEX idx_sleep_logs_user_date ON sleep_logs(user_id, date DESC);
CREATE INDEX idx_sleep_logs_score ON sleep_logs(sleep_score) WHERE sleep_score < 50;

-- Chat messages
CREATE INDEX idx_chat_messages_user_created ON chat_messages(user_id, created_at DESC);

-- Aria memory
CREATE INDEX idx_aria_memory_user_type ON aria_memory(user_id, memory_type);
CREATE INDEX idx_aria_memory_last_ref ON aria_memory(last_referenced_at);

-- Goals
CREATE INDEX idx_goals_user_status ON goals(user_id, status);
CREATE INDEX idx_goals_target_date ON goals(target_date) WHERE status = 'active';

-- Habits
CREATE INDEX idx_habits_user_status ON habits(user_id, status);

-- Income
CREATE INDEX idx_income_logs_user_date ON income_logs(user_id, date);

-- Academics
CREATE INDEX idx_subjects_at_risk ON academic_subjects(at_risk_flag) WHERE at_risk_flag = TRUE;
```

---

## Realtime Configuration

Enable realtime on tables that need live UI updates:

```sql
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE chat_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE opportunities;
ALTER PUBLICATION supabase_realtime ADD TABLE daily_briefings;
ALTER PUBLICATION supabase_realtime ADD TABLE goals;
ALTER PUBLICATION supabase_realtime ADD TABLE sleep_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE time_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE habits;
```

These tables require realtime because:
- **tasks**: Dashboard and task list update live when tasks change
- **chat_messages**: New messages appear in chat without refresh
- **opportunities**: New matches appear as they're found
- **daily_briefings**: Morning briefing appears automatically
- **goals**: Progress bars update live
- **sleep_logs**: Sleep score adjustment triggers immediately
- **time_logs**: Timer status updates live
- **habits**: Streak status reflects immediately

---

## pg_cron Setup

```sql
-- Enable pg_cron extension (run once during Phase 1)
CREATE EXTENSION IF NOT EXISTS pg_cron;
GRANT USAGE ON SCHEMA cron TO postgres;

-- Schedule Edge Functions (add each when building corresponding phase)
-- Daily Briefing (7 AM IST = 01:30 UTC)
SELECT cron.schedule('daily-briefing', '30 1 * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/daily-briefing',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Opportunity Radar (6 AM IST = 00:30 UTC)
SELECT cron.schedule('opp-radar', '30 0 * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/opp-radar',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Missed Task Checker (every 15 minutes)
SELECT cron.schedule('task-checker', '*/15 * * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/task-checker',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Roadmap Update (Sunday 9 AM IST = 03:30 UTC)
SELECT cron.schedule('roadmap-update', '30 3 * * 0',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/roadmap-update',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Weekly Review (Sunday 8 PM IST = 14:30 UTC)
SELECT cron.schedule('weekly-review', '30 14 * * 0',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/weekly-review',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Bedtime Reminder (9:30 PM IST = 16:00 UTC)
SELECT cron.schedule('bedtime-reminder', '0 16 * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/bedtime-reminder',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Habit Miss Checker (Midnight IST = 18:30 UTC)
SELECT cron.schedule('habit-miss-checker', '30 18 * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/habit-miss-checker',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);

-- Course Nudge (6 PM IST = 12:30 UTC)
SELECT cron.schedule('course-nudge', '30 12 * * *',
  $$SELECT net.http_post(
    'https://[project].supabase.co/functions/v1/course-nudge',
    '{}',
    '{"Authorization": "Bearer [service_role_key]"}'
  )$$);
```

---

## Foreign Key Relationships Summary

| Parent Table | Child Table | Foreign Key |
|-------------|-------------|-------------|
| auth.users | users_profile | user_id |
| auth.users | tasks | user_id |
| auth.users | courses | user_id |
| auth.users | youtube_saves | user_id |
| auth.users | resources | user_id |
| auth.users | ideas | user_id |
| auth.users | goals | user_id |
| auth.users | roadmaps | user_id |
| auth.users | opportunities | user_id |
| auth.users | income_sources | user_id |
| auth.users | income_logs | user_id |
| auth.users | projects | user_id |
| auth.users | academic_subjects | user_id |
| auth.users | habits | user_id |
| auth.users | sleep_logs | user_id |
| auth.users | time_logs | user_id |
| auth.users | chat_messages | user_id |
| auth.users | aria_memory | user_id |
| auth.users | daily_briefings | user_id |
| auth.users | weekly_reviews | user_id |
| auth.users | study_sessions | user_id |
| auth.users | daily_logs | user_id |
| tasks | subtasks | task_id ON DELETE CASCADE |
| tasks | task_dependencies | task_id ON DELETE CASCADE |
| tasks | time_logs | task_id ON DELETE SET NULL |
| goals | tasks | goal_id ON DELETE SET NULL |
| goals | courses | related_goal_id ON DELETE SET NULL |
| goals | habits | linked_goal_id ON DELETE SET NULL |
| goals | academic_subjects | related_goal_id ON DELETE SET NULL |
| goals | roadmaps | linked_roadmap_id ON DELETE SET NULL |
| roadmaps | roadmap_updates | roadmap_id ON DELETE CASCADE |
| income_sources | income_logs | source_id ON DELETE CASCADE |
| income_sources | projects | related_income_source_id ON DELETE SET NULL |
| academic_subjects | marks | subject_id ON DELETE CASCADE |
| courses | study_sessions | course_id ON DELETE SET NULL |
