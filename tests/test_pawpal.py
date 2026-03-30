import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
