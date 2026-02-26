# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

High school class scheduling system using Google OR-Tools CP-SAT constraint solver. Schedules 18 classes across grades 9-12 into 35 weekly time slots while satisfying 70+ complex constraints including teacher conflicts, joint sessions, EAL synchronization, 9th grade English tracking classes (走班制), and special time requirements.

## Commands

```bash
# Install dependencies (ortools, pandas)
pip install -r requirements.txt

# Run the scheduler (default: 300s timeout)
python main.py

# Run with custom timeout (seconds)
python main.py 600

# Verify constraints on existing solution (reads output/global_schedule.csv)
python check_constraints.py

# Check time slot feasibility before solving
python check_feasibility.py

# Debug: inspect variable counts, available slots, joint sessions
python debug.py

# Test: isolate Art/PE constraints to check feasibility
python test_minimal.py
```

Output files are written to `output/`:
- `global_schedule.csv` - All classes by time slot
- `{class}_schedule.csv` - Individual class schedules
- `report.txt` - Validation report

## Architecture

```
src/
├── data.py         # All scheduling data: classes, courses, teachers, joint sessions, time constraints
├── models.py       # Dataclasses: Course, ClassGroup, JointSession, TimeSlot, ScheduleConfig
├── constraints.py  # SchedulingConstraints class with all CP-SAT constraints (A-Z categories)
├── solver.py       # ClassScheduleSolver: model building, solving, validation
└── output.py       # ScheduleOutput: CSV/report generation, consecutive analysis
```

### Data Flow
1. `data.py` defines all scheduling data (classes, courses, teachers, constraints) via getter functions
2. `solver.py` creates CP-SAT boolean variables: `schedule[class, course, day, period]`
3. `constraints.py` adds all constraint types to the model via `add_all_constraints()`
4. Soft constraints are collected as `(var, weight)` tuples in `consecutive_pairs`, `daily_ap_indicators`, `teacher_p1_penalties`, `daily_ap_total_penalties`, and `teacher_daily_max_penalties` lists
5. `solver.py:_add_objective_function()` combines soft constraints into a single `Maximize` objective
6. `output.py` formats and exports the solution

### Teacher String Convention
Teachers are stored as strings. Multi-teacher courses use comma-separated values (e.g., `"Yan,Song"`, `"Ezio,Lucy,Darin"`). Use `Course.get_teachers()` to split into a list.

### Key Constraint Categories (in constraints.py)
- **A**: Basic (course hours, one course per slot)
- **B**: Joint sessions (synchronized multi-class courses)
- **C**: Teacher conflicts (same teacher can't teach two classes simultaneously)
- **D-K**: Cross-grade teacher conflicts (English teachers, Guo, Darin, etc.)
- **E3/E4**: EAL synchronization — E3: `Psych&Geo ⇒ EAL` (implication); E4: 10-EAL-C has exactly 3 periods overlapping with 10-A/10-C Phys&Bio
- **H**: 11-A English syncs with 12-A/B AP Seminar
- **I**: Lucy conflict (AP Seminar vs 10th English)
- **L-N**: 9-Eng-A/10-A English synchronization and conflict constraints
- **O**: Group 2 AP requires 10-A Chemistry/Phys&Bio overlap
- **P**: Art vs Group 1 AP conflict (Shiwen teaches both)
- **Q**: Soft — daily AP course optimization (+1 weight per day with >=2 AP courses)
- **R/S**: Per-grade daily course limits (9th grade and 10th grade)
- **T**: Tracking English A/B/C vs admin class 9-A/9-B mutual exclusion
- **U**: Tracking English D/E vs admin class 9-C mutual exclusion
- **V**: Tracking English A/B/C vs D/E teacher conflict (LZY teaches A+E, Ezio teaches C+D)
- **W**: Hard — if a class has 2 periods of the same course on the same day, they must be consecutive
- **X**: Soft — each teacher should teach period 1 at most 3 times per week (-2 penalty per excess day)
- **Y**: Soft — daily total AP periods (Group 1 + 2 + 3) should not exceed 4 (-2 penalty per excess period)
- **Z**: Soft — each teacher should teach at most 5 periods per day (-2 penalty per excess period)

### Soft Constraints (Optimization Objectives)
Located in `add_soft_constraints()` — uses weighted consecutive pair variables:
- Cal-ABBC, Group AP, BC-Stats, AP Seminar: **+3** weight (prefer consecutive)
- Art: **+2** weight (prefer consecutive)
- English: **-1** weight (minimize consecutive)
- Algebra, Pre-Cal: **-2** weight (avoid consecutive)

## Key Data Structures

**Joint Sessions** (in `data.py:get_joint_sessions()`): Classes that must attend simultaneously. Teachers in joint sessions don't create conflicts with each other.

**9th Grade Tracking English (走班制)**: Admin classes 9-A/9-B/9-C have no English course. Instead, students attend tracking English classes (9-Eng-A/B/C from 9-A/9-B students, 9-Eng-D/E from 9-C students). A/B/C are joint; D/E are joint; A/B/C and D/E cannot overlap.

**EAL Constraints**:
- E3: `Psych&Geo ⇒ EAL` (one-way implication, not equality)
- E4: 10-EAL-C has exactly 3 periods overlapping with 10-A/10-C Phys&Bio (uses `AddMinEquality`/`AddMaxEquality`)

**Time Configuration**: Mon=6, Tue=8, Wed=8, Thu=6, Fri=7 periods (35 total). Days are 0-indexed (0=Mon). Periods are 1-indexed.

## Modifying Constraints

To add a new constraint:
1. Add the constraint logic as a method in `SchedulingConstraints` (in `constraints.py`)
2. Call the new method from `add_all_constraints()`
3. If it's a soft constraint, append `(var, weight)` tuples to the appropriate list (`consecutive_pairs`, `daily_ap_indicators`, `teacher_p1_penalties`, `daily_ap_total_penalties`, or `teacher_daily_max_penalties`) and collect them in `solver.py:_add_objective_function()`
4. Update validation in `solver.py:validate_solution()` if needed
5. Update `check_constraints.py` to verify the new constraint against CSV output

## Troubleshooting

- **INFEASIBLE**: Run `check_feasibility.py` first to find time slot availability issues. Use `debug.py` to inspect variable counts and slot availability. Use `test_minimal.py` to isolate which constraint group causes infeasibility.
- **Slow solving**: Increase `time_limit_seconds` arg to `main.py` or simplify constraints
- **Constraint violations**: Run `check_constraints.py` after solving to identify specific issues
- **REQUIREMENTS.md**: Contains the full specification in Chinese (中文) with all constraint details, verification results, and version history
