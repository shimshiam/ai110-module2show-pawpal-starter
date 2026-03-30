import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler, ScheduleEntry, DailyPlan


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
    # Grab the original 4 tasks before any completions add new instances
    original_tasks = list(scheduler.gather_tasks())

    # Complete all original tasks (recurring ones will auto-spawn new instances)
    for t in original_tasks:
        t.mark_complete()

    # Reset should target the 3 completed *original* recurring tasks
    # (the auto-spawned copies are already incomplete, so they aren't reset)
    reset_count = scheduler.reset_recurring_tasks()
    assert reset_count == 3  # 3 recurring originals reset

    # The one-time task ("Play") should still be completed
    play_task = [t for t in original_tasks if t.title == "Play"][0]
    assert play_task.is_completed is True

    # Original recurring tasks should be incomplete again
    walk_task = [t for t in original_tasks if t.title == "Walk"][0]
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


# --- recurring auto-creation tests ---

def test_mark_complete_daily_creates_next_instance():
    """Completing a daily task should add a new incomplete copy to the same pet."""
    pet = Pet(name="Bolt", species="dog")
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name="")
    pet.add_task(task)

    assert len(pet.tasks) == 1
    next_task = task.mark_complete()
    assert len(pet.tasks) == 2

    # Original is completed
    assert task.is_completed is True
    # New instance is incomplete with identical attributes
    assert next_task is not None
    assert next_task.is_completed is False
    assert next_task.title == "Walk"
    assert next_task.duration_minutes == 30
    assert next_task.priority == "high"
    assert next_task.frequency == "daily"
    assert next_task.pet_name == "Bolt"


def test_mark_complete_weekly_creates_next_instance():
    """Completing a weekly task should also spawn a next occurrence."""
    pet = Pet(name="Gigi", species="cat")
    task = Task(title="Grooming", duration_minutes=15, priority="medium", frequency="weekly", pet_name="")
    pet.add_task(task)

    next_task = task.mark_complete()
    assert len(pet.tasks) == 2
    assert next_task is not None
    assert next_task.frequency == "weekly"
    assert next_task.is_completed is False


def test_mark_complete_once_does_not_create_instance():
    """Completing a one-time task should NOT create any new instance."""
    pet = Pet(name="Bolt", species="dog")
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once", pet_name="")
    pet.add_task(task)

    result = task.mark_complete()
    assert len(pet.tasks) == 1
    assert result is None


def test_mark_complete_without_pet_still_completes():
    """A task not attached to a pet should complete without error (no auto-creation)."""
    task = Task(title="Loose task", duration_minutes=10, priority="low", frequency="daily", pet_name="test")
    result = task.mark_complete()
    assert task.is_completed is True
    assert result is None


# --- time-conflict detection tests ---

def _make_plan_with_entries(entries, owner_name="Tester"):
    """Helper: build a DailyPlan from a list of ScheduleEntry objects."""
    return DailyPlan(
        owner_name=owner_name,
        entries=entries,
        total_minutes_used=sum(e.end_minute - e.start_minute for e in entries),
        total_minutes_available=120,
    )


def test_detect_time_conflicts_no_overlap():
    """Sequential entries should produce zero warnings."""
    scheduler = _make_scheduler()
    task_a = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name="Bolt")
    task_b = Task(title="Feed", duration_minutes=10, priority="high", frequency="daily", pet_name="Gigi")
    plan = _make_plan_with_entries([
        ScheduleEntry(task=task_a, start_minute=0, end_minute=30, reason="test"),
        ScheduleEntry(task=task_b, start_minute=30, end_minute=40, reason="test"),
    ])
    assert scheduler.detect_time_conflicts(plan) == []


def test_detect_time_conflicts_same_pet_overlap():
    """Two tasks for the same pet with overlapping windows should flag a same-pet warning."""
    scheduler = _make_scheduler()
    task_a = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name="Bolt")
    task_b = Task(title="Brush", duration_minutes=15, priority="low", frequency="weekly", pet_name="Bolt")
    plan = _make_plan_with_entries([
        ScheduleEntry(task=task_a, start_minute=0, end_minute=30, reason="test"),
        ScheduleEntry(task=task_b, start_minute=20, end_minute=35, reason="test"),
    ])
    warnings = scheduler.detect_time_conflicts(plan)
    assert len(warnings) == 1
    assert "Same-pet (Bolt)" in warnings[0]
    assert "share 10 min" in warnings[0]


def test_detect_time_conflicts_cross_pet_overlap():
    """Tasks for different pets with overlapping windows should flag a cross-pet warning."""
    scheduler = _make_scheduler()
    task_a = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", pet_name="Bolt")
    task_b = Task(title="Feed", duration_minutes=10, priority="high", frequency="daily", pet_name="Gigi")
    plan = _make_plan_with_entries([
        ScheduleEntry(task=task_a, start_minute=0, end_minute=30, reason="test"),
        ScheduleEntry(task=task_b, start_minute=25, end_minute=35, reason="test"),
    ])
    warnings = scheduler.detect_time_conflicts(plan)
    assert len(warnings) == 1
    assert "Cross-pet (Bolt & Gigi)" in warnings[0]
    assert "share 5 min" in warnings[0]


def test_detect_time_conflicts_multiple_overlaps():
    """Three mutually overlapping entries should produce three pairwise warnings."""
    scheduler = _make_scheduler()
    task_a = Task(title="Walk", duration_minutes=20, priority="high", frequency="daily", pet_name="Bolt")
    task_b = Task(title="Feed", duration_minutes=20, priority="high", frequency="daily", pet_name="Gigi")
    task_c = Task(title="Meds", duration_minutes=20, priority="high", frequency="daily", pet_name="Bolt")
    plan = _make_plan_with_entries([
        ScheduleEntry(task=task_a, start_minute=0,  end_minute=20, reason="test"),
        ScheduleEntry(task=task_b, start_minute=5,  end_minute=25, reason="test"),
        ScheduleEntry(task=task_c, start_minute=10, end_minute=30, reason="test"),
    ])
    warnings = scheduler.detect_time_conflicts(plan)
    assert len(warnings) == 3
