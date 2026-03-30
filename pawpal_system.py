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
        return {"high": 3, "medium": 2, "low": 1}[self.priority]

    def is_recurring(self) -> bool:
        """Return True if frequency is not 'once'."""
        return self.frequency != "once"


@dataclass
class Pet:
    """Represents a single pet and its associated care tasks."""

    name: str
    species: str  # "dog", "cat", or "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and auto-set task.pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return tasks filtered by priority level."""
        return [t for t in self.tasks if t.priority == priority]


@dataclass
class Owner:
    """Represents the pet owner and their scheduling constraints."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def total_task_count(self) -> int:
        """Return the combined number of tasks across all pets."""
        return sum(len(pet.tasks) for pet in self.pets)


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
        """Collect all tasks from all pets into one flat list."""
        all_tasks = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                all_tasks.append(task)
        return all_tasks

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort descending by priority, break ties by shorter duration first."""
        return sorted(tasks, key=lambda t: (-t.priority_value(), t.duration_minutes))

    def fit_to_budget(self, tasks: list[Task]) -> tuple[list[Task], list[Task]]:
        """Split sorted tasks into fitting vs. dropped based on time budget."""
        fitting = []
        dropped = []
        time_used = 0
        for task in tasks:
            if time_used + task.duration_minutes <= self.available_minutes:
                fitting.append(task)
                time_used += task.duration_minutes
            else:
                dropped.append(task)
        return fitting, dropped

    def generate_plan(self) -> "DailyPlan":
        """Main method: gather -> sort -> fit to budget -> build and return a DailyPlan."""
        all_tasks = self.gather_tasks()
        sorted_tasks = self.sort_by_priority(all_tasks)
        fitting, dropped = self.fit_to_budget(sorted_tasks)

        entries = []
        cursor = 0
        for i, task in enumerate(fitting):
            if i == 0:
                reason = f"{task.priority.capitalize()} priority — scheduled first"
            else:
                reason = f"{task.priority.capitalize()} priority — next available slot"
            entry = ScheduleEntry(
                task=task,
                start_minute=cursor,
                end_minute=cursor + task.duration_minutes,
                reason=reason,
            )
            entries.append(entry)
            cursor += task.duration_minutes

        dropped_entries = []
        for task in dropped:
            dropped_entries.append(
                ScheduleEntry(
                    task=task,
                    start_minute=0,
                    end_minute=0,
                    reason="Not enough time remaining",
                )
            )

        return DailyPlan(
            owner_name=self.owner.name,
            entries=entries,
            dropped_tasks=dropped_entries,
            total_minutes_used=cursor,
            total_minutes_available=self.available_minutes,
        )


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
        lines = [f"Schedule for {self.owner_name}:\n"]
        for entry in self.entries:
            lines.append(
                f"  [{entry.start_minute}-{entry.end_minute} min] "
                f"{entry.task.title} ({entry.task.pet_name}) — {entry.reason}"
            )
        if self.dropped_tasks:
            lines.append("\nDropped tasks:")
            for entry in self.dropped_tasks:
                lines.append(f"  {entry.task.title} ({entry.task.pet_name}) — {entry.reason}")
        return "\n".join(lines)

    def summary(self) -> str:
        """Return a text summary: tasks scheduled, dropped, time used vs. available."""
        return (
            f"{len(self.entries)} task(s) scheduled, "
            f"{len(self.dropped_tasks)} dropped. "
            f"Time used: {self.total_minutes_used}/{self.total_minutes_available} minutes."
        )
