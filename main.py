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
