"""
Main entry point for the High School Class Scheduling System.

This system uses Google OR-Tools CP-SAT solver to automatically generate
a weekly schedule for 9-12th grade classes, satisfying complex constraints
including teacher conflicts, joint sessions, and special time arrangements.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.solver import ClassScheduleSolver
from src.output import ScheduleOutput


def main():
    """Main function to run the scheduling system."""
    print("=" * 80)
    print("HIGH SCHOOL CLASS SCHEDULING SYSTEM")
    print("=" * 80)
    print()

    # Configuration
    time_limit = 300  # 5 minutes

    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            time_limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid time limit: {sys.argv[1]}")
            print(f"Usage: python main.py [time_limit_seconds]")
            return

    print(f"Configuration:")
    print(f"  Time limit: {time_limit} seconds")
    print()

    # Initialize solver
    print("Initializing solver...")
    solver = ClassScheduleSolver(time_limit_seconds=time_limit)

    # Build model
    solver.build_model()

    # Solve
    success = solver.solve()

    if not success:
        print("\n" + "=" * 80)
        print("NO SOLUTION FOUND")
        print("=" * 80)
        print("\nThe solver could not find a feasible solution within the time limit.")
        print("Consider:")
        print("  1. Increasing the time limit")
        print("  2. Relaxing some constraints")
        print("  3. Checking the data for inconsistencies")
        return

    # Generate output
    output = ScheduleOutput(solver)

    # Print global schedule
    output.print_global_schedule()

    # Print class schedules
    output.print_class_schedules()

    # Print consecutive period analysis
    output.print_consecutive_analysis()

    # Save files
    print("\n" + "=" * 80)
    print("SAVING OUTPUT FILES")
    print("=" * 80)

    output.save_to_csv()
    output.save_report()

    # Validation
    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    is_valid, errors = solver.validate_solution()
    if is_valid:
        print("[OK] Solution is valid!")
    else:
        print("[X] Solution has errors:")
        for error in errors:
            print(f"  - {error}")

    print("\n" + "=" * 80)
    print("SCHEDULING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
