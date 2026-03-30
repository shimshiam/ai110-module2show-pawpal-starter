from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner with 90 minutes available
owner = Owner(name="Shiam", available_minutes=90, pets=[])

# Create two pets
dog = Pet(name="Bolt", species="dog")
cat = Pet(name="Gigi", species="cat")

# Add tasks OUT OF ORDER — mixed durations, priorities, and pets
cat.add_task(Task(title="Grooming", duration_minutes=15, priority="medium", frequency="weekly", pet_name=""))
dog.add_task(Task(title="Training session", duration_minutes=20, priority="medium", frequency="daily", pet_name=""))
cat.add_task(Task(title="Play with laser", duration_minutes=20, priority="medium", frequency="daily", pet_name=""))
dog.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily", pet_name=""))
cat.add_task(Task(title="Litter box cleaning", duration_minutes=5, priority="high", frequency="daily", pet_name=""))
dog.add_task(Task(title="Nail trimming", duration_minutes=10, priority="low", frequency="weekly", pet_name=""))
cat.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", pet_name=""))
dog.add_task(Task(title="Vet medication", duration_minutes=5, priority="high", frequency="daily", pet_name=""))
dog.add_task(Task(title="Brush fur", duration_minutes=15, priority="low", frequency="weekly", pet_name=""))

# Mark a few tasks as completed to test status filtering
cat.tasks[0].mark_complete()   # Grooming — completed
dog.tasks[0].mark_complete()   # Training session — completed

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Build scheduler
scheduler = Scheduler(owner)
all_tasks = scheduler.gather_tasks()

# ====================================================
#  1. Raw task order (as added — intentionally jumbled)
# ====================================================
print("=" * 55)
print("  RAW TASK ORDER (as added)")
print("=" * 55)
for t in all_tasks:
    status = "done" if t.is_completed else "todo"
    print(f"  {t.title:<22} {t.pet_name:<6} {t.duration_minutes:>3} min  {t.priority:<6}  [{status}]")

# ====================================================
#  2. Sorted by duration — shortest first
# ====================================================
print("\n" + "=" * 55)
print("  SORTED BY DURATION (shortest first)")
print("=" * 55)
by_duration_asc = scheduler.sort_by_duration(all_tasks, ascending=True)
for t in by_duration_asc:
    print(f"  {t.title:<22} {t.duration_minutes:>3} min")

# ====================================================
#  3. Sorted by duration — longest first
# ====================================================
print("\n" + "=" * 55)
print("  SORTED BY DURATION (longest first)")
print("=" * 55)
by_duration_desc = scheduler.sort_by_duration(all_tasks, ascending=False)
for t in by_duration_desc:
    print(f"  {t.title:<22} {t.duration_minutes:>3} min")

# ====================================================
#  4. Sorted by priority (default scheduler sort)
# ====================================================
print("\n" + "=" * 55)
print("  SORTED BY PRIORITY (high -> low, ties: shortest)")
print("=" * 55)
by_priority = scheduler.sort_by_priority(all_tasks)
for t in by_priority:
    print(f"  {t.title:<22} {t.priority:<6}  {t.duration_minutes:>3} min")

# ====================================================
#  5. Filter by pet
# ====================================================
print("\n" + "=" * 55)
print("  FILTER BY PET")
print("=" * 55)
for pet_name in ["Bolt", "Gigi"]:
    pet_tasks = scheduler.filter_by_pet(all_tasks, pet_name)
    print(f"\n  {pet_name}'s tasks ({len(pet_tasks)}):")
    for t in pet_tasks:
        print(f"    {t.title:<22} {t.priority:<6}  {t.duration_minutes:>3} min")

# ====================================================
#  6. Filter by completion status
# ====================================================
print("\n" + "=" * 55)
print("  FILTER BY STATUS")
print("=" * 55)
incomplete = scheduler.filter_by_status(all_tasks, completed=False)
completed = scheduler.filter_by_status(all_tasks, completed=True)
print(f"\n  Incomplete ({len(incomplete)}):")
for t in incomplete:
    print(f"    {t.title:<22} ({t.pet_name})")
