import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant.
Enter your info, add pets and tasks, then generate a daily schedule.
"""
)

# --- Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "current_pet" not in st.session_state:
    st.session_state.current_pet = None

# ─────────────────────────────────────────────
#  Owner & Pet Setup
# ─────────────────────────────────────────────
st.subheader("Owner & Pet Info")

col_owner, col_pet = st.columns(2)
with col_owner:
    owner_name = st.text_input("Owner name", value="Shiam")
    available_minutes = st.number_input(
        "Available minutes today", min_value=1, max_value=480, value=90
    )
with col_pet:
    pet_name = st.text_input("Pet name", value="Bolt")
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=available_minutes, pets=[]
        )
    else:
        st.session_state.owner.available_minutes = available_minutes

    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.current_pet = new_pet
    st.success(f"Added {pet_name} the {species}!")

# Keep available_minutes in sync whenever the input changes
if st.session_state.owner is not None:
    st.session_state.owner.available_minutes = available_minutes

if st.session_state.owner and st.session_state.owner.pets:
    st.write("**Pets:**")
    for pet in st.session_state.owner.pets:
        col_pname, col_premove = st.columns([4, 1])
        with col_pname:
            st.write(f"{pet.name} ({pet.species})")
        with col_premove:
            if st.button("Remove", key=f"remove_pet_{pet.name}"):
                st.session_state.owner.remove_pet(pet.name)
                st.rerun()

st.divider()

# ─────────────────────────────────────────────
#  Task Entry
# ─────────────────────────────────────────────
st.subheader("Add Tasks")

if not st.session_state.owner or not st.session_state.owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_options = {p.name: p for p in st.session_state.owner.pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    frequency = st.selectbox("Frequency", ["daily", "once", "weekly"])

    if st.button("Add Task"):
        pet = pet_options[selected_pet_name]
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            pet_name="",
        )
        pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {pet.name}!")

    # Show tasks per pet
    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.write(f"**{pet.name}'s tasks:**")
            st.table(
                [
                    {
                        "Title": t.title,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Frequency": t.frequency,
                    }
                    for t in pet.tasks
                ]
            )

st.divider()

# ─────────────────────────────────────────────
#  Schedule Generation
# ─────────────────────────────────────────────
st.subheader("Generate Schedule")

# Sort & filter controls
col_sort, col_filter_pet, col_filter_status = st.columns(3)
with col_sort:
    sort_mode = st.selectbox(
        "Sort tasks by",
        ["Priority (default)", "Duration (shortest first)", "Duration (longest first)"],
    )
with col_filter_pet:
    filter_pet = "All"
    if st.session_state.owner and st.session_state.owner.pets:
        pet_names = ["All"] + [p.name for p in st.session_state.owner.pets]
        filter_pet = st.selectbox("Filter by pet", pet_names)
with col_filter_status:
    filter_status = st.selectbox(
        "Filter by status", ["All", "Incomplete only", "Completed only"]
    )

if st.button("Generate schedule"):
    if not st.session_state.owner or not st.session_state.owner.pets:
        st.warning("Add at least one pet with tasks first.")
    elif st.session_state.owner.total_task_count() == 0:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # ── Pre-schedule conflict checks ──
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.write("#### Pre-Schedule Warnings")
            for warning in conflicts:
                st.warning(warning)

        # ── Recurring task summary ──
        recurring = scheduler.get_recurring_tasks()
        if recurring:
            st.success(
                f"{len(recurring)} recurring task(s) detected — "
                "a new instance is created automatically when completed."
            )

        # ── Generate the plan ──
        plan = scheduler.generate_plan()

        # ── Post-schedule time-conflict checks ──
        time_conflicts = scheduler.detect_time_conflicts(plan)
        if time_conflicts:
            st.write("#### Time-Overlap Warnings")
            for warning in time_conflicts:
                st.warning(warning)

        # ── Apply filters using Scheduler methods ──
        all_tasks = [e.task for e in plan.entries]

        if filter_pet != "All":
            filtered_tasks = scheduler.filter_by_pet(all_tasks, filter_pet)
        else:
            filtered_tasks = all_tasks

        if filter_status == "Incomplete only":
            filtered_tasks = scheduler.filter_by_status(filtered_tasks, completed=False)
        elif filter_status == "Completed only":
            filtered_tasks = scheduler.filter_by_status(filtered_tasks, completed=True)

        # ── Apply sort using Scheduler methods ──
        if sort_mode == "Duration (shortest first)":
            filtered_tasks = scheduler.sort_by_duration(filtered_tasks, ascending=True)
        elif sort_mode == "Duration (longest first)":
            filtered_tasks = scheduler.sort_by_duration(filtered_tasks, ascending=False)
        else:
            filtered_tasks = scheduler.sort_by_priority(filtered_tasks)

        # Build a lookup from task -> entry for time display
        entry_map = {id(e.task): e for e in plan.entries}

        # ── Display scheduled tasks ──
        st.write(f"### Schedule for {plan.owner_name}")
        if filtered_tasks:
            st.table(
                [
                    {
                        "Time": (
                            f"{entry_map[id(t)].start_minute}–{entry_map[id(t)].end_minute} min"
                            if id(t) in entry_map
                            else "—"
                        ),
                        "Task": t.title,
                        "Pet": t.pet_name,
                        "Priority": t.priority.capitalize(),
                        "Duration": f"{t.duration_minutes} min",
                        "Frequency": t.frequency.capitalize(),
                        "Reason": entry_map[id(t)].reason if id(t) in entry_map else "",
                    }
                    for t in filtered_tasks
                ]
            )
        else:
            st.info("No tasks match the current filter.")

        # ── Dropped tasks ──
        if plan.dropped_tasks:
            st.write("### Dropped Tasks")
            for entry in plan.dropped_tasks:
                st.warning(
                    f"**{entry.task.title}** ({entry.task.pet_name}) — {entry.reason}"
                )

        # ── Summary metrics ──
        st.divider()
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Scheduled", f"{len(plan.entries)} task(s)")
        with col_m2:
            st.metric("Dropped", f"{len(plan.dropped_tasks)} task(s)")
        with col_m3:
            st.metric(
                "Time Used",
                f"{plan.total_minutes_used} / {plan.total_minutes_available} min",
            )

        if plan.total_minutes_used == plan.total_minutes_available:
            st.success("Time budget fully utilized!")
        elif plan.total_minutes_used < plan.total_minutes_available:
            remaining = plan.total_minutes_available - plan.total_minutes_used
            st.info(f"{remaining} minute(s) remaining — room for more tasks.")
