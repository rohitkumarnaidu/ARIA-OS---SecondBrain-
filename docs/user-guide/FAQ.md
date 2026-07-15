# Frequently Asked Questions (User FAQ)

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-FAQ-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-11 |

---

## General

**Q: What is ARIA OS?**
A: ARIA OS (Adaptive Reasoning Intelligent Assistant) is a personal productivity system built for BTech CSE students. It combines task management, habit tracking, sleep logging, goal planning, project management, and an AI assistant into a single dashboard.

**Q: Is my data private?**
A: Yes. By default, all AI processing runs locally on your machine using Ollama. No data leaves your computer. If cloud fallback is enabled (optional), your queries go to Anthropic's API but are never used for training.

**Q: Can I use it offline?**
A: Some features work offline if you're using local AI (Ollama). Data sync requires internet connection. The app will still load and show cached data, but new data won't save until you're back online.

**Q: Is it free?**
A: Yes. ARIA OS uses free tiers for hosting (Vercel, Railway, Supabase) and free local AI (Ollama). Cloud AI fallback (Claude) would cost roughly $1.50/month if enabled.

---

## Tasks

**Q: How do I set recurring tasks?**
A: When creating or editing a task, enable the **Recurring** option and choose a frequency (Daily, Weekly, Monthly). The task will automatically recreate itself after completion.

**Q: What happens to completed tasks?**
A: Completed tasks stay in your task list with a "completed" status. You can filter to view them. They are automatically archived after 30 days but remain in your history.

**Q: Can I delete a task instead of completing it?**
A: Yes. Open the task details and click **Delete**. This permanently removes the task.

**Q: What does "Missed" status mean?**
A: A task gets marked as **Missed** if it was overdue and never completed. You can still reopen and complete it later.

---

## Habits

**Q: Can I edit past habit logs?**
A: Yes. You can log or edit habit completions for the current week. Older entries are locked to prevent retroactive changes.

**Q: What breaks a streak?**
A: Missing a day (for daily habits) or a cycle (for weekly habits) resets your streak to 0. Weekends and holidays are not excluded -- consistency is tracked on all days.

**Q: Can I pause a habit?**
A: Yes. Go to the habit settings and toggle **Active** off. The habit is paused and won't appear in your daily check-in. Your streaks are preserved but frozen.

**Q: What if I complete a habit but forget to log it?**
A: Log it as soon as you remember. The habit history is editable for the current week.

---

## Sleep

**Q: Can I edit past sleep logs?**
A: Yes. Open any sleep entry and click **Edit** to change bedtime, wake time, or quality rating. The sleep score and debt are recalculated automatically.

**Q: How is sleep score calculated?**
A: Sleep score = min(100, duration_hours * 12.5 + quality_rating * 20). So 8 hours with a quality rating of 5 gives you a perfect score (100). Less sleep or lower quality reduces the score.

**Q: What is sleep debt?**
A: Sleep debt = max(0, 8 - duration_hours). It's the hours you're short of the recommended 8 hours. Consistent sleep debt can affect your focus and productivity.

**Q: When does the wind-down feature become available?**
A: The wind-down routine is available after 6 PM. Before that, you'll see a message saying to check back later.

---

## AI

**Q: Is the AI always listening?**
A: No. ARIA only processes your input when you send a message in the chat or when a scheduled agent runs (briefing at 7 AM, review at 8 PM Sunday, etc.). It does not have continuous microphone access.

**Q: Can I reset the AI's memory?**
A: Yes. Go to **Settings > Memory** and click **Reset Memory**. This clears all stored preferences and patterns. ARIA will start learning fresh.

**Q: What happens if the AI is unavailable?**
A: ARIA has a graceful fallback system. If the AI model is down, it uses keyword-based responses so you always get a helpful reply. No feature breaks entirely if the AI is unavailable.

**Q: Which AI model does ARIA use?**
A: By default, ARIA uses Ollama with Mistral 7B (free, local). If that's unavailable, it can fall back to Claude (cloud, costs ~$0.003 per request).

---

## Account

**Q: How do I delete my account?**
A: Go to **Settings > Account** and click **Delete Account**. This permanently removes all your data (tasks, habits, sleep logs, chat history, etc.). This action cannot be undone.

**Q: Can I export my data?**
A: Yes. Go to **Settings > Data Export** and click **Export**. You'll receive a downloadable archive of all your data in JSON format, suitable for GDPR compliance.

**Q: How do I change my password?**
A: Use the Supabase auth flow. Go to **Settings > Account** and click **Change Password**. You'll receive a password reset email.

---

## Troubleshooting

**Q: Why isn't the AI responding?**
A: Check if Ollama is running (if using local AI). Try restarting the service. If the issue persists, the system will fall back to keyword responses automatically.

**Q: Why is my data not saving?**
A: Check your internet connection. If you're offline, data won't save to the server. Also check that you're logged in -- your session may have expired. Refresh the page and try again.

**Q: The page is loading slowly. What do I do?**
A: Try refreshing the page. If it persists, check your internet speed. The app stores some data locally, so it should improve after the initial load.

**Q: I'm seeing a 429 error. What does it mean?**
A: You've been rate-limited. The chat endpoint allows 30 requests per minute. Wait a minute and try again.

---

## Browsers

**Q: Which browsers are supported?**
A: ARIA OS supports the latest versions of:

| Browser | Status |
|---|---|
| Google Chrome | Fully supported |
| Mozilla Firefox | Fully supported |
| Microsoft Edge | Fully supported |
| Safari | Supported (minor styling differences) |
| Brave | Supported |

> Mobile browsers work but are not optimized for all features. Use a desktop browser for the best experience.
