from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """A single pet care activity (walk, feed, groom, medication, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    frequency: str  # "once", "daily", or "weekly"
    pet_name: str

    def priority_value(self) -> int:
        """Return numeric weight: high=3, medium=2, low=1."""
        pass

    def is_recurring(self) -> bool:
        """Return True if frequency is not 'once'."""
        pass


@dataclass
class Pet:
    """Represents a single pet and its associated care tasks."""

    name: str
    species: str  # "dog", "cat", or "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and auto-set task.pet_name."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        pass

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return tasks filtered by priority level."""
        pass


@dataclass
class Owner:
    """Represents the pet owner and their scheduling constraints."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        pass

    def total_task_count(self) -> int:
        """Return the combined number of tasks across all pets."""
        pass


@dataclass
class ScheduleEntry:
    """A single entry in the daily plan, wrapping a Task with timing and reasoning."""

    task: Task
    start_minute: int
    end_minute: int
    reason: str


class Scheduler:
    """Core scheduling engine that produces a DailyPlan from an Owner's pets and tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.available_minutes = owner.available_minutes

    def gather_tasks(self) -> list[Task]:
        """Collect all tasks from all pets into one flat list, filtering by frequency."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort descending by priority, break ties by shorter duration first."""
        pass

    def fit_to_budget(self, tasks: list[Task]) -> tuple[list[Task], list[Task]]:
        """Split sorted tasks into fitting vs. dropped based on time budget."""
        pass

    def generate_plan(self) -> "DailyPlan":
        """Main method: gather -> sort -> detect conflicts -> build and return a DailyPlan."""
        pass


class DailyPlan:
    """The output schedule with ordered entries, dropped tasks, and explanations."""

    def __init__(
        self,
        owner_name: str,
        entries: Optional[list[ScheduleEntry]] = None,
        dropped_tasks: Optional[list[ScheduleEntry]] = None,
        total_minutes_used: int = 0,
        total_minutes_available: int = 0,
    ):
        self.owner_name = owner_name
        self.entries = entries or []
        self.dropped_tasks = dropped_tasks or []
        self.total_minutes_used = total_minutes_used
        self.total_minutes_available = total_minutes_available

    def display_schedule(self) -> str:
        """Return a formatted string of the schedule for Streamlit display."""
        pass

    def summary(self) -> str:
        """Return a text summary: tasks scheduled, dropped, time used vs. available."""
        pass
