# PawPal+ Class Diagram

```mermaid
classDiagram
    direction TB

    class Owner {
        +String name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) void
        +total_task_count() int
    }

    class Pet {
        +String name
        +String species
        +list~Task~ tasks
        +add_task(task: Task) void
        +remove_task(title: String) void
        +get_tasks_by_priority(priority: String) list~Task~
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String frequency
        +String pet_name
        +bool is_completed
        -Pet _owner_pet
        +mark_complete() Optional~Task~
        +priority_value() int
        +is_recurring() bool
    }

    class Scheduler {
        +Owner owner
        +int available_minutes
        +gather_tasks() list~Task~
        +sort_by_priority(tasks) list~Task~
        +sort_by_duration(tasks, ascending) list~Task~
        +filter_by_pet(tasks, pet_name) list~Task~
        +filter_by_status(tasks, completed) list~Task~
        +fit_to_budget(tasks) tuple~list, list~
        +detect_conflicts() list~String~
        +detect_time_conflicts(plan) list~String~
        +get_recurring_tasks() list~Task~
        +reset_recurring_tasks() int
        +generate_plan() DailyPlan
    }

    class DailyPlan {
        +String owner_name
        +list~ScheduleEntry~ entries
        +list~ScheduleEntry~ dropped_tasks
        +int total_minutes_used
        +int total_minutes_available
        +display_schedule() str
        +summary() str
    }

    class ScheduleEntry {
        +Task task
        +int start_minute
        +int end_minute
        +String reason
    }

    Owner "1" --> "*" Pet : has
    Pet "1" --> "*" Task : contains
    Task "*" ..> "0..1" Pet : _owner_pet back-reference
    Scheduler --> Owner : reads
    Scheduler ..> Task : sorts / filters
    Scheduler --> DailyPlan : creates and inspects
    DailyPlan "1" --> "*" ScheduleEntry : contains
    ScheduleEntry --> Task : wraps
```
