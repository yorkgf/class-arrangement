import pandas as pd

df = pd.read_csv('output/global_schedule.csv')

print('=' * 80)
print('CONSTRAINT VERIFICATION')
print('=' * 80)

# Check E3: EAL synchronized with Psych&Geo
print()
print('E3: EAL synchronized with Psych&Geo')
print('-' * 60)
violations = []
for class_name, eal_class in [('10-A', '10-EAL-A'), ('10-B', '10-EAL-B'), ('10-C', '10-EAL-C')]:
    psych = df[(df['Class'] == class_name) & (df['Course'] == 'Psych&Geo')][['Day', 'Period']].values.tolist()
    eal = df[(df['Class'] == eal_class) & (df['Course'] == 'EAL')][['Day', 'Period']].values.tolist()
    psych_set = set(tuple(x) for x in psych)
    eal_set = set(tuple(x) for x in eal)
    if not psych_set.issubset(eal_set):
        missing = psych_set - eal_set
        for day, period in missing:
            violations.append(f'  {class_name} has Psych&Geo but {eal_class} has no EAL at {day} period {period}')

if violations:
    print('VIOLATIONS:')
    for v in violations:
        print(v)
else:
    print('  [OK] All E3 constraints satisfied')

# Check E4: 10-EAL-C has exactly 3 overlaps with Phys&Bio
print()
print('E4: 10-EAL-C overlaps with 10-A/10-C Phys&Bio')
print('-' * 60)
ealc = df[(df['Class'] == '10-EAL-C') & (df['Course'] == 'EAL')][['Day', 'Period']].values.tolist()
phys_a = df[(df['Class'] == '10-A') & (df['Course'] == 'Phys&Bio')][['Day', 'Period']].values.tolist()
phys_c = df[(df['Class'] == '10-C') & (df['Course'] == 'Phys&Bio')][['Day', 'Period']].values.tolist()

ealc_set = set(tuple(x) for x in ealc)
phys_a_set = set(tuple(x) for x in phys_a)
phys_c_set = set(tuple(x) for x in phys_c)
overlaps = ealc_set & (phys_a_set | phys_c_set)
print(f'  Found {len(overlaps)} overlaps: {sorted(overlaps)}')
e4_ok = len(overlaps) == 3
if not e4_ok:
    print(f'  [VIOLATION] Expected 3 overlaps, found {len(overlaps)}')
else:
    print('  [OK] E4 constraint satisfied')

# Check teacher conflicts
print()
print('Teacher Conflicts')
print('-' * 60)
schedule = {}
for _, row in df.iterrows():
    key = (row['Teacher'], row['Day'], row['Period'])
    if key not in schedule:
        schedule[key] = []
    schedule[key].append((row['Class'], row['Course']))

teacher_violations = []
for (teacher, day, period), classes in schedule.items():
    if len(classes) > 1:
        # Check if this is a joint session
        course_names = [c[1] for c in classes]
        is_joint = False
        if len(set(course_names)) == 1 and len(classes) > 1:
            # Same course, check if joint session
            class_names = [c[0] for c in classes]
            # Check official joint sessions
            if '9-A' in class_names and '9-B' in class_names and '9-C' in class_names and course_names[0] == 'English':
                is_joint = True
            elif '10-A' in class_names and '10-B' in class_names and '10-C' in class_names and course_names[0] == 'Psych&Geo':
                is_joint = True
            elif '12-A' in class_names and '12-B' in class_names and course_names[0] in ['BC-Stats', 'AP Seminar']:
                is_joint = True
            elif all(c in ['11-A', '11-B', '12-A', '12-B'] for c in class_names) and course_names[0].startswith('Group'):
                is_joint = True

        if not is_joint and teacher not in ['Shiwen', 'Wen']:
            teacher_violations.append(f'  {teacher} at {day} period {period}: {classes}')

if teacher_violations:
    print('VIOLATIONS:')
    for v in teacher_violations[:10]:
        print(v)
    if len(teacher_violations) > 10:
        print(f'  ... and {len(teacher_violations) - 10} more')
else:
    print('  [OK] No teacher conflicts')

# Check course period counts
print()
print('Course Period Counts')
print('-' * 60)
class_courses = {}
for _, row in df.iterrows():
    key = (row['Class'], row['Course'])
    if key not in class_courses:
        class_courses[key] = 0
    class_courses[key] += 1

