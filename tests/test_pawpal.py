import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Verify that calling mark_complete() changes the task's status to True."""
    task = Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        pet_name="Bolt",
    )
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Gigi", species="cat")
    assert len(pet.tasks) == 0

    pet.add_task(Task(
        title="Feeding",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        pet_name="",
    ))
    assert len(pet.tasks) == 1

    pet.add_task(Task(
        title="Grooming",
        duration_minutes=15,
        priority="medium",
        frequency="weekly",
        pet_name="",
    ))
    assert len(pet.tasks) == 2


# --- Helper to build a scheduler with sample data ---

def _make_scheduler(available_minutes=90):
    """Create a Scheduler with two pets and several tasks for testing."""
    owner = Owner(name="Tester", available_minutes=available_minutes, pets=[])
    dog = Pet(name="Bolt", species="dog")
    cat = Pet(name="Gigi", species="cat")

    dog.add_task(Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name=""))
    dog.add_task(Task(title="Brush fur", duration_minutes=15, priority="low", frequency="weekly", pet_name=""))
    cat.add_task(Task(title="Feeding", duration_minutes=10, priority="high", frequency="daily", pet_name=""))
    cat.add_task(Task(title="Play", duration_minutes=20, priority="medium", frequency="once", pet_name=""))

    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner)


# --- sort_by_duration tests ---

def test_sort_by_duration_ascending():
    """Shortest tasks should appear first when ascending."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    result = scheduler.sort_by_duration(tasks, ascending=True)
    durations = [t.duration_minutes for t in result]
    assert durations == sorted(durations)


def test_sort_by_duration_descending():
    """Longest tasks should appear first when descending."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    result = scheduler.sort_by_duration(tasks, ascending=False)
    durations = [t.duration_minutes for t in result]
    assert durations == sorted(durations, reverse=True)


# --- filter_by_pet tests ---

def test_filter_by_pet_returns_correct_tasks():
    """Only tasks for the specified pet should be returned."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    bolt_tasks = scheduler.filter_by_pet(tasks, "Bolt")
    assert len(bolt_tasks) == 2
    assert all(t.pet_name == "Bolt" for t in bolt_tasks)


def test_filter_by_pet_unknown_returns_empty():
    """Filtering by a pet name that doesn't exist returns an empty list."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    assert scheduler.filter_by_pet(tasks, "Unknown") == []


# --- filter_by_status tests ---

def test_filter_by_status_incomplete():
    """All tasks start incomplete, so filtering for incomplete returns all."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    incomplete = scheduler.filter_by_status(tasks, completed=False)
    assert len(incomplete) == 4


def test_filter_by_status_completed():
    """After completing one task, filtering for completed returns just that one."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()
    tasks[0].mark_complete()
    completed = scheduler.filter_by_status(tasks, completed=True)
    assert len(completed) == 1
    assert completed[0].title == "Walk"


# --- recurring task tests ---

def test_get_recurring_tasks():
    """Should return only daily/weekly tasks, not 'once' tasks."""
    scheduler = _make_scheduler()
    recurring = scheduler.get_recurring_tasks()
    assert len(recurring) == 3  # Walk (daily), Brush fur (weekly), Feeding (daily)
    assert all(t.frequency != "once" for t in recurring)


def test_reset_recurring_tasks():
    """Completed recurring tasks should be reset; one-time tasks stay completed."""
    scheduler = _make_scheduler()
    tasks = scheduler.gather_tasks()

    # Complete all tasks
    for t in tasks:
        t.mark_complete()

    reset_count = scheduler.reset_recurring_tasks()
    assert reset_count == 3  # 3 recurring tasks reset

    # The one-time task ("Play") should still be completed
    play_task = [t for t in tasks if t.title == "Play"][0]
    assert play_task.is_completed is True

    # Recurring tasks should be incomplete again
    walk_task = [t for t in tasks if t.title == "Walk"][0]
    assert walk_task.is_completed is False


# --- conflict detection tests ---

def test_detect_conflicts_no_conflicts():
    """A normal setup should have no conflicts."""
    scheduler = _make_scheduler()
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_duplicate_task():
    """Adding the same task title twice to a pet should flag a duplicate."""
    scheduler = _make_scheduler()
    # Add a duplicate "Walk" to Bolt
    bolt = scheduler.owner.pets[0]
    bolt.add_task(Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name=""))
    conflicts = scheduler.detect_conflicts()
    assert any("Duplicate" in c for c in conflicts)


def test_detect_conflicts_time_overload():
    """If one pet's tasks exceed available minutes, flag an overload."""
    scheduler = _make_scheduler(available_minutes=20)
    conflicts = scheduler.detect_conflicts()
    # Bolt has 30+15=45 min of tasks but only 20 min available
    assert any("Overload" in c and "Bolt" in c for c in conflicts)
