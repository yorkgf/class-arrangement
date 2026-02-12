"""
Test to trace the specific constraint causing infeasibility.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ortools.sat.python import cp_model
import src.data as data


def test_without_art_pe_special():
    """Test without special Art/PE constraints."""
    print("Testing WITHOUT special Art/PE teacher constraints...")

    model = cp_model.CpModel()
    classes = data.get_class_groups()
    excluded = data.get_excluded_time_slots()
    required = data.get_required_time_slots()
    joint_sessions = data.get_joint_sessions()
    time_slots = data.get_time_slots()

    # Build teacher to classes map
    teacher_classes = {}
    for class_name, class_group in classes.items():
        for course_name, course in class_group.courses.items():
            teacher = course.teacher
            if teacher not in teacher_classes:
                teacher_classes[teacher] = set()
            teacher_classes[teacher].add((class_name, course_name))

    # Build class to joint sessions map
    class_to_joint_sessions = {}
    for session in joint_sessions:
        for class_name in session.classes:
            if class_name not in class_to_joint_sessions:
                class_to_joint_sessions[class_name] = []
            class_to_joint_sessions[class_name].append(session)

    # Create variables
    schedule_vars = {}
    for class_name, class_group in classes.items():
        for course_name, course in class_group.courses.items():
            for day, period in time_slots:
                if (day, period) in excluded.get(class_name, set()):
                    continue
                req = required.get(class_name, {})
                if (day, period) in req:
                    if req[(day, period)] != course_name:
                        continue
                var_name = f"schedule_{class_name}_{course_name}_{day}_{period}"
                schedule_vars[(class_name, course_name, day, period)] = model.NewBoolVar(var_name)

    # Basic constraints
    for class_name, class_group in classes.items():
        for course_name, course in class_group.courses.items():
            periods = []
            for day, period in time_slots:
                if (day, period) in excluded.get(class_name, set()):
                    continue
                req = required.get(class_name, {})
                if (day, period) in req:
                    if req[(day, period)] != course_name:
                        continue
                key = (class_name, course_name, day, period)
                if key in schedule_vars:
                    periods.append(schedule_vars[key])

            if periods:
                model.Add(sum(periods) == course.periods_per_week)

    # Joint session constraints
    for session in joint_sessions:
        if "10-EAL" in str(session.classes):
            continue

        course_name = session.course_name
        for day, period in time_slots:
            slot_vars = []
            valid_slot = True

            for class_name in session.classes:
                if (day, period) in excluded.get(class_name, set()):
                    valid_slot = False
                    break

                key = (class_name, course_name, day, period)
                if key in schedule_vars:
                    slot_vars.append(schedule_vars[key])
                else:
                    valid_slot = False
                    break

            if valid_slot and len(slot_vars) == len(session.classes):
                for i in range(len(slot_vars) - 1):
                    model.Add(slot_vars[i] == slot_vars[i + 1])

    # Required slot constraints
    for class_name, slot_courses in required.items():
        for (day, period), course_name in slot_courses.items():
            key = (class_name, course_name, day, period)
            if key in schedule_vars:
                model.Add(schedule_vars[key] == 1)

    # Teacher conflict constraints (GENERAL, not special Art/PE)
    for teacher, class_courses in teacher_classes.items():
        # Skip special teachers for now
        if teacher in ["Shiwen", "Wen"]:
            continue

        for day, period in time_slots:
            teacher_courses = []

            for class_name, course_name in class_courses:
                if (day, period) in excluded.get(class_name, set()):
                    continue

                # Check if this is a joint session
                session = None
                if class_name in class_to_joint_sessions:
                    for s in class_to_joint_sessions[class_name]:
                        if s.course_name == course_name:
                            session = s
                            break

                if session:
                    if session.classes[0] == class_name:
                        key = (class_name, course_name, day, period)
                        if key in schedule_vars:
                            teacher_courses.append(schedule_vars[key])
                else:
                    key = (class_name, course_name, day, period)
                    if key in schedule_vars:
                        teacher_courses.append(schedule_vars[key])

            if len(teacher_courses) > 1:
                model.Add(sum(teacher_courses) <= 1)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("  [OK] Without Art/PE special: FEASIBLE")
        return True
    else:
        print(f"  [FAIL] Without Art/PE special: INFEASIBLE ({solver.StatusName(status)})")
        return False


def test_with_art_pe_only():
    """Test with ONLY Art/PE teacher constraints."""
    print("Testing with ONLY Art/PE teacher constraints...")

    model = cp_model.CpModel()
    classes = data.get_class_groups()
    excluded = data.get_excluded_time_slots()
    required = data.get_required_time_slots()
    time_slots = data.get_time_slots()

    # Create variables
    schedule_vars = {}
    for class_name, class_group in classes.items():
        for course_name, course in class_group.courses.items():
            for day, period in time_slots:
                if (day, period) in excluded.get(class_name, set()):
                    continue
                req = required.get(class_name, {})
                if (day, period) in req:
                    if req[(day, period)] != course_name:
                        continue
                var_name = f"schedule_{class_name}_{course_name}_{day}_{period}"
                schedule_vars[(class_name, course_name, day, period)] = model.NewBoolVar(var_name)

    # Basic constraints
    for class_name, class_group in classes.items():
        for course_name, course in class_group.courses.items():
            periods = []
            for day, period in time_slots:
                if (day, period) in excluded.get(class_name, set()):
                    continue
                req = required.get(class_name, {})
                if (day, period) in req:
                    if req[(day, period)] != course_name:
                        continue
                key = (class_name, course_name, day, period)
                if key in schedule_vars:
                    periods.append(schedule_vars[key])

            if periods:
                model.Add(sum(periods) == course.periods_per_week)

    # Required slot constraints
    for class_name, slot_courses in required.items():
        for (day, period), course_name in slot_courses.items():
            key = (class_name, course_name, day, period)
            if key in schedule_vars:
                model.Add(schedule_vars[key] == 1)

    # Art teacher constraints (Shiwen)
    for day, period in time_slots:
        art_classes = []
        for class_name, class_group in classes.items():
            for course_name, course in class_group.courses.items():
                if course.teacher == "Shiwen" and course_name == "Art":
                    if (day, period) in excluded.get(class_name, set()):
                        continue
                    key = (class_name, course_name, day, period)
                    if key in schedule_vars:
                        art_classes.append(schedule_vars[key])

        if len(art_classes) > 1:
            model.Add(sum(art_classes) <= 1)

    # PE teacher constraints (Wen) - SIMPLE VERSION (no joint handling)
    for day, period in time_slots:
        pe_classes = []
        for class_name, class_group in classes.items():
            for course_name, course in class_group.courses.items():
                if course.teacher == "Wen" and course_name == "PE":
                    if (day, period) in excluded.get(class_name, set()):
                        continue
                    key = (class_name, course_name, day, period)
                    if key in schedule_vars:
                        pe_classes.append(schedule_vars[key])

        if len(art_classes) > 1:
            model.Add(sum(art_classes) <= 1)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("  [OK] With Art/PE only: FEASIBLE")
        return True
    else:
        print(f"  [FAIL] With Art/PE only: INFEASIBLE ({solver.StatusName(status)})")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ART/PE CONSTRAINT TESTING")
    print("=" * 60)

    results = []
    results.append(test_without_art_pe_special())
    results.append(test_with_art_pe_only())

    print("\n" + "=" * 60)
    if all(results):
        print("All tests passed!")
    else:
        print("Some tests failed.")
    print("=" * 60)
