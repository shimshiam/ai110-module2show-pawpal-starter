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
