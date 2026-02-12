"""
Output module for the class scheduling system.
Generates global time table and statistics reports.
"""
from typing import Dict, List, Tuple
import csv
import os
from src.solver import ClassScheduleSolver
import src.data as data


class ScheduleOutput:
    """Handles output formatting and file generation for schedules."""

    def __init__(self, solver: ClassScheduleSolver):
        """
        Initialize the output handler.

        Args:
            solver: The solver instance with the solution
        """
        self.solver = solver
        self.solution = solver.get_solution()
        self.classes = solver.classes
        self.time_slots = solver.time_slots

    def print_global_schedule(self):
        """Print the global schedule by time slot (all classes)."""
        if self.solution is None:
            print("No solution to display.")
            return

        print("\n" + "=" * 100)
        print("GLOBAL SCHEDULE (By Time Slot)")
        print("=" * 100)

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        for day in range(5):
            periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)

            print(f"\n{day_names[day]}")
            print("-" * 96)

            for period in range(1, periods_per_day + 1):
                print(f"  Period {period:2d}: ", end="")

                # Find all classes scheduled at this time
                scheduled_classes = []
                for class_name in sorted(self.classes.keys()):
                    if (class_name, day, period) in self.solution:
                        course_name, teacher = self.solution[(class_name, day, period)]
                        scheduled_classes.append(f"{class_name} {course_name}({teacher})")

                if scheduled_classes:
                    print(", ".join(scheduled_classes))
                else:
                    print("[No classes scheduled]")

    def print_class_schedules(self):
        """Print individual class schedules."""
        if self.solution is None:
            print("No solution to display.")
            return

        print("\n" + "=" * 100)
        print("CLASS SCHEDULES")
        print("=" * 100)

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        for class_name in sorted(self.classes.keys()):
            class_group = self.classes[class_name]
            print(f"\n{class_name} (Grade {class_group.grade})")
            print("-" * 40)

            # Print header
            print(f"{'Period':<8}", end="")
            for day in range(5):
                print(f"{day_names[day]:<12}", end="")
            print()

            periods_per_day_list = [6, 8, 8, 6, 7]
            max_periods = max(periods_per_day_list)

            for period in range(1, max_periods + 1):
                print(f"{period:<8}", end="")

                for day in range(5):
                    periods_per_day = periods_per_day_list[day]
                    if period > periods_per_day:
                        print(f"{'-':<12}", end="")
                        continue

                    if (class_name, day, period) in self.solution:
                        course_name, teacher = self.solution[(class_name, day, period)]
                        display = f"{course_name[:10]}"
                        if len(display) > 10:
                            display = display[:7] + ".."
                        print(f"{display:<12}", end="")
                    else:
                        if (day, period) in data.get_excluded_time_slots().get(class_name, set()):
                            print(f"{'[X]':<12}", end="")
                        else:
                            print(f"{'[Free]':<12}", end="")

                print()

    def save_to_csv(self, output_dir: str = "output"):
        """Save the schedule to CSV files."""
        if self.solution is None:
            print("No solution to save.")
            return

        os.makedirs(output_dir, exist_ok=True)

        # 1. Global schedule CSV
        global_csv = os.path.join(output_dir, "global_schedule.csv")
        with open(global_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Day", "Period", "Class", "Course", "Teacher"])

            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

            for day in range(5):
                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                for period in range(1, periods_per_day + 1):
                    for class_name in sorted(self.classes.keys()):
                        if (class_name, day, period) in self.solution:
                            course_name, teacher = self.solution[(class_name, day, period)]
                            writer.writerow([day_names[day], period, class_name, course_name, teacher])

        print(f"Global schedule saved to: {global_csv}")

        # 2. Individual class schedules
        for class_name in sorted(self.classes.keys()):
            class_csv = os.path.join(output_dir, f"{class_name}_schedule.csv")
            with open(class_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Day", "Period", "Course", "Teacher"])

                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

                for day in range(5):
                    periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                    for period in range(1, periods_per_day + 1):
                        if (class_name, day, period) in self.solution:
                            course_name, teacher = self.solution[(class_name, day, period)]
                            writer.writerow([day_names[day], period, course_name, teacher])
                        elif (day, period) not in data.get_excluded_time_slots().get(class_name, set()):
                            writer.writerow([day_names[day], period, "[Free]", ""])

        print(f"Individual class schedules saved to: {output_dir}/")

    def save_report(self, output_dir: str = "output"):
        """Save a validation and statistics report."""
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, "report.txt")
        is_valid, errors = self.solver.validate_solution()

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CLASS SCHEDULE REPORT\n")
            f.write("=" * 80 + "\n\n")

            # Solution status
            status = self.solver.solver.StatusName(self.solver.status)
            f.write(f"Solver Status: {status}\n\n")

            # Validation results
            f.write("VALIDATION RESULTS:\n")
            f.write("-" * 40 + "\n")
            if is_valid:
                f.write("[OK] Solution is valid!\n\n")
            else:
                f.write("[X] Solution has errors:\n")
                for error in errors:
                    f.write(f"  - {error}\n")
                f.write("\n")

            # Statistics
            stats = self.solver.get_statistics()
            if stats:
                f.write("STATISTICS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total time slots per week: {stats['total_slots']}\n")
                f.write(f"Total classes: {stats['classes']}\n")
                f.write(f"Total scheduled periods: {stats['scheduled_periods']}\n\n")

            # Class period counts
            f.write("CLASS PERIOD COUNTS:\n")
            f.write("-" * 40 + "\n")
            for class_name in sorted(self.classes.keys()):
                class_group = self.classes[class_name]
                expected = class_group.total_periods()
                actual = stats.get(f"{class_name}_periods", 0)
                status_symbol = "[OK]" if expected == actual else "[X]"
                f.write(f"  {status_symbol} {class_name}: {actual}/{expected} periods\n")

            f.write("\n")

            # Joint sessions check
            f.write("JOINT SESSIONS:\n")
            f.write("-" * 40 + "\n")
            for session in self.solver.joint_sessions:
                f.write(f"  {session.course_name}: {', '.join(session.classes)}\n")
                f.write(f"    Teachers: {', '.join(session.teachers)}\n")

            f.write("\n")

            # Excluded time slots
            f.write("EXCLUDED TIME SLOTS:\n")
            f.write("-" * 40 + "\n")
            excluded = data.get_excluded_time_slots()
            for class_name, slots in sorted(excluded.items()):
                if slots:
                    f.write(f"  {class_name}: {slots}\n")

            f.write("\n")

            # Required time slots
            f.write("REQUIRED TIME SLOTS:\n")
            f.write("-" * 40 + "\n")
            required = data.get_required_time_slots()
            for class_name, slots in sorted(required.items()):
                if slots:
                    for (day, period), course in slots.items():
                        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
                        f.write(f"  {class_name}: {day_names[day]} Period {period} - {course}\n")

        print(f"Report saved to: {report_path}")

        return is_valid, errors

    def print_consecutive_analysis(self):
        """Analyze and print consecutive period satisfaction (soft constraints)."""
        if self.solution is None:
            return

        print("\n" + "=" * 80)
        print("CONSECUTIVE PERIOD ANALYSIS (Soft Constraints)")
        print("=" * 80)

        consecutive_courses = data.get_preferred_consecutive_courses()

        for course_name in consecutive_courses:
            print(f"\n{course_name}:")
            print("-" * 40)

            for class_name in sorted(self.classes.keys()):
                if course_name not in self.classes[class_name].courses:
                    continue

                # Find all scheduled periods for this course
                scheduled_slots = []
                for (cn, day, period), (c_name, _) in self.solution.items():
                    if cn == class_name and c_name == course_name:
                        scheduled_slots.append((day, period))

                # Sort by day and period
                scheduled_slots.sort()

                # Count consecutive pairs
                consecutive_count = 0
                for i in range(len(scheduled_slots) - 1):
                    d1, p1 = scheduled_slots[i]
                    d2, p2 = scheduled_slots[i + 1]
                    if d1 == d2 and p2 == p1 + 1:
                        consecutive_count += 1

                expected_pairs = 1 if self.classes[class_name].courses[course_name].periods_per_week == 2 else 2
                status = "[OK]" if consecutive_count >= expected_pairs else "[~]"
                print(f"  {status} {class_name}: {consecutive_count}+ consecutive pairs (expected: {expected_pairs})")
                print(f"      Scheduled at: {scheduled_slots}")
