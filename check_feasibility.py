"""
Check feasibility of course requirements against available time slots.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import src.data as data


def check_feasibility():
    """Check if each course has enough available time slots."""
    classes = data.get_class_groups()
    excluded = data.get_excluded_time_slots()
    required = data.get_required_time_slots()

    time_slots = data.get_time_slots()

    print("COURSE FEASIBILITY CHECK")
    print("=" * 60)

    infeasible = []

    for class_name, class_group in sorted(classes.items()):
        print(f"\n{class_name}:")

        # Count available slots for each course
        for course_name, course in class_group.courses.items():
            available = 0
            for day, period in time_slots:
                if (day, period) in excluded.get(class_name, set()):
                    continue

                # Check if this slot is required for a different course
                req = required.get(class_name, {})
                if (day, period) in req:
                    if req[(day, period)] != course_name:
                        continue  # This slot is for another course

                available += 1

            if available < course.periods_per_week:
                status = "INFEASIBLE"
                infeasible.append((class_name, course_name, available, course.periods_per_week))
            else:
                status = "OK"

            print(f"  {course_name}: {course.periods_per_week} periods needed, {available} available - {status}")

    if infeasible:
        print("\n" + "=" * 60)
        print("INFEASIBLE COURSES FOUND:")
        for class_name, course_name, available, needed in infeasible:
            print(f"  {class_name} {course_name}: need {needed}, have {available}")
    else:
        print("\n" + "=" * 60)
        print("All courses have sufficient available slots!")


if __name__ == "__main__":
    check_feasibility()
