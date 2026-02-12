"""
Constraint definitions for the class scheduling system.
Uses Google OR-Tools CP-SAT solver.
"""
from ortools.sat.python import cp_model
from typing import Dict, List, Set, Tuple
import src.data as data
import src.models as models


class SchedulingConstraints:
    """Encapsulates all scheduling constraints for the CP-SAT model."""

    def __init__(self, model: cp_model.CpModel, schedule_vars: Dict,
                 classes: Dict[str, models.ClassGroup],
                 joint_sessions: List[models.JointSession],
                 time_slots: List[Tuple[int, int]]):
        """
        Initialize constraints.

        Args:
            model: CP-SAT model
            schedule_vars: Dictionary of schedule variables
            classes: Dictionary of class groups
            joint_sessions: List of joint sessions
            time_slots: List of (day, period) tuples
        """
        self.model = model
        self.schedule_vars = schedule_vars
        self.classes = classes
        self.joint_sessions = joint_sessions
        self.time_slots = time_slots

        # Get additional data
        self.excluded_slots = data.get_excluded_time_slots()
        self.required_slots = data.get_required_time_slots()

        # Build lookup structures
        self._build_teacher_to_classes()
        self._build_course_to_classes()
        self._build_joint_session_map()

        # Special handling: Treat 12th grade PE as a joint session for teacher purposes
        self.teacher_joint_sessions = self._get_teacher_joint_sessions()

    def _get_teacher_joint_sessions(self) -> Dict[str, List[Set[str]]]:
        """
        Get sessions where teachers teach multiple classes at once (for conflict purposes).
        Returns: teacher -> list of sets of class names that can be taught simultaneously
        """
        sessions = {}

        # 12th grade PE - both classes together
        if "Wen" not in sessions:
            sessions["Wen"] = []
        sessions["Wen"].append({"12-A", "12-B"})  # PE for 12th grade

        # 12th grade Counseling - both classes together (different periods)
        if "Wen" not in sessions:
            sessions["Wen"] = []
        sessions["Wen"].append({"12-A", "12-B"})  # Counseling for 12th grade

        # Shiwen Art - no joint sessions, each class separate
        # Wen PE for other grades - each class separate

        return sessions

    def _build_teacher_to_classes(self):
        """Build a map of teacher to the classes and courses they teach."""
        self.teacher_classes = {}  # teacher -> {(class_name, course_name)}
        for class_name, class_group in self.classes.items():
            for course_name, course in class_group.courses.items():
                # Handle multiple teachers (comma-separated)
                teachers = course.get_teachers() if hasattr(course, 'get_teachers') else [course.teacher]
                for teacher in teachers:
                    if teacher not in self.teacher_classes:
                        self.teacher_classes[teacher] = set()
                    self.teacher_classes[teacher].add((class_name, course_name))

    def _build_course_to_classes(self):
        """Build a map of course name to classes that take it."""
        self.course_classes = {}  # course_name -> {class_name}
        for class_name, class_group in self.classes.items():
            for course_name in class_group.courses.keys():
                if course_name not in self.course_classes:
                    self.course_classes[course_name] = set()
                self.course_classes[course_name].add(class_name)

    def _build_joint_session_map(self):
        """Build a map for quick joint session lookup."""
        self.joint_session_map = {}  # frozenset of classes -> JointSession
        for session in self.joint_sessions:
            key = frozenset(session.classes)
            self.joint_session_map[key] = session

        # Also build map by class
        self.class_to_joint_sessions = {}  # class_name -> [JointSession]
        for session in self.joint_sessions:
            for class_name in session.classes:
                if class_name not in self.class_to_joint_sessions:
                    self.class_to_joint_sessions[class_name] = []
                self.class_to_joint_sessions[class_name].append(session)

    def is_in_joint_session(self, class_name: str, course_name: str) -> bool:
        """Check if a class/course is part of a joint session."""
        if class_name not in self.class_to_joint_sessions:
            return False
        for session in self.class_to_joint_sessions[class_name]:
            if session.course_name == course_name:
                return True
        return False

    def get_joint_session(self, class_name: str, course_name: str) -> models.JointSession:
        """Get the joint session for a class/course."""
        if class_name not in self.class_to_joint_sessions:
            return None
        for session in self.class_to_joint_sessions[class_name]:
            if session.course_name == course_name:
                return session
        return None

    def add_all_constraints(self):
        """Add all constraints to the model."""
        print("Adding constraints...")

        # A. Basic constraints
        self.add_basic_constraints()

        # B. Joint session constraints
        self.add_joint_session_constraints()

        # C. Teacher conflict constraints
        self.add_teacher_conflict_constraints()

        # D. Special teacher constraints (English teachers) - temporarily disabled due to conflict
        # self.add_english_teacher_constraints()

        # E. Special time slot constraints (EAL synchronization - E3 and E4 are REQUIRED)
        self.add_special_time_constraints()

        # F. Daily course limit constraints
        self.add_daily_course_constraints()

        # F2. World History daily limit: max 1 per day for 10th grade
        # (already covered by add_daily_course_constraints since World History has 3 periods/week < 5)
        # self.add_world_history_daily_constraint()

        # H. AP Seminar/Composition synchronization with 11-A English (HARD CONSTRAINT)
        self.add_ap_seminar_english_sync_constraint()

        # I. Lucy teacher conflict: AP Seminar vs 10th grade English
        self.add_lucy_ap_seminar_english_conflict()

        # J. Guo teacher conflict: Group 1/2 AP vs 9th grade Physics
        self.add_guo_conflict_constraint()

        # K. Darin teacher conflict: AP Seminar (12th) vs 9th grade Social
        self.add_darin_ap_seminar_social_constraint()

        # L. 9-A/10-A English synchronization (10-A English => 9-A English)
        self.add_english_9a_10a_sync_constraint()

        # M. 9-A/10-A English vs 11-A/B Literature conflict
        self.add_english_literature_conflict_constraint()

        # N. 9-A/10-A English vs 12-A/B AP Seminar conflict
        self.add_english_ap_seminar_conflict_constraint()

        # O. Group 2 AP requires 10-A to be in Chemistry or Phys&Bio
        self.add_group2_ap_10a_requirement_constraint()

        # P. Art vs Group 1 AP conflict (Shiwen teaches both)
        self.add_art_group1_ap_conflict_constraint()

        # R. 9th grade daily course limits (special rules for English and Art)
        self.add_9th_grade_daily_limits_constraint()

        # S. 10th grade daily course limits (Art can have 2 periods on one day)
        self.add_10th_grade_daily_limits_constraint()

        # G. Soft constraints (optimization objectives)
        self.add_soft_constraints()

    def add_basic_constraints(self):
        """A. Basic constraints."""
        print("  Adding basic constraints...")

        # A1. Each class has exactly the required number of periods for each course
        for class_name, class_group in self.classes.items():
            for course_name, course in class_group.courses.items():
                periods = []
                for day, period in self.time_slots:
                    if (day, period) in self.excluded_slots.get(class_name, set()):
                        continue
                    key = (class_name, course_name, day, period)
                    if key in self.schedule_vars:
                        periods.append(self.schedule_vars[key])

                if periods:
                    self.model.Add(sum(periods) == course.periods_per_week)

        # A2. Each class has at most one course per time slot
        for class_name, class_group in self.classes.items():
            for day, period in self.time_slots:
                if (day, period) in self.excluded_slots.get(class_name, set()):
                    continue

                courses_at_slot = []
                for course_name in class_group.courses.keys():
                    key = (class_name, course_name, day, period)
                    if key in self.schedule_vars:
                        courses_at_slot.append(self.schedule_vars[key])

                if len(courses_at_slot) > 1:
                    self.model.Add(sum(courses_at_slot) <= 1)

    def add_joint_session_constraints(self):
        """B. Joint session constraints (classes must attend simultaneously)."""
        print("  Adding joint session constraints...")

        for session in self.joint_sessions:
            course_name = session.course_name

            # For each time slot, all classes in the joint session must either all have the course or none
            for day, period in self.time_slots:
                slot_vars = []
                valid_slot = True

                for class_name in session.classes:
                    # Check if this slot is excluded for this class
                    if (day, period) in self.excluded_slots.get(class_name, set()):
                        valid_slot = False
                        break

                    key = (class_name, course_name, day, period)
                    if key in self.schedule_vars:
                        slot_vars.append(self.schedule_vars[key])
                    else:
                        valid_slot = False
                        break

                if valid_slot and len(slot_vars) == len(session.classes):
                    # All classes must have the same value
                    for i in range(1, len(slot_vars)):
                        self.model.Add(slot_vars[0] == slot_vars[i])

    def add_teacher_conflict_constraints(self):
        """C. Teacher conflict constraints."""
        print("  Adding teacher conflict constraints...")

        # For each teacher, ensure they don't teach multiple classes at the same time
        for teacher, class_courses in self.teacher_classes.items():
            for day, period in self.time_slots:
                # Separate joint session courses and regular courses
                joint_session_vars = []  # One per joint session
                regular_courses = []

                counted_joint_sessions = set()

                for class_name, course_name in class_courses:
                    # Skip if slot is excluded for this class
                    if (day, period) in self.excluded_slots.get(class_name, set()):
                        continue

                    key = (class_name, course_name, day, period)
                    if key not in self.schedule_vars:
                        continue

                    # Check if this class/course is in a joint session
                    is_joint = False
                    if self.is_in_joint_session(class_name, course_name):
                        session = self.get_joint_session(class_name, course_name)
                        if session:
                            # Use both course name and classes as key (different courses = different keys)
                            session_key = (session.course_name, frozenset(session.classes))
                            if session_key not in counted_joint_sessions:
                                counted_joint_sessions.add(session_key)
                                joint_session_vars.append(self.schedule_vars[key])
                            is_joint = True
                    elif teacher in self.teacher_joint_sessions:
                        # Check if this is a teacher joint session (e.g., Wen teaching 12-A/B PE together)
                        for session_classes in self.teacher_joint_sessions[teacher]:
                            if class_name in session_classes:
                                # Verify all classes in this session have the same course
                                all_have_course = all(
                                    (cl, course_name) in class_courses
                                    for cl in session_classes
                                )
                                if all_have_course:
                                    session_key = (course_name, frozenset(session_classes))
                                    if session_key not in counted_joint_sessions:
                                        counted_joint_sessions.add(session_key)
                                        joint_session_vars.append(self.schedule_vars[key])
                                    is_joint = True
                                    break

                    if not is_joint:
                        # Regular (non-joint) course
                        regular_courses.append(self.schedule_vars[key])

                # Total courses = joint sessions (each counts as 1) + regular courses
                all_courses = joint_session_vars + regular_courses

                # Teacher can teach at most one "thing" at a time
                # (either one joint session OR one regular course)
                if len(all_courses) > 1:
                    self.model.Add(sum(all_courses) <= 1)

    def add_english_teacher_constraints(self):
        """D. English teacher constraints (cross-grade conflicts)."""
        print("  Adding English teacher constraints...")

        # LZY teaches 9-A English and 10-C EAL
        # CYF teaches 9-B English, 10-B EAL, and 11-A/B English/Literature
        # Ezio teaches 9-C English, 10-A EAL, and 12-A/B AP Seminar

        english_teachers = {
            "LZY": [("9-A", "English"), ("10-C", "EAL")],
            "CYF": [("9-B", "English"), ("10-B", "EAL"), ("11-A", "English"), ("11-A", "Literature"), ("11-B", "English"), ("11-B", "Literature")],
            "Ezio": [("9-C", "English"), ("10-A", "EAL"), ("12-A", "AP Seminar"), ("12-B", "AP Seminar")],
            "Lucy": [("10-A", "English"), ("10-B", "English"), ("10-C", "English")],
        }

        for teacher, class_courses in english_teachers.items():
            for day, period in self.time_slots:
                courses_at_slot = []

                for class_name, course_name in class_courses:
                    if (day, period) in self.excluded_slots.get(class_name, set()):
                        continue

                    key = (class_name, course_name, day, period)
                    if key in self.schedule_vars:
                        courses_at_slot.append(self.schedule_vars[key])

                # Teacher can teach at most one English course at a time
                if len(courses_at_slot) > 1:
                    self.model.Add(sum(courses_at_slot) <= 1)

    def add_special_time_constraints(self):
        """E. Special time slot constraints."""
        print("  Adding special time constraints...")

        # E1. Required time slots (e.g., 12th grade PE and Counseling)
        required_slots = data.get_required_time_slots()

        for class_name, slots in required_slots.items():
            for (day, period), course_name in slots.items():
                key = (class_name, course_name, day, period)
                if key in self.schedule_vars:
                    self.model.Add(self.schedule_vars[key] == 1)

        # E2. Excluded time slots (handled in basic constraints by not including those slots)

        # E3. EAL synchronization with Psych&Geo (10-EAL-A, 10-EAL-B, 10-EAL-C)
        # When 10-A/B/C have Psych&Geo, corresponding EAL classes must also have EAL
        e3_count = 0
        for day, period in self.time_slots:
            for class_name, eal_class in [("10-A", "10-EAL-A"), ("10-B", "10-EAL-B"), ("10-C", "10-EAL-C")]:
                psych_key = (class_name, "Psych&Geo", day, period)
                eal_key = (eal_class, "EAL", day, period)

                if psych_key in self.schedule_vars and eal_key in self.schedule_vars:
                    # If Psych&Geo is scheduled, EAL must also be scheduled
                    self.model.AddImplication(self.schedule_vars[psych_key], self.schedule_vars[eal_key])
                    e3_count += 1
        print(f"    Added {e3_count} E3 constraints (implications)")

        # E4. 10-EAL-C additional 3 periods synchronized with 10-A/10-C Phys&Bio
        # 10-EAL-C must have exactly 3 periods overlapping with 10-A or 10-C Phys&Bio
        e4_terms = []
        for day, period in self.time_slots:
            eal_key = ("10-EAL-C", "EAL", day, period)
            if eal_key not in self.schedule_vars:
                continue

            # Check if 10-A or 10-C has Phys&Bio at this time
            physbio_10a_key = ("10-A", "Phys&Bio", day, period)
            physbio_10c_key = ("10-C", "Phys&Bio", day, period)

            physbio_10a = self.schedule_vars.get(physbio_10a_key)
            physbio_10c = self.schedule_vars.get(physbio_10c_key)

            # Create overlap indicator: overlap = EAL AND (PhysBio_10A OR PhysBio_10C)
            if physbio_10a is not None and physbio_10c is not None:
                # Both 10-A and 10-C have Phys&Bio potential at this time
                has_physbio = self.model.NewBoolVar(f"has_physbio_{day}_{period}")
                self.model.AddMaxEquality(has_physbio, [physbio_10a, physbio_10c])
                overlap = self.model.NewBoolVar(f"eal_physbio_overlap_{day}_{period}")
                self.model.AddMinEquality(overlap, [self.schedule_vars[eal_key], has_physbio])
                e4_terms.append(overlap)
            elif physbio_10a is not None:
                # Only 10-A has Phys&Bio at this time
                overlap = self.model.NewBoolVar(f"eal_physbio_overlap_{day}_{period}")
                self.model.AddMinEquality(overlap, [self.schedule_vars[eal_key], physbio_10a])
                e4_terms.append(overlap)
            elif physbio_10c is not None:
                # Only 10-C has Phys&Bio at this time
                overlap = self.model.NewBoolVar(f"eal_physbio_overlap_{day}_{period}")
                self.model.AddMinEquality(overlap, [self.schedule_vars[eal_key], physbio_10c])
                e4_terms.append(overlap)

        # Require exactly 3 overlaps total
        if e4_terms:
            self.model.Add(sum(e4_terms) == 3)
            print(f"    Added E4 constraint: exactly 3 overlaps (found {len(e4_terms)} potential)")

    def add_world_history_daily_constraint(self):
        """F1. World History daily limit: max 1 per day for 10th grade."""
        print("  Adding World History daily limit constraint...")

        for class_name in ["10-A", "10-B", "10-C"]:
            if class_name not in self.classes:
                continue

            for day in range(5):
                max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)

                wh_periods = []
                for period in range(1, max_period + 1):
                    if (day, period) in self.excluded_slots.get(class_name, set()):
                        continue

                    key = (class_name, "World History", day, period)
                    if key in self.schedule_vars:
                        wh_periods.append(self.schedule_vars[key])

                if wh_periods:
                    self.model.Add(sum(wh_periods) <= 1)

        print("    Added World History daily limit: max 1 per day for 10-A/B/C")

    def add_daily_course_constraints(self):
        """F. Daily course limit constraints.
        - Courses with 5+ periods/week: at most 2 periods per day
        - All other courses: at most 1 period per day
        """
        print("  Adding daily course limit constraints...")

        constraint_count = 0

        for class_name, class_group in self.classes.items():
            for day in range(5):
                # Get max periods for this day
                max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)

                # For each course, collect periods in this day
                for course_name, course in class_group.courses.items():
                    # Skip EAL classes - they have special synchronization constraints
                    if class_name in ["10-EAL-A", "10-EAL-B", "10-EAL-C"]:
                        continue

                    day_periods = []
                    for period in range(1, max_period + 1):
                        # Skip excluded slots
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue

                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            day_periods.append(self.schedule_vars[key])

                    if day_periods:
                        # Courses with 5+ periods/week: at most 2 per day
                        # Art: at most 2 per day (to allow consecutive scheduling)
                        # All other courses: at most 1 per day
                        if course.periods_per_week >= 5 or course_name == "Art":
                            self.model.Add(sum(day_periods) <= 2)
                            constraint_count += 1
                        else:
                            self.model.Add(sum(day_periods) <= 1)
                            constraint_count += 1

        print(f"    Added {constraint_count} daily course limit constraints")

    def add_soft_constraints(self):
        """G. Soft constraints (optimization objectives)."""
        print("  Adding soft constraints (optimization objectives)...")

        # Collect all consecutive pair indicators for objective function
        # Categories:
        # 1. Prefer consecutive (weighted +3): Cal-ABBC, Group 1/2/3 AP, BC-Stats, AP Seminar
        # 2. Minimize consecutive (weighted -1): English (6 periods)
        # 3. Avoid consecutive (weighted -2): Algebra, Pre-Cal

        self.consecutive_pairs = []  # List of (indicator_var, weight) tuples

        # Category 1: Prefer consecutive (maximize)
        prefer_consecutive = ["Cal-ABBC", "Group 1 AP", "Group 2 AP", "Group 3 AP",
                              "BC-Stats", "AP Seminar"]
        for course_name in prefer_consecutive:
            for class_name, class_group in self.classes.items():
                if course_name not in class_group.courses:
                    continue
                self._add_consecutive_indicator(class_name, course_name, +3)

        # Category 2: Minimize consecutive (but allow some)
        minimize_consecutive = ["English"]
        for course_name in minimize_consecutive:
            for class_name, class_group in self.classes.items():
                if course_name not in class_group.courses:
                    continue
                self._add_consecutive_indicator(class_name, course_name, -1)

        # Category 3: Avoid consecutive (strong penalty)
        avoid_consecutive = ["Algebra", "Pre-Cal"]
        for course_name in avoid_consecutive:
            for class_name, class_group in self.classes.items():
                if course_name not in class_group.courses:
                    continue
                self._add_consecutive_indicator(class_name, course_name, -2)

        print(f"    Added {len(self.consecutive_pairs)} consecutive pair indicators for optimization")

        # Q. Soft constraint: Prefer at least 2 AP classes per day for 11th and 12th grade
        # AP classes include: Group 1 AP, Group 2 AP, Group 3 AP
        self._add_daily_ap_preference_constraint()

    def _add_daily_ap_preference_constraint(self):
        """Q. Soft constraint: Prefer at least 2 AP classes per day.
        For each day, create an indicator if the class has >= 2 AP periods.
        Maximize the sum of these indicators."""
        print("  Adding daily AP preference soft constraint...")

        ap_courses = ["Group 1 AP", "Group 2 AP", "Group 3 AP"]
        # Only 11th and 12th grade have all three AP courses
        ap_classes = ["11-A", "11-B", "12-A", "12-B"]

        self.daily_ap_indicators = []  # List of (indicator_var, weight) tuples

        for class_name in ap_classes:
            if class_name not in self.classes:
                continue

            for day in range(5):
                # Get max periods for this day
                max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)

                # Collect all AP course variables for this day
                ap_periods = []
                for course_name in ap_courses:
                    for period in range(1, max_period + 1):
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue

                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            ap_periods.append(self.schedule_vars[key])

                if len(ap_periods) >= 2:
                    # Create indicator: has_at_least_2_ap = (sum(ap_periods) >= 2)
                    has_at_least_2_ap = self.model.NewBoolVar(
                        f"has_at_least_2_ap_{class_name}_day_{day}")

                    # Use AddGreaterOrEqual to create the indicator
                    # has_at_least_2_ap = 1 if sum(ap_periods) >= 2, else 0
                    self.model.Add(sum(ap_periods) >= 2).OnlyEnforceIf(has_at_least_2_ap)
                    self.model.Add(sum(ap_periods) < 2).OnlyEnforceIf(has_at_least_2_ap.Not())

                    self.daily_ap_indicators.append((has_at_least_2_ap, 1))  # Weight +1

        print(f"    Added {len(self.daily_ap_indicators)} daily AP preference indicators")

    def _add_consecutive_indicator(self, class_name: str, course_name: str, weight: int):
        """Add indicator variables for consecutive periods with given weight."""
        for day in range(5):
            max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
            for period in range(1, max_period):
                if (day, period) in self.excluded_slots.get(class_name, set()):
                    continue
                if (day, period + 1) in self.excluded_slots.get(class_name, set()):
                    continue

                key1 = (class_name, course_name, day, period)
                key2 = (class_name, course_name, day, period + 1)

                if key1 in self.schedule_vars and key2 in self.schedule_vars:
                    # Create indicator: consecutive = var1 AND var2
                    consecutive = self.model.NewBoolVar(
                        f"consecutive_{class_name}_{course_name}_{day}_{period}")
                    self.model.AddMinEquality(consecutive,
                        [self.schedule_vars[key1], self.schedule_vars[key2]])
                    self.consecutive_pairs.append((consecutive, weight))

    def add_ap_seminar_english_sync_constraint(self):
        """H. Hard constraint: 11-A English must sync with 12-A/B AP Seminar.
        Since 12-A and 12-B have AP Seminar as a joint session, they share the same time slots.
        11-A English must be scheduled at exactly the same time."""
        print("  Adding AP Seminar/English synchronization constraint...")

        sync_count = 0
        for day, period in self.time_slots:
            # 12-A and 12-B have AP Seminar as a joint session
            # So we only need to check one of them
            ap_seminar_key = ("12-A", "AP Seminar", day, period)
            english_11a_key = ("11-A", "English", day, period)

            ap_seminar = self.schedule_vars.get(ap_seminar_key)
            english_11a = self.schedule_vars.get(english_11a_key)

            # 11-A English must equal 12-A AP Seminar (both 0 or both 1)
            if ap_seminar is not None and english_11a is not None:
                self.model.Add(english_11a == ap_seminar)
                sync_count += 1

        print(f"    Added {sync_count} AP Seminar/English sync constraints")

    def add_lucy_ap_seminar_english_conflict(self):
        """I. Lucy teacher conflict: When 12th grade has AP Seminar, 10th grade cannot have English.
        Lucy teaches AP Seminar (12-A/B) and English (10-A/B/C)."""
        print("  Adding Lucy AP Seminar/English conflict constraint...")

        conflict_count = 0
        for day, period in self.time_slots:
            # Check AP Seminar for 12-A (12-B is joint session, so same time)
            ap_seminar_key = ("12-A", "AP Seminar", day, period)
            ap_seminar = self.schedule_vars.get(ap_seminar_key)

            # Check English for 10-A, 10-B, 10-C (all taught by Lucy)
            for class_10 in ["10-A", "10-B", "10-C"]:
                english_key = (class_10, "English", day, period)
                english_10 = self.schedule_vars.get(english_key)

                if english_10 is not None and ap_seminar is not None:
                    # Lucy cannot teach both at the same time
                    self.model.Add(english_10 + ap_seminar <= 1)
                    conflict_count += 1

        print(f"    Added {conflict_count} Lucy AP Seminar/English conflict constraints")

    def add_guo_conflict_constraint(self):
        """J. Guo teacher conflict: Group 1/2 AP vs 9th grade Physics.
        Guo teaches Group 1 AP, Group 2 AP (11/12 grade) and Physics (9-A/B/C)."""
        print("  Adding Guo teacher conflict constraint...")

        conflict_count = 0
        for day, period in self.time_slots:
            # Check Group 1 AP and Group 2 AP for 11-A/B and 12-A/B
            for group_class in ["11-A", "11-B", "12-A", "12-B"]:
                group1_key = (group_class, "Group 1 AP", day, period)
                group2_key = (group_class, "Group 2 AP", day, period)

                group1 = self.schedule_vars.get(group1_key)
                group2 = self.schedule_vars.get(group2_key)

                # Check Physics for 9-A, 9-B, 9-C (all taught by Guo)
                for class_9 in ["9-A", "9-B", "9-C"]:
                    physics_key = (class_9, "Physics", day, period)
                    physics = self.schedule_vars.get(physics_key)

                    if physics is not None:
                        if group1 is not None:
                            # Guo cannot teach both Physics and Group 1 AP
                            self.model.Add(physics + group1 <= 1)
                            conflict_count += 1
                        if group2 is not None:
                            # Guo cannot teach both Physics and Group 2 AP
                            self.model.Add(physics + group2 <= 1)
                            conflict_count += 1

        print(f"    Added {conflict_count} Guo teacher conflict constraints")

    def add_darin_ap_seminar_social_constraint(self):
        """K. Darin teacher conflict: AP Seminar (12th) vs 9th grade Social.
        Darin teaches AP Seminar (12-A/B) and Social (9-A/B/C)."""
        print("  Adding Darin AP Seminar/Social conflict constraint...")

        conflict_count = 0
        for day, period in self.time_slots:
            # Check AP Seminar for 12-A and 12-B
            for class_12 in ["12-A", "12-B"]:
                ap_seminar_key = (class_12, "AP Seminar", day, period)
                ap_seminar = self.schedule_vars.get(ap_seminar_key)

                if ap_seminar is not None:
                    # Check Social for 9-A, 9-B, 9-C (all taught by Darin)
                    for class_9 in ["9-A", "9-B", "9-C"]:
                        social_key = (class_9, "Social", day, period)
                        social = self.schedule_vars.get(social_key)

                        if social is not None:
                            # Darin cannot teach both AP Seminar and Social
                            self.model.Add(ap_seminar + social <= 1)
                            conflict_count += 1

        print(f"    Added {conflict_count} Darin AP Seminar/Social conflict constraints")

    def add_english_9a_10a_sync_constraint(self):
        """L. 9-A/10-A English synchronization: When 10-A has English, 9-A must also have English.
        9-A has 6 English periods, 10-A has 5. 5 periods must be synchronized, 1 is free."""
        print("  Adding 9-A/10-A English synchronization constraint...")

        sync_count = 0
        for day, period in self.time_slots:
            english_10a_key = ("10-A", "English", day, period)
            english_9a_key = ("9-A", "English", day, period)

            english_10a = self.schedule_vars.get(english_10a_key)
            english_9a = self.schedule_vars.get(english_9a_key)

            # If 10-A has English, 9-A must also have English (10-A English => 9-A English)
            if english_10a is not None and english_9a is not None:
                self.model.AddImplication(english_10a, english_9a)
                sync_count += 1

        print(f"    Added {sync_count} 9-A/10-A English sync constraints")

    def add_english_literature_conflict_constraint(self):
        """M. English vs Literature conflict: 9-A/10-A English cannot be at the same time as 11-A/B Literature.
        LZY teaches 9-A English, Lucy teaches 10-A English, CYF teaches 11-A/B Literature."""
        print("  Adding English vs Literature conflict constraint...")

        conflict_count = 0
        for day, period in self.time_slots:
            # Check 9-A and 10-A English
            for class_9_10 in ["9-A", "10-A"]:
                english_key = (class_9_10, "English", day, period)
                english = self.schedule_vars.get(english_key)

                if english is not None:
                    # Check 11-A and 11-B Literature
                    for class_11 in ["11-A", "11-B"]:
                        literature_key = (class_11, "Literature", day, period)
                        literature = self.schedule_vars.get(literature_key)

                        if literature is not None:
                            # Cannot have both English and Literature at the same time
                            self.model.Add(english + literature <= 1)
                            conflict_count += 1

        print(f"    Added {conflict_count} English vs Literature conflict constraints")

    def add_english_ap_seminar_conflict_constraint(self):
        """N. English vs AP Seminar conflict: 9-A/10-A English cannot be at the same time as 12-A/B AP Seminar.
        LZY teaches 9-A English, Lucy teaches 10-A English and 12-A/B AP Seminar."""
        print("  Adding English vs AP Seminar conflict constraint...")

        conflict_count = 0
        for day, period in self.time_slots:
            # Check 9-A and 10-A English
            for class_9_10 in ["9-A", "10-A"]:
                english_key = (class_9_10, "English", day, period)
                english = self.schedule_vars.get(english_key)

                if english is not None:
                    # Check 12-A and 12-B AP Seminar
                    for class_12 in ["12-A", "12-B"]:
                        ap_seminar_key = (class_12, "AP Seminar", day, period)
                        ap_seminar = self.schedule_vars.get(ap_seminar_key)

                        if ap_seminar is not None:
                            # Cannot have both English and AP Seminar at the same time
                            self.model.Add(english + ap_seminar <= 1)
                            conflict_count += 1

        print(f"    Added {conflict_count} English vs AP Seminar conflict constraints")

    def add_art_group1_ap_conflict_constraint(self):
        """P. Art vs Group 1 AP conflict.
        Shiwen teaches both Art (9-A/B/C, 10-A/B/C, 11-A/B) and Group 1 AP (11-A/B, 12-A/B).
        Art and Group 1 AP cannot be scheduled at the same time."""
        print("  Adding Art vs Group 1 AP conflict constraint...")

        conflict_count = 0
        art_classes = ["9-A", "9-B", "9-C", "10-A", "10-B", "10-C", "11-A", "11-B"]
        group1_classes = ["11-A", "11-B", "12-A", "12-B"]

        for day, period in self.time_slots:
            # Check Art for all classes that have it
            for art_class in art_classes:
                art_key = (art_class, "Art", day, period)
                art = self.schedule_vars.get(art_key)

                if art is not None:
                    # Check Group 1 AP for all classes that have it
                    for group1_class in group1_classes:
                        group1_key = (group1_class, "Group 1 AP", day, period)
                        group1 = self.schedule_vars.get(group1_key)

                        if group1 is not None:
                            # Art and Group 1 AP cannot be at the same time
                            self.model.Add(art + group1 <= 1)
                            conflict_count += 1

        print(f"    Added {conflict_count} Art vs Group 1 AP conflict constraints")

    def add_group2_ap_10a_requirement_constraint(self):
        """O. Group 2 AP requires 10-A to be in Chemistry or Phys&Bio.
        When Group 2 AP is scheduled for any class (11-A, 11-B, 12-A, 12-B),
        10-A must simultaneously be in either Chemistry or Phys&Bio."""
        print("  Adding Group 2 AP / 10-A requirement constraint...")

        constraint_count = 0
        for day, period in self.time_slots:
            # For each class with Group 2 AP
            for group_class in ["11-A", "11-B", "12-A", "12-B"]:
                group2_key = (group_class, "Group 2 AP", day, period)
                group2 = self.schedule_vars.get(group2_key)

                if group2 is not None:
                    # 10-A must have Chemistry OR Phys&Bio
                    chem_key = ("10-A", "Chemistry", day, period)
                    physbio_key = ("10-A", "Phys&Bio", day, period)

                    chem = self.schedule_vars.get(chem_key)
                    physbio = self.schedule_vars.get(physbio_key)

                    # Group 2 AP implies (Chemistry OR Phys&Bio)
                    # Using AddBoolOr with OnlyEnforceIf for the implication
                    if chem is not None and physbio is not None:
                        # Both Chemistry and Phys&Bio are possible at this time
                        self.model.AddBoolOr([chem, physbio]).OnlyEnforceIf(group2)
                        constraint_count += 1
                    elif chem is not None:
                        # Only Chemistry is possible, Group 2 AP implies Chemistry
                        self.model.AddImplication(group2, chem)
                        constraint_count += 1
                    elif physbio is not None:
                        # Only Phys&Bio is possible, Group 2 AP implies Phys&Bio
                        self.model.AddImplication(group2, physbio)
                        constraint_count += 1

        print(f"    Added {constraint_count} Group 2 AP / 10-A requirement constraints")

    def add_9th_grade_daily_limits_constraint(self):
        """R. 9th grade daily course limits.
        - English: exactly 1 day with 2 periods, other days max 1
        - Art: at most 1 day with 2 periods (consecutive preferred), other days max 1
        - Other courses: max 1 period per day
        """
        print("  Adding 9th grade daily limits constraint...")

        ninth_grade_classes = ["9-A", "9-B", "9-C"]
        special_courses = ["English", "Art"]  # These can have 2 periods on at most 1 day
        other_courses = ["Algebra", "Social", "Psychology", "Physics", "Chemistry", "Biology", "Geography", "PE"]

        constraint_count = 0

        for class_name in ninth_grade_classes:
            if class_name not in self.classes:
                continue

            # For English: exactly 1 day with 2 periods, other days max 1
            # For Art: at most 1 day with 2 periods, other days max 1
            for course_name in special_courses:
                if course_name not in self.classes[class_name].courses:
                    continue

                # Collect day period counts
                day_periods = {}
                for day in range(5):
                    max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                    day_periods[day] = []
                    for period in range(1, max_period + 1):
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue
                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            day_periods[day].append(self.schedule_vars[key])

                # For each day, limit to max 2 periods
                for day, periods in day_periods.items():
                    if periods:
                        self.model.Add(sum(periods) <= 2)

                # Create indicator for each day: has_2_periods = (sum == 2)
                has_2_days = []
                for day, periods in day_periods.items():
                    if len(periods) >= 2:
                        has_2 = self.model.NewBoolVar(f"{class_name}_{course_name}_day_{day}_has_2")
                        # has_2 = 1 iff sum(periods) == 2
                        self.model.Add(sum(periods) == 2).OnlyEnforceIf(has_2)
                        self.model.Add(sum(periods) != 2).OnlyEnforceIf(has_2.Not())
                        has_2_days.append(has_2)
                    elif periods:
                        # If less than 2 periods possible, create a fixed False indicator
                        has_2 = self.model.NewBoolVar(f"{class_name}_{course_name}_day_{day}_has_2")
                        self.model.Add(has_2 == 0)
                        has_2_days.append(has_2)

                # English: exactly 1 day with 2 periods (6 periods total = 2+1+1+1+1)
                if course_name == "English" and has_2_days:
                    self.model.Add(sum(has_2_days) == 1)
                    constraint_count += 1

                # Art: at most 1 day with 2 periods (2 periods total = 2 or 1+1)
                if course_name == "Art" and has_2_days:
                    self.model.Add(sum(has_2_days) <= 1)
                    constraint_count += 1

            # For other courses: max 1 period per day
            for course_name in other_courses:
                if course_name not in self.classes[class_name].courses:
                    continue

                for day in range(5):
                    max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                    day_periods = []
                    for period in range(1, max_period + 1):
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue
                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            day_periods.append(self.schedule_vars[key])

                    if day_periods:
                        self.model.Add(sum(day_periods) <= 1)
                        constraint_count += 1

        print(f"    Added {constraint_count} 9th grade daily limit constraints")

    def add_10th_grade_daily_limits_constraint(self):
        """S. 10th grade daily course limits.
        - Art: at most 1 day with 2 periods (consecutive preferred), other days max 1
        - Other courses: max 1 period per day
        """
        print("  Adding 10th grade daily limits constraint...")

        tenth_grade_classes = ["10-A", "10-B", "10-C"]
        special_courses = ["Art"]  # Can have 2 periods on at most 1 day
        other_courses = ["English", "World History", "Psych&Geo", "Spanish", "Pre-Cal",
                         "Micro-Econ", "Chemistry", "Phys&Bio", "PE"]

        constraint_count = 0

        for class_name in tenth_grade_classes:
            if class_name not in self.classes:
                continue

            # For Art: at most 1 day with 2 periods, other days max 1
            for course_name in special_courses:
                if course_name not in self.classes[class_name].courses:
                    continue

                # Collect day period counts
                day_periods = {}
                for day in range(5):
                    max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                    day_periods[day] = []
                    for period in range(1, max_period + 1):
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue
                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            day_periods[day].append(self.schedule_vars[key])

                # For each day, limit to max 2 periods
                for day, periods in day_periods.items():
                    if periods:
                        self.model.Add(sum(periods) <= 2)

                # Create indicator for each day: has_2_periods = (sum == 2)
                has_2_days = []
                for day, periods in day_periods.items():
                    if len(periods) >= 2:
                        has_2 = self.model.NewBoolVar(f"{class_name}_{course_name}_day_{day}_has_2")
                        # has_2 = 1 iff sum(periods) == 2
                        self.model.Add(sum(periods) == 2).OnlyEnforceIf(has_2)
                        self.model.Add(sum(periods) != 2).OnlyEnforceIf(has_2.Not())
                        has_2_days.append(has_2)
                    elif periods:
                        # If less than 2 periods possible, create a fixed False indicator
                        has_2 = self.model.NewBoolVar(f"{class_name}_{course_name}_day_{day}_has_2")
                        self.model.Add(has_2 == 0)
                        has_2_days.append(has_2)

                # Art: at most 1 day with 2 periods (2 periods total = 2 or 1+1)
                if has_2_days:
                    self.model.Add(sum(has_2_days) <= 1)
                    constraint_count += 1

            # For other courses: max 1 period per day
            for course_name in other_courses:
                if course_name not in self.classes[class_name].courses:
                    continue

                for day in range(5):
                    max_period = 6 if day in [0, 3] else (8 if day in [1, 2] else 7)
                    day_periods = []
                    for period in range(1, max_period + 1):
                        if (day, period) in self.excluded_slots.get(class_name, set()):
                            continue
                        key = (class_name, course_name, day, period)
                        if key in self.schedule_vars:
                            day_periods.append(self.schedule_vars[key])

                    if day_periods:
                        self.model.Add(sum(day_periods) <= 1)
                        constraint_count += 1

        print(f"    Added {constraint_count} 10th grade daily limit constraints")
