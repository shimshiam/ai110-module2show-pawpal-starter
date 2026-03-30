# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Priority-first greedy scheduling** — tasks are sorted high-to-low by priority, with ties broken by shortest duration, then packed into the available time budget using a greedy fit algorithm
- **Sorting by time** — sort any task list by duration (shortest or longest first) to quickly see what fits in a free window
- **Sorting by priority** — sort by importance with automatic tiebreaking on duration so more tasks can be squeezed in
- **Filter by pet** — isolate a single pet's tasks from the full list to focus on one animal at a time
- **Filter by completion status** — view only incomplete or only completed tasks; filters chain with pet and sort for combined queries
- **Daily recurrence** — completing a daily task automatically creates a fresh incomplete copy on the same pet for the next day
- **Weekly recurrence** — same auto-creation logic applies to weekly tasks; one-time tasks simply finish with no follow-up
- **Chained recurrence** — the auto-created copy is itself recurring, so completing it spawns yet another instance, day after day
- **Pre-schedule conflict warnings** — before generating a plan, detects duplicate task titles on the same pet and flags any pet whose total task time exceeds the owner's available minutes
- **Post-schedule time-overlap detection** — after generating a plan, scans all scheduled entries pairwise for overlapping time windows and labels each conflict as same-pet or cross-pet
- **Lightweight warning strategy** — all conflict checks return a list of human-readable warning strings instead of raising exceptions, so the app never crashes on bad data
- **Budget-aware task dropping** — tasks that don't fit the time budget are collected into a dropped list with a reason, so the owner knows exactly what was skipped and why

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Smarter Scheduling

Beyond the base priority-first planner, the Scheduler now supports:

- **Sort by duration** — view tasks shortest-first or longest-first to plan your time at a glance.
- **Filter by pet or status** — narrow the task list to a single pet or see only completed/incomplete tasks. Filters can be chained (e.g. "Bolt's incomplete tasks, shortest first").
- **Recurring task handling** — when a daily or weekly task is marked complete, a fresh copy is automatically created for the next occurrence. One-time tasks simply finish.
- **Conflict detection** — two layers of checks that return warnings instead of crashing:
  - *Pre-schedule*: flags duplicate task titles on the same pet and per-pet time overload.
  - *Post-schedule*: scans the generated plan for overlapping time slots and labels each conflict as same-pet or cross-pet.

All features are demonstrated in `main.py`, wired into the Streamlit UI in `app.py`, and covered by 36 passing tests.

### Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

The 36 tests cover five areas:

| Category | Tests | What they verify |
|---|---|---|
| Core behavior | 2 | Task completion, adding tasks to a pet |
| Sorting correctness | 6 | Duration sort (asc/desc), priority sort, empty lists, stable ordering for ties |
| Filtering | 4 | Filter by pet name, by completion status, unknown pet returns empty |
| Recurring task logic | 8 | Daily/weekly auto-creation on complete, chained recurrence, one-time tasks stay finished, reset behavior |
| Conflict detection | 7 | Same-pet overlap, cross-pet overlap, duplicate times, adjacent (touching) entries safe, multiple overlaps, warnings not exceptions |
| Scheduling edge cases | 9 | Zero budget drops all, exact budget fits all, no pets produces empty plan, overload and duplicate pre-checks |

**Confidence Level: 4/5 stars**

The test suite covers happy paths, edge cases (empty lists, zero budget, no pets), and boundary conditions (adjacent time slots, chained recurrence). It earns 4 out of 5 because the core scheduling logic, sorting, filtering, recurrence, and conflict detection are all thoroughly verified. The missing star is because the Streamlit UI layer (`app.py`) is not tested with automated integration tests, and the scheduler does not yet handle real-world clock times or multi-day planning.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
