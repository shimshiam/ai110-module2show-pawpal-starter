from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner with 90 minutes available
owner = Owner(name="Shiam", available_minutes=90, pets=[])

# Create two pets
dog = Pet(name="Bolt", species="dog")
cat = Pet(name="Gigi", species="cat")

# Add tasks with different durations and priorities
dog.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily", pet_name=""))
dog.add_task(Task(title="Brush fur", duration_minutes=15, priority="low", frequency="weekly", pet_name=""))
cat.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", pet_name=""))
cat.add_task(Task(title="Play with laser", duration_minutes=20, priority="medium", frequency="daily", pet_name=""))
dog.add_task(Task(title="Vet medication", duration_minutes=5, priority="high", frequency="daily", pet_name=""))
dog.add_task(Task(title="Training session", duration_minutes=20, priority="medium", frequency="daily", pet_name=""))
dog.add_task(Task(title="Nail trimming", duration_minutes=10, priority="low", frequency="weekly", pet_name=""))
cat.add_task(Task(title="Litter box cleaning", duration_minutes=5, priority="high", frequency="daily", pet_name=""))
cat.add_task(Task(title="Grooming", duration_minutes=15, priority="medium", frequency="weekly", pet_name=""))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Generate and print schedule
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

print("=" * 50)
print("  Today's Schedule")
print("=" * 50)
print()
print(plan.display_schedule())
print()
print("-" * 50)
print(plan.summary())
print("=" * 50)

# --- New features demo ---

# 1. Sort by duration (shortest first)
all_tasks = scheduler.gather_tasks()
by_duration = scheduler.sort_by_duration(all_tasks)
print("\nTasks sorted by duration (shortest first):")
for t in by_duration:
    print(f"  {t.title} ({t.pet_name}) — {t.duration_minutes} min")

# 2. Filter by pet
bolt_tasks = scheduler.filter_by_pet(all_tasks, "Bolt")
print(f"\nBolt's tasks ({len(bolt_tasks)}):")
for t in bolt_tasks:
    print(f"  {t.title} — {t.priority} priority")

# 3. Filter by status
incomplete = scheduler.filter_by_status(all_tasks, completed=False)
print(f"\nIncomplete tasks: {len(incomplete)}")

# 4. Recurring tasks
recurring = scheduler.get_recurring_tasks()
print(f"\nRecurring tasks ({len(recurring)}):")
for t in recurring:
    print(f"  {t.title} ({t.pet_name}) — {t.frequency}")

# 5. Conflict detection
conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\nConflicts detected:")
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("\nNo conflicts detected.")

# 6. Reset recurring tasks after completing some
dog.tasks[0].mark_complete()  # Complete "Morning walk"
cat.tasks[0].mark_complete()  # Complete "Feeding"
reset_count = scheduler.reset_recurring_tasks()
print(f"\nReset {reset_count} recurring task(s) for the next day.")
