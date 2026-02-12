"""
Debug script to identify infeasible constraints.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ortools.sat.python import cp_model
import src.data as data


def debug_variables():
    """Check variable counts and available slots."""
    classes = data.get_class_groups()
    excluded = data.get_excluded_time_slots()
    required = data.get_required_time_slots()

    time_slots = data.get_time_slots()

    for class_name in sorted(classes.keys()):
        class_group = classes[class_name]
        print(f"\n{class_name}:")
        print(f"  Total periods needed: {class_group.total_periods()}")

        # Count available slots
        available = 0
        for day, period in time_slots:
            if (day, period) not in excluded.get(class_name, set()):
                available += 1

        print(f"  Available slots: {available}")

        # Check each course
        for course_name, course in class_group.courses.items():
            print(f"    {course_name}: {course.periods_per_week} periods")


def debug_time_slots():
    """Check time slot distribution."""
    time_slots = data.get_time_slots()
    excluded = data.get_excluded_time_slots()
    required = data.get_required_time_slots()

    print("\nTime Slot Distribution:")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for day in range(5):
        periods = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
        print(f"{day_names[day]}: {periods} periods")

    print("\nExcluded Slots:")
    for class_name, slots in sorted(excluded.items()):
        if slots:
            print(f"  {class_name}: {slots}")

    print("\nRequired Slots:")
    for class_name, slots in sorted(required.items()):
        if slots:
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
            for (day, period), course in slots.items():
                print(f"  {class_name}: {day_names[day]} Period {period} -> {course}")


def debug_joint_sessions():
    """Check joint session requirements."""
    sessions = data.get_joint_sessions()

    print("\nJoint Sessions:")
    for session in sessions:
        print(f"  {session.course_name}: {session.classes}")
        print(f"    Teachers: {session.teachers}")


if __name__ == "__main__":
    print("=" * 60)
    print("CLASS SCHEDULE DEBUG")
    print("=" * 60)

    debug_variables()
    debug_time_slots()
    debug_joint_sessions()

    print("\n" + "=" * 60)
