"""
Data configuration for the high school scheduling system.
Contains all classes, courses, teachers, and constraints.
"""
from typing import Dict, List, Set
from src.models import ClassGroup, Course, JointSession, TimeSlot


def get_time_slots() -> List[tuple]:
    """Get all time slots as (day, period) tuples."""
    slots = []
    # Monday: 6 periods
    for p in range(1, 7):
        slots.append((0, p))
    # Tuesday: 8 periods
    for p in range(1, 9):
        slots.append((1, p))
    # Wednesday: 8 periods
    for p in range(1, 9):
        slots.append((2, p))
    # Thursday: 6 periods
    for p in range(1, 7):
        slots.append((3, p))
    # Friday: 7 periods
    for p in range(1, 8):
        slots.append((4, p))
    return slots


def get_class_groups() -> Dict[str, ClassGroup]:
    """
    Define all class groups with their courses.
    Returns a dictionary mapping class name to ClassGroup object.
    """
    classes = {}

    # ========================================
    # 9th Grade Classes (33 periods each)
    # ========================================

    # 9-A
    classes["9-A"] = ClassGroup(name="9-A", grade=9)
    classes["9-A"].add_course(Course("English", 6, "LZY"))
    classes["9-A"].add_course(Course("Algebra", 5, "Yuhan"))
    classes["9-A"].add_course(Course("Social", 4, "Darin"))
    classes["9-A"].add_course(Course("Psychology", 3, "Chloe"))
    classes["9-A"].add_course(Course("Physics", 3, "Guo"))
    classes["9-A"].add_course(Course("Chemistry", 3, "Shao"))
    classes["9-A"].add_course(Course("Biology", 3, "Zhao"))
    classes["9-A"].add_course(Course("Geography", 2, "Manuel"))
    classes["9-A"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["9-A"].add_course(Course("PE", 2, "Wen"))

    # 9-B
    classes["9-B"] = ClassGroup(name="9-B", grade=9)
    classes["9-B"].add_course(Course("English", 6, "CYF"))
    classes["9-B"].add_course(Course("Algebra", 5, "Yuhan"))
    classes["9-B"].add_course(Course("Social", 4, "Darin"))
    classes["9-B"].add_course(Course("Psychology", 3, "Chloe"))
    classes["9-B"].add_course(Course("Physics", 3, "Guo"))
    classes["9-B"].add_course(Course("Chemistry", 3, "Shao"))
    classes["9-B"].add_course(Course("Biology", 3, "Zhao"))
    classes["9-B"].add_course(Course("Geography", 2, "Manuel"))
    classes["9-B"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["9-B"].add_course(Course("PE", 2, "Wen"))

    # 9-C (NEW)
    classes["9-C"] = ClassGroup(name="9-C", grade=9)
    classes["9-C"].add_course(Course("English", 6, "Ezio"))
    classes["9-C"].add_course(Course("Algebra", 5, "Yuhan"))
    classes["9-C"].add_course(Course("Social", 4, "Darin"))
    classes["9-C"].add_course(Course("Psychology", 3, "Chloe"))
    classes["9-C"].add_course(Course("Physics", 3, "Guo"))
    classes["9-C"].add_course(Course("Chemistry", 3, "Shao"))
    classes["9-C"].add_course(Course("Biology", 3, "Zhao"))
    classes["9-C"].add_course(Course("Geography", 2, "Manuel"))
    classes["9-C"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["9-C"].add_course(Course("PE", 2, "Wen"))

    # ========================================
    # 10th Grade Classes (33 periods each)
    # ========================================

    # 10-A
    classes["10-A"] = ClassGroup(name="10-A", grade=10)
    classes["10-A"].add_course(Course("English", 5, "Lucy"))
    classes["10-A"].add_course(Course("World History", 3, "Neil"))
    classes["10-A"].add_course(Course("Psych&Geo", 3, "Chloe,Manuel"))
    classes["10-A"].add_course(Course("Spanish", 2, "AK"))
    classes["10-A"].add_course(Course("Pre-Cal", 5, "Dan"))
    classes["10-A"].add_course(Course("Micro-Econ", 5, "Neil"))
    classes["10-A"].add_course(Course("Chemistry", 3, "Shao"))
    classes["10-A"].add_course(Course("Phys&Bio", 3, "Song"))
    classes["10-A"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["10-A"].add_course(Course("PE", 2, "Wen"))

    # 10-B
    classes["10-B"] = ClassGroup(name="10-B", grade=10)
    classes["10-B"].add_course(Course("English", 5, "Lucy"))
    classes["10-B"].add_course(Course("World History", 3, "Neil"))
    classes["10-B"].add_course(Course("Psych&Geo", 3, "Chloe,Manuel"))
    classes["10-B"].add_course(Course("Spanish", 2, "AK"))
    classes["10-B"].add_course(Course("Pre-Cal", 5, "Dan"))
    classes["10-B"].add_course(Course("Micro-Econ", 5, "Neil"))
    classes["10-B"].add_course(Course("Chemistry", 3, "Shao"))
    classes["10-B"].add_course(Course("Phys&Bio", 3, "Song"))
    classes["10-B"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["10-B"].add_course(Course("PE", 2, "Wen"))

    # 10-C
    classes["10-C"] = ClassGroup(name="10-C", grade=10)
    classes["10-C"].add_course(Course("English", 5, "Lucy"))
    classes["10-C"].add_course(Course("World History", 3, "Neil"))
    classes["10-C"].add_course(Course("Psych&Geo", 3, "Chloe,Manuel"))
    classes["10-C"].add_course(Course("Spanish", 2, "AK"))
    classes["10-C"].add_course(Course("Pre-Cal", 5, "Dan"))
    classes["10-C"].add_course(Course("Micro-Econ", 5, "Neil"))
    classes["10-C"].add_course(Course("Chemistry", 3, "Shao"))
    classes["10-C"].add_course(Course("Phys&Bio", 3, "Zhao"))
    classes["10-C"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["10-C"].add_course(Course("PE", 2, "Wen"))

    # 10-EAL-A (Ezio - 3 periods with Psych&Geo)
    classes["10-EAL-A"] = ClassGroup(name="10-EAL-A", grade=10)
    classes["10-EAL-A"].add_course(Course("EAL", 3, "Ezio"))

    # 10-EAL-B (CYF - 3 periods with Psych&Geo)
    classes["10-EAL-B"] = ClassGroup(name="10-EAL-B", grade=10)
    classes["10-EAL-B"].add_course(Course("EAL", 3, "CYF"))

    # 10-EAL-C (LZY - 6 periods total)
    classes["10-EAL-C"] = ClassGroup(name="10-EAL-C", grade=10)
    classes["10-EAL-C"].add_course(Course("EAL", 6, "LZY"))

    # ========================================
    # 11th Grade Classes
    # ========================================

    # 11-A
    classes["11-A"] = ClassGroup(name="11-A", grade=11)
    classes["11-A"].add_course(Course("English", 5, "CYF"))
    classes["11-A"].add_course(Course("Literature", 3, "CYF"))
    classes["11-A"].add_course(Course("Spanish", 3, "AK"))
    classes["11-A"].add_course(Course("Cal-ABBC", 5, "Yan,Song"))
    classes["11-A"].add_course(Course("Group 1 AP", 5, "Guo,Zhao,Shiwen"))
    classes["11-A"].add_course(Course("Group 2 AP", 5, "Neil,Guo"))
    classes["11-A"].add_course(Course("Group 3 AP", 5, "Chloe,Manuel"))
    classes["11-A"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["11-A"].add_course(Course("PE", 2, "Wen"))

    # 11-B
    classes["11-B"] = ClassGroup(name="11-B", grade=11)
    classes["11-B"].add_course(Course("English", 5, "CYF"))
    classes["11-B"].add_course(Course("Literature", 3, "CYF"))
    classes["11-B"].add_course(Course("Spanish", 3, "AK"))
    classes["11-B"].add_course(Course("Cal-ABBC", 5, "Yan"))
    classes["11-B"].add_course(Course("Group 1 AP", 5, "Guo,Zhao,Shiwen"))
    classes["11-B"].add_course(Course("Group 2 AP", 5, "Neil,Guo"))
    classes["11-B"].add_course(Course("Group 3 AP", 5, "Chloe,Manuel"))
    classes["11-B"].add_course(Course("Art", 2, "Shiwen", prefer_consecutive=True))
    classes["11-B"].add_course(Course("PE", 2, "Wen"))

    # ========================================
    # 12th Grade Classes
    # ========================================

    # 12-A
    classes["12-A"] = ClassGroup(name="12-A", grade=12)
    classes["12-A"].add_course(Course("Spanish", 3, "AK"))
    classes["12-A"].add_course(Course("BC-Stats", 5, "Yan"))
    classes["12-A"].add_course(Course("AP Seminar", 5, "Ezio,Lucy,Darin"))  # Lucy also teaches 10th grade English, Darin teaches 9th Social
    classes["12-A"].add_course(Course("Group 1 AP", 5, "Guo,Zhao,Shiwen"))
    classes["12-A"].add_course(Course("Group 2 AP", 5, "Neil,Guo"))
    classes["12-A"].add_course(Course("Group 3 AP", 5, "Chloe,Manuel"))
    classes["12-A"].add_course(Course("PE", 2, "Wen"))
    classes["12-A"].add_course(Course("Counseling", 1, "Wen"))

    # 12-B
    classes["12-B"] = ClassGroup(name="12-B", grade=12)
    classes["12-B"].add_course(Course("Spanish", 3, "AK"))
    classes["12-B"].add_course(Course("BC-Stats", 5, "Yuhan"))
    classes["12-B"].add_course(Course("AP Seminar", 5, "Ezio,Lucy,Darin"))  # Lucy also teaches 10th grade English, Darin teaches 9th Social
    classes["12-B"].add_course(Course("Group 1 AP", 5, "Guo,Zhao,Shiwen"))
    classes["12-B"].add_course(Course("Group 2 AP", 5, "Neil,Guo"))
    classes["12-B"].add_course(Course("Group 3 AP", 5, "Chloe,Manuel"))
    classes["12-B"].add_course(Course("PE", 2, "Wen"))
    classes["12-B"].add_course(Course("Counseling", 1, "Wen"))

    return classes


def get_joint_sessions() -> List[JointSession]:
    """
    Define all joint sessions where classes must attend simultaneously.
    These sessions don't count as teacher conflicts.
    """
    sessions = []

    # 9th Grade English - 3 classes must attend simultaneously
    sessions.append(JointSession(
        classes=["9-A", "9-B", "9-C"],
        course_name="English",
        teachers=["LZY", "CYF", "Ezio"]
    ))

    # 10th Grade Psych&Geo - all 3 classes must attend simultaneously
    sessions.append(JointSession(
        classes=["10-A", "10-B", "10-C"],
        course_name="Psych&Geo",
        teachers=["Chloe,Manuel", "Chloe,Manuel", "Chloe,Manuel"]
    ))

    # 10th Grade Phys&Bio - 10-A and 10-C must attend simultaneously
    sessions.append(JointSession(
        classes=["10-A", "10-C"],
        course_name="Phys&Bio",
        teachers=["Song", "Zhao"]
    ))

    # Note: EAL classes are synchronized with Psych&Geo
    # When 10-A, 10-B, 10-C have Psych&Geo (3 periods/week),
    # 10-EAL-A, 10-EAL-B, 10-EAL-C have EAL at the same time
    # 10-EAL-C has 3 additional EAL periods (not synchronized)
    # This is handled in constraints.py with special logic

    # 12th Grade BC-Statistics - both classes must attend simultaneously
    sessions.append(JointSession(
        classes=["12-A", "12-B"],
        course_name="BC-Stats",
        teachers=["Yan", "Yuhan"]
    ))

    # 12th Grade AP Seminar/Composition - both classes must attend simultaneously
    # Teachers: Ezio, Lucy, and Darin (Lucy also teaches 10th grade English, Darin teaches 9th Social)
    sessions.append(JointSession(
        classes=["12-A", "12-B"],
        course_name="AP Seminar",
        teachers=["Ezio,Lucy,Darin", "Ezio,Lucy,Darin"]
    ))

    # Group 1/2/3 AP - 11-A, 11-B, 12-A, 12-B must attend simultaneously
    sessions.append(JointSession(
        classes=["11-A", "11-B", "12-A", "12-B"],
        course_name="Group 1 AP",
        teachers=["Guo,Zhao,Shiwen", "Guo,Zhao,Shiwen", "Guo,Zhao,Shiwen", "Guo,Zhao,Shiwen"]
    ))

    sessions.append(JointSession(
        classes=["11-A", "11-B", "12-A", "12-B"],
        course_name="Group 2 AP",
        teachers=["Neil,Guo", "Neil,Guo", "Neil,Guo", "Neil,Guo"]
    ))

    sessions.append(JointSession(
        classes=["11-A", "11-B", "12-A", "12-B"],
        course_name="Group 3 AP",
        teachers=["Chloe,Manuel", "Chloe,Manuel", "Chloe,Manuel", "Chloe,Manuel"]
    ))

    return sessions


def get_excluded_time_slots() -> Dict[str, Set[tuple]]:
    """
    Define time slots that are excluded for specific classes.
    Returns a dictionary mapping class name to set of (day, period) tuples.
    """
    excluded = {}

    # 9th and 10th grade: Tuesday periods 7-8 are excluded
    # Including EAL classes (10-EAL-A, 10-EAL-B, 10-EAL-C)
    for class_name in ["9-A", "9-B", "9-C", "10-A", "10-B", "10-C", "10-EAL-A", "10-EAL-B", "10-EAL-C"]:
        excluded[class_name] = {(1, 7), (1, 8)}

    # 12th grade: Friday period 7 is excluded
    excluded["12-A"] = excluded.get("12-A", set()) | {(4, 7)}
    excluded["12-B"] = excluded.get("12-B", set()) | {(4, 7)}

    return excluded


def get_required_time_slots() -> Dict[str, Dict[tuple, str]]:
    """
    Define time slots that are required for specific courses.
    Returns a dictionary mapping class name to {(day, period): course_name}.
    """
    required = {}

    # 12th grade: Tuesday periods 7-8 are PE and Counseling
    required["12-A"] = {(1, 7): "PE", (1, 8): "Counseling"}
    required["12-B"] = {(1, 7): "PE", (1, 8): "Counseling"}

    return required


def get_teacher_course_conflicts() -> Dict[str, Set[tuple]]:
    """
    Define course pairs that cannot be taught simultaneously by the same teacher.
    Returns a dictionary mapping teacher to set of (course1, course2) tuples.
    """
    conflicts = {}

    # Yuhan: 9th grade Algebra - no conflicts with himself
    # Darin: 9th grade Social - no conflicts with himself

    # Chloe: 9th grade Psychology, 10th grade Psych&Geo - can conflict
    # (students are different, so it's allowed)

    # Guo: 9th grade Physics, 10th grade Phys&Bio - can conflict

    # Shao: 9th grade Chemistry, 10th grade Chemistry - can conflict

    # Zhao: 9th grade Biology, 11/12th grade Group 3 AP - can conflict

    # Shiwen: Art (全校) - cannot have two Art classes simultaneously
    # But since Art is taught by the same teacher to all classes, we need to avoid conflicts

    # Wen: PE (全校) - cannot have two PE classes simultaneously
    # But since PE is taught by the same teacher to all classes, we need to avoid conflicts

    return conflicts


def get_course_time_constraints() -> Dict[str, List[tuple]]:
    """
    Define specific time constraints for certain courses.
    Returns a dictionary mapping course pattern to constraints.
    """
    constraints = {}

    # Group 1 AP: Mon 2 periods, Thu 1 period, Fri 2 periods
    constraints["Group 1 AP"] = [(0, 5), (0, 6)]  # Avoid Mon periods 5-6

    # Group 1 AP preferred time slots (soft constraint)
    # Monday: 2 periods (periods 1-4 or 5-6 but avoiding 5-6)
    # Thursday: 1 period
    # Friday: 2 periods

    return constraints


def get_preferred_consecutive_courses() -> Set[str]:
    """
    Define courses that should preferably be scheduled as consecutive periods.
    5-period courses should be arranged as 2+2+1 (two doubles + single).
    """
    return {
        "Cal-ABBC",
        "BC-Stats",
        "Group 1 AP",
        "Group 2 AP",
        "Group 3 AP",
        "Art",  # 2 periods, prefer consecutive
    }


def get_teacher_for_course(class_name: str, course_name: str, classes: Dict[str, ClassGroup]) -> str:
    """Get the teacher for a specific course in a specific class."""
    if class_name in classes and course_name in classes[class_name].courses:
        return classes[class_name].courses[course_name].teacher
    return None


def is_joint_session(class_names: List[str], joint_sessions: List[JointSession]) -> bool:
    """Check if a set of classes forms a joint session."""
    for session in joint_sessions:
        if set(class_names) == set(session.classes):
            return True
    return False


def get_joint_session_for_classes(class_names: List[str], joint_sessions: List[JointSession]) -> JointSession:
    """Get the joint session for a set of classes."""
    for session in joint_sessions:
        if set(class_names).issubset(set(session.classes)):
            return session
    return None


def get_period_names() -> Dict[int, str]:
    """Get period names for each day."""
    return {
        0: ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6"],
        1: ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7", "Period 8"],
        2: ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7", "Period 8"],
        3: ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6"],
        4: ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5", "Period 6", "Period 7"],
    }


def get_day_names() -> List[str]:
    """Get day names."""
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
