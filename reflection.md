# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial design uses five classes and one helper dataclass. Owner holds the users name, time budget, and a list of pets. Pet stores the pets name, species, and its care tasks. Task represents a single activity with a title, duration, priority, and frequency. Scheduler gathers tasks from all pets, sorts by priority, checks what fits in the available time, and builds the plan. DailyPlan holds the final schedule with ordered entries, dropped tasks, and reasoning. ScheduleEntry is a small wrapper that pairs a task with its start/end time and a reason for its placement.

Owner and Pet handle data entry, Scheduler owns the logic, and DailyPlan owns the output.

**b. Core user actions**

Add a pet and set up its care tasks, things like walks, feeding, or meds, each with a duration, priority, and how often it repeats.

Click "Generate schedule" to build a daily plan that fits tasks into the time you have, tackling the important stuff first.

See the final schedule with timing, reasoning for each task's placement, and a list of anything that got dropped.

**c. Design changes**

After reviewing the skeleton with AI, three changes were made:

1. Renamed `detect_conflicts` to `fit_to_budget` Renaming it makes the intent clearer and leaves room for a real conflict-detection method later if needed.

2. `Pet.add_task` now auto-sets `task.pet_name` Previously, callers had to pass `pet_name` manually when creating a Task, which was redundant and could cause errors. Having `add_task` handle it keeps the data consistent.

3. `dropped_tasks` changed from `list[dict]` to `list[ScheduleEntry]`
Reusing `ScheduleEntry` (with a reason string) keeps the output uniform and easier to display.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three things. How much time the owner has, how important each task is, and how long it takes. Important stuff like meds and feeding always goes first because you really cant skip those. If two tasks have the same priority, the quicker one wins so we can squeeze more in. Once the time runs out, everything left just gets dropped.

**b. Tradeoffs**

The scheduler just goes down the list from most important to least important and squeezes in whatever fits. It never goes back to rethink earlier choices, so it can miss better combos. It might slot in one big 30 minute task when two smaller 15 minute ones would have covered more ground.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
