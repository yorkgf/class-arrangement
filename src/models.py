"""
Data models for the class scheduling system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass
class TimeSlot:
    """Represents a time slot in the weekly schedule."""
    day: int  # 0=Monday, 1=Tuesday, ..., 4=Friday
    period: int  # 1-indexed period number
    name: str = ""

    def __str__(self) -> str:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        return f"{days[self.day]}-{self.period}"

    def __hash__(self) -> int:
        return hash((self.day, self.period))

    def __eq__(self, other) -> bool:
        if not isinstance(other, TimeSlot):
            return False
        return self.day == other.day and self.period == other.period


@dataclass
class Course:
    """Represents a course offered to a class."""
    name: str
    periods_per_week: int
    teacher: str  # Can be a single teacher or comma-separated list (e.g., "Yan" or "Yan,Song")
    prefer_consecutive: bool = False  # For soft constraint: prefer consecutive periods

    def get_teachers(self) -> List[str]:
        """Get list of teachers for this course."""
        if ',' in self.teacher:
            return [t.strip() for t in self.teacher.split(',')]
        return [self.teacher]

    def __hash__(self) -> int:
        return hash((self.name, self.teacher))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Course):
            return False
        return self.name == other.name and self.teacher == other.teacher


@dataclass
class ClassGroup:
    """Represents a class group (e.g., 9-A, 10-B)."""
    name: str  # e.g., "9-A", "10-B", "12-EAL-A"
    grade: int  # 9, 10, 11, or 12
    courses: Dict[str, Course] = field(default_factory=dict)  # course_name -> Course
    excluded_time_slots: Set[TimeSlot] = field(default_factory=set)

    def add_course(self, course: Course):
        """Add a course to this class."""
        self.courses[course.name] = course

    def get_course(self, course_name: str) -> Optional[Course]:
        """Get a course by name."""
        return self.courses.get(course_name)

    def total_periods(self) -> int:
        """Calculate total periods needed per week."""
        return sum(c.periods_per_week for c in self.courses.values())

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ClassGroup):
            return False
        return self.name == other.name


@dataclass
class JointSession:
    """Represents a joint session where multiple classes must attend simultaneously."""
    classes: List[str]  # List of class names that must attend together
    course_name: str  # The course name for this joint session
    teachers: List[str]  # The teachers for each class (one per class)

    def __hash__(self) -> int:
        return hash((tuple(sorted(self.classes)), self.course_name))

    def __eq__(self, other) -> bool:
        if not isinstance(other, JointSession):
            return False
        return (tuple(sorted(self.classes)) == tuple(sorted(other.classes)) and
                self.course_name == other.course_name)


@dataclass
class TeacherConflict:
    """Represents courses that cannot be taught simultaneously by the same teacher."""
    teacher: str
    course1: str  # First course name pattern
    course2: str  # Second course name pattern


@dataclass
class ScheduleConfig:
    """Configuration for the weekly schedule."""
    # Periods per day: Mon=6, Tue=8, Wed=8, Thu=6, Fri=7
    periods_per_day: Dict[int, int] = field(default_factory=lambda: {
        0: 6,  # Monday
        1: 8,  # Tuesday
        2: 8,  # Wednesday
        3: 6,  # Thursday
        4: 7,  # Friday
    })

    def total_slots(self) -> int:
        """Calculate total time slots in a week."""
        return sum(self.periods_per_day.values())

    def get_slot_index(self, day: int, period: int) -> int:
        """Get the linear index of a time slot."""
        index = 0
        for d in range(day):
            index += self.periods_per_day[d]
        index += period - 1
        return index

    def get_day_period(self, slot_index: int) -> tuple:
        """Get day and period from slot index."""
        for day in range(5):
            if slot_index < self.periods_per_day[day]:
                return day, slot_index + 1
            slot_index -= self.periods_per_day[day]
        return None, None

    def is_valid_slot(self, day: int, period: int) -> bool:
        """Check if a day/period combination is valid."""
        if day < 0 or day > 4:
            return False
        if period < 1 or period > self.periods_per_day[day]:
            return False
        return True


# Special time slot constraints
@dataclass
class TimeSlotConstraint:
    """Represents a constraint on specific time slots."""
    day: int
    period: int
    constraint_type: str  # "excluded", "required", "prefer_consecutive"
    classes: List[str] = field(default_factory=list)
    courses: List[str] = field(default_factory=list)