# Expected periods (from data)
expected = {
    '9-A': {'English': 6, 'Algebra': 5, 'Social': 4, 'Psychology': 3, 'Physics': 3, 'Chemistry': 3, 'Biology': 3, 'Geography': 2, 'Art': 2, 'PE': 2},
    '9-B': {'English': 6, 'Algebra': 5, 'Social': 4, 'Psychology': 3, 'Physics': 3, 'Chemistry': 3, 'Biology': 3, 'Geography': 2, 'Art': 2, 'PE': 2},
    '9-C': {'English': 6, 'Algebra': 5, 'Social': 4, 'Psychology': 3, 'Physics': 3, 'Chemistry': 3, 'Biology': 3, 'Geography': 2, 'Art': 2, 'PE': 2},
    '10-A': {'English': 5, 'World History': 3, 'Psych&Geo': 3, 'Spanish': 2, 'Pre-Cal': 5, 'Micro-Econ': 5, 'Chemistry': 3, 'Phys&Bio': 3, 'Art': 2, 'PE': 2},
    '10-B': {'English': 5, 'World History': 3, 'Psych&Geo': 3, 'Spanish': 2, 'Pre-Cal': 5, 'Micro-Econ': 5, 'Chemistry': 3, 'Phys&Bio': 3, 'Art': 2, 'PE': 2},
    '10-C': {'English': 5, 'World History': 3, 'Psych&Geo': 3, 'Spanish': 2, 'Pre-Cal': 5, 'Micro-Econ': 5, 'Chemistry': 3, 'Phys&Bio': 3, 'Art': 2, 'PE': 2},
    '10-EAL-A': {'EAL': 3},
    '10-EAL-B': {'EAL': 3},
    '10-EAL-C': {'EAL': 6},
    '11-A': {'English': 5, 'Literature': 3, 'Spanish': 3, 'Cal-ABBC': 5, 'Group 1 AP': 5, 'Group 2 AP': 5, 'Group 3 AP': 5, 'Art': 2, 'PE': 2},
    '11-B': {'English': 5, 'Literature': 3, 'Spanish': 3, 'Cal-ABBC': 5, 'Group 1 AP': 5, 'Group 2 AP': 5, 'Group 3 AP': 5, 'Art': 2, 'PE': 2},
    '12-A': {'Spanish': 3, 'BC-Stats': 5, 'AP Seminar': 5, 'Group 1 AP': 5, 'Group 2 AP': 5, 'Group 3 AP': 5, 'PE': 2, 'Counseling': 1},
    '12-B': {'Spanish': 3, 'BC-Stats': 5, 'AP Seminar': 5, 'Group 1 AP': 5, 'Group 2 AP': 5, 'Group 3 AP': 5, 'PE': 2, 'Counseling': 1},
}

count_violations = []
for cls, courses in expected.items():
    for course, exp_count in courses.items():
        actual = class_courses.get((cls, course), 0)
        if actual != exp_count:
            count_violations.append(f'  {cls} {course}: expected {exp_count}, got {actual}')

if count_violations:
    print('VIOLATIONS:')
    for v in count_violations[:5]:
        print(v)
    if len(count_violations) > 5:
        print(f'  ... and {len(count_violations) - 5} more')
else:
    print('  [OK] All course period counts correct')

# Check joint sessions
print()
print('Joint Sessions')
print('-' * 60)
joint_sessions = [
    ('English', ['9-A', '9-B', '9-C']),
    ('Psych&Geo', ['10-A', '10-B', '10-C']),
    ('Phys&Bio', ['10-A', '10-C']),
    ('BC-Stats', ['12-A', '12-B']),
    ('AP Seminar', ['12-A', '12-B']),
    ('Group 1 AP', ['11-A', '11-B', '12-A', '12-B']),
    ('Group 2 AP', ['11-A', '11-B', '12-A', '12-B']),
    ('Group 3 AP', ['11-A', '11-B', '12-A', '12-B']),
]

joint_violations = []
for course, classes in joint_sessions:
    for day in df['Day'].unique():
        for period in df[df['Day'] == day]['Period'].unique():
            scheduled = []
            for cls in classes:
                if len(df[(df['Class'] == cls) & (df['Course'] == course) & (df['Day'] == day) & (df['Period'] == period)]) > 0:
                    scheduled.append(cls)
            if scheduled and len(scheduled) != len(classes):
                joint_violations.append(f'  {course} at {day} period {period}: only {scheduled} of {classes}')

if joint_violations:
    print('VIOLATIONS:')
    for v in joint_violations[:5]:
        print(v)
    if len(joint_violations) > 5:
        print(f'  ... and {len(joint_violations) - 5} more')
else:
    print('  [OK] All joint sessions synchronized')

print()
print('=' * 80)
print('SUMMARY')
print('=' * 80)
all_violations = violations + (['E4'] if not e4_ok else []) + teacher_violations + count_violations + joint_violations
if all_violations:
    print(f'Total violations found: {len(all_violations)}')
else:
    print('No violations found. Solution is valid!')