print(f"\n  Completed ({len(completed)}):")
for t in completed:
    print(f"    {t.title:<22} ({t.pet_name})")

# ====================================================
#  7. Combined: Bolt's incomplete tasks, sorted shortest first
# ====================================================
print("\n" + "=" * 55)
print("  COMBINED: Bolt's incomplete tasks (shortest first)")
print("=" * 55)
bolt_incomplete = scheduler.filter_by_pet(
    scheduler.filter_by_status(all_tasks, completed=False), "Bolt"
)
bolt_incomplete_sorted = scheduler.sort_by_duration(bolt_incomplete, ascending=True)
for t in bolt_incomplete_sorted:
    print(f"  {t.title:<22} {t.duration_minutes:>3} min  {t.priority}")

# ====================================================
#  8. Generate the daily schedule
# ====================================================
print("\n" + "=" * 55)
print("  DAILY SCHEDULE")
print("=" * 55)
plan = scheduler.generate_plan()
print()
print(plan.display_schedule())
print()
print("-" * 55)
print(plan.summary())
print("=" * 55)

# ====================================================
#  9. Time-conflict detection on the generated plan
# ====================================================
print("\n" + "=" * 55)
print("  TIME-CONFLICT DETECTION")
print("=" * 55)

# A) Check the normal sequential plan — should be clean
time_conflicts = scheduler.detect_time_conflicts(plan)
print("\n  [A] Normal plan:")
if time_conflicts:
    for w in time_conflicts:
        print(f"      WARNING: {w}")
else:
    print("      No time conflicts — all tasks are sequential.")

# B) Build a realistic scenario: two tasks scheduled at the SAME time
#    Imagine the owner manually pencils in "Morning walk" and "Vet medication"
#    for Bolt at minute 0, plus "Feeding" for Gigi also at minute 0.
from pawpal_system import ScheduleEntry, DailyPlan

walk_task = Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily", pet_name="Bolt")
meds_task = Task(title="Vet medication", duration_minutes=5, priority="high", frequency="daily", pet_name="Bolt")
feed_task = Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", pet_name="Gigi")

conflict_plan = DailyPlan(
    owner_name="Shiam",
    entries=[
        ScheduleEntry(task=walk_task, start_minute=0, end_minute=30, reason="manual"),
        ScheduleEntry(task=meds_task, start_minute=0, end_minute=5,  reason="manual"),
        ScheduleEntry(task=feed_task, start_minute=0, end_minute=10, reason="manual"),
    ],
    total_minutes_used=45,
    total_minutes_available=90,
)

overlap_warnings = scheduler.detect_time_conflicts(conflict_plan)
print(f"\n  [B] Three tasks all starting at minute 0 — {len(overlap_warnings)} conflict(s):")
for w in overlap_warnings:
    print(f"      WARNING: {w}")

# ====================================================
# 10. Recurring auto-creation on mark_complete
# ====================================================
print("\n" + "=" * 55)
print("  RECURRING AUTO-CREATION")
print("=" * 55)

# Pick a daily task that is still incomplete
walk = next(t for t in dog.tasks if t.title == "Morning walk" and not t.is_completed)
print(f"\n  Before: Bolt has {len(dog.tasks)} tasks")
print(f"  Completing '{walk.title}' (frequency={walk.frequency})...")
next_walk = walk.mark_complete()
print(f"  After:  Bolt has {len(dog.tasks)} tasks")
print(f"  Original completed? {walk.is_completed}")
print(f"  New instance created? {next_walk is not None}")
if next_walk:
    print(f"  New task: '{next_walk.title}' — completed={next_walk.is_completed}, pet={next_walk.pet_name}")

# Add a one-time task to show the contrast — should NOT spawn a new instance
one_time = Task(title="Vet checkup", duration_minutes=45, priority="high", frequency="once", pet_name="")
cat.add_task(one_time)
print(f"\n  Before: Gigi has {len(cat.tasks)} tasks")
print(f"  Completing '{one_time.title}' (frequency={one_time.frequency})...")
result = one_time.mark_complete()
print(f"  After:  Gigi has {len(cat.tasks)} tasks  (unchanged — no new instance)")
print(f"  New instance created? {result is not None}")
print("=" * 55)
