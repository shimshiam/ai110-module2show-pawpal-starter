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

I used it for design brainstorming, asking things like "suggest small algorithms that would make a pet scheduler more efficient". During implementation I gave it specific build prompts like "implement a method that filters tasks by completion status or pet name" and it wrote the logic directly into my Scheduler class. 

The most helpful prompts were the ones that were specific about what I wanted. Asking it to explain tradeoffs before writing code also helped me understand what I was building instead of just copying answers.

**b. Judgment and verification**

When AI added the conflict detection demo in main.py, it originally built fake ScheduleEntry objects with hardcoded indexes like `dog.tasks[1]` and `dog.tasks[3]` to force overlapping times. I replaced it with a version that creates fresh Task objects with clear names like "Morning walk" and "Vet medication". That way the demo is readable and wont break if the task list changes.

To verify the code suggestions, I ran the tests after every change. I also ran main.py to visually confirm the output made sense.

---

## 4. Testing and Verification

**a. What you tested**

Filtering by pet name and by completion status. Recurring task logic to confirm that completing a daily or weekly task creates a new one, that chaining works and that one time tasks dont repeat. Conflict detection to verify overlaps, duplicate times, and that adjacent tasks touching at the same minute dont get falsely flagged.

These tests were important because the scheduler has a lot of dependent moving parts. Sorting feeds into the budget fit, which feeds into conflict detection. If any one piece is wrong then it all breaks, so testing each layer separately catches bugs efficiently.

**b. Confidence**

4 out of 5. The core logic, sorting, filtering, recurrence, and conflict detection are all covered with happy paths and edge cases. Streamlit UI doesn't have automated tests so I can only verify it manually.

---

## 5. Reflection

**a. What went well**

Having two layers where one checks the raw task list before scheduling and one that scans the actual plan for time overlaps, catches problems at different stages without ever crashing the app. I'm also happy with how the recurring task logic works. Completing a daily task and seeing a new one automatically appear on the same pet.

**b. What you would improve**

I'd add real clock times instead of just minute offsets.

**c. Key takeaway**

The biggest thing I learned is that being specific with AI prompts makes a huge difference. But I also learned that you cant just accept everything AI gives you. You have to run the tests, read the code, and make sure it actually fits your project.
