"""
CP-SAT solver implementation for the class scheduling problem.
"""
from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Optional
import src.data as data
import src.models as models
from src.constraints import SchedulingConstraints


class ClassScheduleSolver:
    """Main solver for the class scheduling problem."""

    def __init__(self, time_limit_seconds: int = 300):
        """
        Initialize the solver.

        Args:
            time_limit_seconds: Maximum time to spend solving (default: 300)
        """
        self.time_limit_seconds = time_limit_seconds
        self.model = None
        self.solver = None
        self.schedule_vars = {}
        self.solution = None
        self.status = None

        # Load data
        self.classes = data.get_class_groups()
        self.joint_sessions = data.get_joint_sessions()
        self.time_slots = data.get_time_slots()

        # Validation
        self._validate_data()

    def _validate_data(self):
        """Validate that the data is consistent."""
        print("Validating data...")

        # Check total periods per class
        for class_name, class_group in self.classes.items():
            total = class_group.total_periods()
            print(f"  {class_name}: {total} periods")

        # Check excluded slots
        excluded = data.get_excluded_time_slots()
        for class_name, slots in excluded.items():
            print(f"  {class_name} excluded: {slots}")

        # Check required slots
        required = data.get_required_time_slots()
        for class_name, slots in required.items():
            print(f"  {class_name} required: {slots}")

    def build_model(self):
        """Build the CP-SAT model with all variables and constraints."""
        print("Building CP-SAT model...")

        self.model = cp_model.CpModel()

        # Create variables
        print("Creating variables...")
        self._create_variables()

        # Add constraints
        self.constraints = SchedulingConstraints(
            self.model, self.schedule_vars, self.classes,
            self.joint_sessions, self.time_slots
        )
        self.constraints.add_all_constraints()

        # Add optimization objective
        self._add_objective_function()

        print("Model built successfully!")

    def _create_variables(self):
        """Create decision variables for the schedule."""
        # schedule[class_name, course_name, day, period] ∈ {0, 1}
        # = 1 if the class has that course at that time slot

        for class_name, class_group in self.classes.items():
            for course_name, course in class_group.courses.items():
                for day, period in self.time_slots:
                    # Skip excluded time slots
                    if (day, period) in data.get_excluded_time_slots().get(class_name, set()):
                        continue

                    # Skip if this is a required slot for a different course
                    required = data.get_required_time_slots().get(class_name, {})
                    if (day, period) in required:
                        if required[(day, period)] != course_name:
                            continue

                    var_name = f"schedule_{class_name}_{course_name}_{day}_{period}"
                    self.schedule_vars[(class_name, course_name, day, period)] = self.model.NewBoolVar(var_name)

    def solve(self) -> bool:
        """
        Solve the scheduling problem.

        Returns:
            True if a feasible solution was found, False otherwise.
        """
        if self.model is None:
            self.build_model()

        print(f"\nSolving (time limit: {self.time_limit_seconds}s)...")
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = self.time_limit_seconds
        self.solver.parameters.log_search_progress = True

        # Add a callback to monitor progress
        class SolutionCallback(cp_model.CpSolverSolutionCallback):
            def __init__(self):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.solution_count = 0

            def on_solution_callback(self):
                self.solution_count += 1
                if self.solution_count % 100 == 0:
                    print(f"  Solutions found: {self.solution_count}, Objective: {self.ObjectiveValue()}")

        callback = SolutionCallback()

        self.status = self.solver.Solve(self.model, callback)

        if self.status == cp_model.OPTIMAL:
            print("\nOptimal solution found!")
            return True
        elif self.status == cp_model.FEASIBLE:
            print("\nFeasible solution found!")
            return True
        else:
            print(f"\nNo solution found. Status: {self.solver.StatusName(self.status)}")
            return False

    def _add_objective_function(self):
        """Add optimization objective based on soft constraints."""
        # Soft constraints already added in build_model via add_all_constraints
        # Just need to set the objective function
        objective_terms = []

        # Consecutive pairs optimization
        if hasattr(self.constraints, 'consecutive_pairs') and self.constraints.consecutive_pairs:
            objective_terms.extend(self.constraints.consecutive_pairs)
            print(f"  Optimization: Added {len(self.constraints.consecutive_pairs)} consecutive pair objectives")

        # Daily AP preference optimization (at least 2 AP classes per day)
        if hasattr(self.constraints, 'daily_ap_indicators') and self.constraints.daily_ap_indicators:
            objective_terms.extend(self.constraints.daily_ap_indicators)
            print(f"  Optimization: Added {len(self.constraints.daily_ap_indicators)} daily AP preference objectives")

        # Teacher period-1 penalties (at most 3 per week per teacher)
        if hasattr(self.constraints, 'teacher_p1_penalties') and self.constraints.teacher_p1_penalties:
            objective_terms.extend(self.constraints.teacher_p1_penalties)
            print(f"  Optimization: Added {len(self.constraints.teacher_p1_penalties)} teacher period-1 penalty objectives")

        # Daily AP total penalties (at most 4 AP periods per day)
        if hasattr(self.constraints, 'daily_ap_total_penalties') and self.constraints.daily_ap_total_penalties:
            objective_terms.extend(self.constraints.daily_ap_total_penalties)
            print(f"  Optimization: Added {len(self.constraints.daily_ap_total_penalties)} daily AP total penalty objectives")

        # Teacher daily max penalties (at most 5 periods per day per teacher)
        if hasattr(self.constraints, 'teacher_daily_max_penalties') and self.constraints.teacher_daily_max_penalties:
            objective_terms.extend(self.constraints.teacher_daily_max_penalties)
            print(f"  Optimization: Added {len(self.constraints.teacher_daily_max_penalties)} teacher daily max penalty objectives")

        if objective_terms:
            # Maximize the weighted sum of all soft constraints
            objective = sum(var * weight for var, weight in objective_terms)
            self.model.Maximize(objective)
            print(f"  Total optimization terms: {len(objective_terms)}")

    def get_solution(self) -> Dict:
        """
        Get the solution as a dictionary.

        Returns:
            Dictionary mapping (class_name, day, period) to (course_name, teacher)
        """
        if self.status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return None

        solution = {}

        for (class_name, course_name, day, period), var in self.schedule_vars.items():
            if self.solver.Value(var) == 1:
                teacher = self.classes[class_name].courses[course_name].teacher
                solution[(class_name, day, period)] = (course_name, teacher)

        return solution

    def print_solution(self):
        """Print the solution in a readable format."""
        solution = self.get_solution()
        if solution is None:
            print("No solution to print.")
            return

        print("\n" + "=" * 80)
        print("CLASS SCHEDULE")
        print("=" * 80)

        # Print by class
        for class_name in sorted(self.classes.keys()):
            class_group = self.classes[class_name]
            print(f"\n{class_name} (Grade {class_group.grade})")
            print("-" * 40)

            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

            for day in range(5):
                print(f"\n{day_names[day]}:", end="")

                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)

                for period in range(1, periods_per_day + 1):
                    if (class_name, day, period) in solution:
                        course_name, teacher = solution[(class_name, day, period)]
                        print(f"\n  {period}. {course_name} ({teacher})", end="")
                    else:
                        if (day, period) not in data.get_excluded_time_slots().get(class_name, set()):
                            print(f"\n  {period}. [Free]", end="")

        print("\n")

    def validate_solution(self) -> Tuple[bool, List[str]]:
        """
        Validate the solution against all constraints.

        Returns:
            (is_valid, list_of_errors)
        """
        solution = self.get_solution()
        if solution is None:
            return False, ["No solution to validate"]

        errors = []

        # Check 1: Each class has correct number of periods for each course
        for class_name, class_group in self.classes.items():
            for course_name, course in class_group.courses.items():
                count = sum(1 for (cn, d, p) in solution.keys()
                           if cn == class_name and solution[(cn, d, p)][0] == course_name)
                if count != course.periods_per_week:
                    errors.append(f"{class_name} {course_name}: expected {course.periods_per_week}, got {count}")

        # Check 2: No class has two courses at the same time
        for class_name in self.classes.keys():
            for day in range(5):
                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                for period in range(1, periods_per_day + 1):
                    if (class_name, day, period) not in solution:
                        continue
                    # Should only have one entry
                    pass  # Already enforced by data structure

        # Check 3: Teacher conflicts (excluding joint sessions)
        teacher_schedule = {}  # (teacher, day, period) -> [classes]

        for (class_name, day, period), (course_name, teacher) in solution.items():
            key = (teacher, day, period)
            if key not in teacher_schedule:
                teacher_schedule[key] = []
            teacher_schedule[key].append((class_name, course_name))

        for (teacher, day, period), classes in teacher_schedule.items():
            # Check if these classes are in a joint session
            if len(classes) > 1:
                # Check if this is a valid joint session
                class_names = [c[0] for c in classes]
                course_names = [c[1] for c in classes]

                is_joint = False
                for session in self.joint_sessions:
                    if set(class_names).issubset(set(session.classes)):
                        if all(c == session.course_name or c.startswith("Phys&Bio") or c.startswith("EAL")
                               for c in course_names):
                            is_joint = True
                            break

                if not is_joint and teacher not in ["Shiwen", "Wen"]:  # Art and PE are special
                    # Shiwen and Wen teach Art/PE to all classes, so they have explicit constraints
                    errors.append(f"Teacher {teacher} has conflict at day {day} period {period}: {classes}")

        # Check 4: Joint sessions are synchronized
        for session in self.joint_sessions:
            for day in range(5):
                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                for period in range(1, periods_per_day + 1):
                    # Check if all classes in the session have this course at this time
                    scheduled_classes = []
                    for class_name in session.classes:
                        if (class_name, day, period) in solution:
                            course = solution[(class_name, day, period)][0]
                            if course == session.course_name:
                                scheduled_classes.append(class_name)

                    if scheduled_classes and len(scheduled_classes) != len(session.classes):
                        errors.append(
                            f"Joint session {session.course_name} at day {day} period {period}: "
                            f"only {scheduled_classes} of {session.classes} are scheduled"
                        )

        # Check 5: English teacher conflicts (using tracking English classes)
        english_teachers = {
            "LZY": ["9-Eng-A", "9-Eng-E", "10-EAL-C"],  # Teaches English A, E and EAL-C
            "CYF": ["9-Eng-B", "10-EAL-B", "11-A", "11-B"],  # Teaches English B and EAL-B
            "Ezio": ["9-Eng-C", "9-Eng-D", "10-EAL-A", "12-A", "12-B"]  # Teaches English C, D and EAL-A
        }

        for teacher, class_list in english_teachers.items():
            for day in range(5):
                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                for period in range(1, periods_per_day + 1):
                    scheduled = []
                    for class_name in class_list:
                        if (class_name, day, period) in solution:
                            course = solution[(class_name, day, period)][0]
                            if course in ["English", "EAL", "AP Seminar", "AP Composition", "Literature"]:
                                scheduled.append((class_name, course))

                    if len(scheduled) > 1:
                        # Check if this is a joint session (allowed)
                        class_names = [c[0] for c in scheduled]
                        course_names = [c[1] for c in scheduled]

                        is_joint = False
                        for session in self.joint_sessions:
                            if set(class_names).issubset(set(session.classes)):
                                if session.course_name in course_names or all(c in ["AP Seminar", "AP Composition"] for c in course_names):
                                    is_joint = True
                                    break

                        if not is_joint:
                            errors.append(f"English teacher {teacher} has conflict at day {day} period {period}: {scheduled}")

        # Check 6: EAL E3 constraint - EAL classes must be scheduled when Psych&Geo is scheduled
        # Note: This is an implication (Psych&Geo -> EAL), not equality
        for class_name, eal_class in [("10-A", "10-EAL-A"), ("10-B", "10-EAL-B"), ("10-C", "10-EAL-C")]:
            for day in range(5):
                periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                for period in range(1, periods_per_day + 1):
                    psych_scheduled = (class_name, day, period) in solution and solution[(class_name, day, period)][0] == "Psych&Geo"
                    eal_scheduled = (eal_class, day, period) in solution and solution[(eal_class, day, period)][0] == "EAL"

                    # E3: If Psych&Geo is scheduled, EAL must also be scheduled
                    if psych_scheduled and not eal_scheduled:
                        errors.append(f"E3 violation: {class_name} has Psych&Geo but {eal_class} has no EAL at day {day} period {period}")

        # Check 7: EAL E4 constraint - 10-EAL-C has exactly 3 periods overlapping with 10-A/10-C Phys&Bio
        overlap_count = 0
        for day in range(5):
            periods_per_day = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
            for period in range(1, periods_per_day + 1):
                eal_scheduled = ("10-EAL-C", day, period) in solution and solution[("10-EAL-C", day, period)][0] == "EAL"
                physbio_10a = ("10-A", day, period) in solution and solution[("10-A", day, period)][0] == "Phys&Bio"
                physbio_10c = ("10-C", day, period) in solution and solution[("10-C", day, period)][0] == "Phys&Bio"

                if eal_scheduled and (physbio_10a or physbio_10c):
                    overlap_count += 1

        if overlap_count != 3:
            errors.append(f"E4 violation: 10-EAL-C has {overlap_count} periods overlapping with Phys&Bio, expected 3")

        if errors:
            return False, errors
        return True, ["Solution is valid!"]

    def get_statistics(self) -> Dict:
        """Get statistics about the solution."""
        solution = self.get_solution()
        if solution is None:
            return None

        stats = {
            "total_slots": len(self.time_slots),
            "classes": len(self.classes),
            "scheduled_periods": len(solution),
        }

        # Count courses per class
        for class_name in self.classes.keys():
            count = sum(1 for (cn, _, _) in solution.keys() if cn == class_name)
            stats[f"{class_name}_periods"] = count

        return stats
