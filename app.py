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

# --- Owner & Pet Setup ---
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
    # Create owner on first pet add, reuse after that
    if st.session_state.owner is None:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=available_minutes, pets=[]
        )
    else:
        st.session_state.owner.available_minutes = available_minutes

    # Create pet and add to owner
    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.current_pet = new_pet
    st.success(f"Added {pet_name} the {species}!")

# Show current pets
if st.session_state.owner and st.session_state.owner.pets:
    st.write(
        "**Pets:**",
        ", ".join(f"{p.name} ({p.species})" for p in st.session_state.owner.pets),
    )

st.divider()

# --- Task Entry ---
st.subheader("Add Tasks")

if not st.session_state.owner or not st.session_state.owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    # Pick which pet gets the task
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

# --- Schedule Generation ---
st.subheader("Generate Schedule")

# Sort & filter options
col_sort, col_filter_pet, col_filter_status = st.columns(3)
with col_sort:
    sort_mode = st.selectbox("Sort tasks by", ["Priority (default)", "Duration (shortest first)", "Duration (longest first)"])
with col_filter_pet:
    filter_pet = "All"
    if st.session_state.owner and st.session_state.owner.pets:
        pet_names = ["All"] + [p.name for p in st.session_state.owner.pets]
        filter_pet = st.selectbox("Filter by pet", pet_names)
with col_filter_status:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete only", "Completed only"])

if st.button("Generate schedule"):
    if not st.session_state.owner or not st.session_state.owner.pets:
        st.warning("Add at least one pet with tasks first.")
    elif st.session_state.owner.total_task_count() == 0:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # Conflict detection
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(f"Conflict: {warning}")

        # Recurring task info
        recurring = scheduler.get_recurring_tasks()
        if recurring:
            st.caption(f"{len(recurring)} recurring task(s) will repeat automatically.")

        plan = scheduler.generate_plan()

        # Apply filters to display
        display_entries = plan.entries

        if filter_pet != "All":
            display_entries = [e for e in display_entries if e.task.pet_name == filter_pet]

        if filter_status == "Incomplete only":
            display_entries = [e for e in display_entries if not e.task.is_completed]
        elif filter_status == "Completed only":
            display_entries = [e for e in display_entries if e.task.is_completed]

        # Apply sort to display
        if sort_mode == "Duration (shortest first)":
            display_entries = sorted(display_entries, key=lambda e: e.task.duration_minutes)
        elif sort_mode == "Duration (longest first)":
            display_entries = sorted(display_entries, key=lambda e: e.task.duration_minutes, reverse=True)

        st.write(f"### Schedule for {plan.owner_name}")
        if display_entries:
            st.table(
                [
                    {
                        "Time": f"{e.start_minute}–{e.end_minute} min",
                        "Task": e.task.title,
                        "Pet": e.task.pet_name,
                        "Priority": e.task.priority,
                        "Frequency": e.task.frequency,
                        "Reason": e.reason,
                    }
                    for e in display_entries
                ]
            )
        else:
            st.info("No tasks match the current filter.")

        if plan.dropped_tasks:
            st.write("### Dropped Tasks")
            st.table(
                [
                    {
                        "Task": e.task.title,
                        "Pet": e.task.pet_name,
                        "Reason": e.reason,
                    }
                    for e in plan.dropped_tasks
                ]
            )

        st.info(plan.summary())
