# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

High school class scheduling system using Google OR-Tools CP-SAT constraint solver. Schedules 18 classes across grades 9-12 into 35 weekly time slots while satisfying 70+ complex constraints including teacher conflicts, joint sessions, EAL synchronization, 9th grade English tracking classes (走班制), and special time requirements.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scheduler (default: 300s timeout)
python main.py

# Run with custom timeout (seconds)
python main.py 600

# Verify constraints on existing solution
python check_constraints.py

# Check time slot feasibility before solving
python check_feasibility.py
```

Output files are written to `output/`:
- `global_schedule.csv` - All classes by time slot
- `{class}_schedule.csv` - Individual class schedules
- `report.txt` - Validation report

## Architecture

```
src/
├── data.py         # Class/course/teacher definitions, joint sessions, time constraints
├── models.py       # Data classes: Course, ClassGroup, JointSession, TimeSlot
├── constraints.py  # All CP-SAT constraints (A-S categories)
├── solver.py       # CP-SAT model building and solving
└── output.py       # CSV/report generation
```

### Data Flow
1. `data.py` defines all scheduling data (classes, courses, teachers, constraints)
2. `solver.py` creates CP-SAT boolean variables: `schedule[class, course, day, period]`
3. `constraints.py` adds all constraint types to the model
4. Soft constraints use weighted objective function for optimization
5. `output.py` formats and exports the solution

### Key Constraint Categories (in constraints.py)
- **A**: Basic (course hours, one course per slot)
- **B**: Joint sessions (synchronized multi-class courses)
- **C**: Teacher conflicts (same teacher can't teach two classes simultaneously)
- **D-K**: English teacher cross-grade conflicts
- **E3/E4**: EAL synchronization with Psych&Geo and Phys&Bio
- **L-N**: 9-Eng-A/10-A English synchronization and conflicts
- **O**: Group 2 AP requires 10-A Chemistry/Phys&Bio overlap
- **P**: Art vs Group 1 AP conflict (Shiwen teaches both)
- **Q**: Soft - daily AP course optimization
- **R/S**: Per-grade daily course limits
- **T**: 9th grade tracking English A/B/C vs admin class 9-A/9-B mutual exclusion
- **U**: 9th grade tracking English D/E vs admin class 9-C mutual exclusion
- **V**: Tracking English A/B/C vs D/E teacher conflict (LZY teaches A+E, Ezio teaches C+D)

### Soft Constraints (Optimization Objectives)
Located in `add_soft_constraints()` - uses weighted consecutive pair variables:
- Cal-ABBC, Group AP, BC-Stats, AP Seminar: +3 weight (prefer consecutive)
- English: -1 weight (minimize consecutive)
- Algebra, Pre-Cal: -2 weight (avoid consecutive)

## Key Data Structures

**Joint Sessions** (in `data.py:get_joint_sessions()`): Classes that must attend simultaneously. Teachers in joint sessions don't create conflicts.

**EAL Constraints**:
- E3: `Psych&Geo ⇒ EAL` (implication, not equality)
- E4: 10-EAL-C has exactly 3 periods overlapping with 10-A/10-C Phys&Bio

**Time Configuration**: Mon=6, Tue=8, Wed=8, Thu=6, Fri=7 periods (35 total)

## Modifying Constraints

To add a new constraint:
1. Add the constraint logic in `constraints.py` in the appropriate method
2. Call the new method from `add_all_constraints()`
3. If it's a soft constraint, add to `consecutive_pairs` or `daily_ap_indicators` lists
4. Update validation in `solver.py:validate_solution()` if needed

## Troubleshooting

- **INFEASIBLE**: Check `check_feasibility.py` for time slot availability issues
- **Slow solving**: Reduce `time_limit_seconds` in `main.py` or simplify constraints
- **Constraint violations**: Run `check_constraints.py` after solving to identify specific issues
