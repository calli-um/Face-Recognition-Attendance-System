import csv
import os
from datetime import date, datetime, timedelta

CSV_PATH = "data/attendance.csv"


def init_csv(student_name):
    """Initialize CSV file with headers"""
    if not os.path.exists(CSV_PATH):
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Section", student_name])


def add_student_column(student_name):
    """Add a new student column to the CSV"""
    if not os.path.exists(CSV_PATH):
        init_csv(student_name)
        return

    with open(CSV_PATH, "r") as f:
        rows = list(csv.reader(f))

    if not rows:
        init_csv(student_name)
        return

    # Check if Section column exists, if not add it
    if len(rows[0]) > 0 and rows[0][1] != "Section":
        # Old format - need to migrate
        rows[0].insert(1, "Section")
        for i in range(1, len(rows)):
            rows[i].insert(1, "Unknown")

    if student_name in rows[0]:
        return

    rows[0].append(student_name)
    for i in range(1, len(rows)):
        rows[i].append("A")

    with open(CSV_PATH, "w", newline="") as f:
        csv.writer(f).writerows(rows)


def mark_attendance(present_students, section="Unknown"):
    """Mark attendance for present students with section info"""
    today = str(date.today())
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["Date", "Section"] + list(present_students)
            writer.writerow(header)
        return

    with open(CSV_PATH, "r") as f:
        rows = list(csv.reader(f))

    if not rows:
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["Date", "Section"] + list(present_students)
            writer.writerow(header)
        return

    header = rows[0]

    # Check if Section column exists, if not add it
    if len(header) > 1 and header[1] != "Section":
        header.insert(1, "Section")
        for i in range(1, len(rows)):
            rows[i].insert(1, "Unknown")

    # Ensure Section column exists
    if "Section" not in header:
        header.insert(1, "Section")
        for i in range(1, len(rows)):
            rows[i].insert(1, "Unknown")

    # Add any new students to the header
    for student in present_students:
        if student not in header:
            header.append(student)
            for i in range(1, len(rows)):
                rows[i].append("A")

    rows[0] = header

    new_row = [today, section]
    for name in header[2:]:  # Skip Date and Section columns
        new_row.append("P" if name in present_students else "A")

    rows.append(new_row)

    with open(CSV_PATH, "w", newline="") as f:
        csv.writer(f).writerows(rows)


def get_attendance_data():
    """Get all attendance data from CSV"""
    if not os.path.exists(CSV_PATH):
        return [], []

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) < 2:
        return [], []

    header = rows[0]
    data = rows[1:]

    return header, data


def get_students_list():
    """Get list of all enrolled students from CSV header"""
    header, _ = get_attendance_data()
    if not header:
        return []

    # Check if Section column exists
    has_section = len(header) > 1 and header[1] == "Section"
    start_idx = 2 if has_section else 1

    if len(header) > start_idx:
        return header[start_idx:]
    return []


def get_attendance_by_section(section=None):
    """Get attendance data filtered by section"""
    header, data = get_attendance_data()
    if not data:
        return header, []

    if section and section != "All":
        # Ensure Section column exists
        section_idx = 1 if len(header) > 1 and header[1] == "Section" else -1
        if section_idx >= 0:
            data = [row for row in data if len(
                row) > section_idx and row[section_idx] == section]

    return header, data


def get_attendance_by_date_range(start_date=None, end_date=None, section=None):
    """Get attendance data within a date range and optionally filtered by section"""
    header, data = get_attendance_data()
    if not data:
        return header, []

    filtered_data = []
    for row in data:
        if not row:
            continue

        row_date = row[0]
        try:
            row_date_obj = datetime.strptime(row_date, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Date filter
        if start_date and row_date_obj < start_date:
            continue
        if end_date and row_date_obj > end_date:
            continue

        # Section filter
        if section and section != "All":
            section_idx = 1 if len(
                header) > 1 and header[1] == "Section" else -1
            if section_idx >= 0 and len(row) > section_idx:
                if row[section_idx] != section:
                    continue

        filtered_data.append(row)

    return header, filtered_data


def get_student_attendance_rate(student_name):
    """Calculate attendance rate for a specific student"""
    header, data = get_attendance_data()
    if not data or student_name not in header:
        return 0.0

    student_idx = header.index(student_name)
    total = len(data)
    present = sum(1 for row in data if len(row) >
                  student_idx and row[student_idx] == "P")

    return (present / total * 100) if total > 0 else 0.0


def get_all_student_attendance_rates():
    """Get attendance rates for all students"""
    header, data = get_attendance_data()
    if not data:
        return {}

    # Check if Section column exists
    has_section = len(header) > 1 and header[1] == "Section"

    # Skip Date and Section columns if present
    start_idx = 2 if has_section else 1
    students = header[start_idx:] if len(header) > start_idx else []
    rates = {}

    for student in students:
        rates[student] = get_student_attendance_rate(student)

    return rates


def get_low_attendance_students(threshold=75.0):
    """Get students with attendance below threshold"""
    rates = get_all_student_attendance_rates()
    return {name: rate for name, rate in rates.items() if rate < threshold}


def get_daily_attendance_counts(days=7, section=None):
    """Get daily attendance counts for the last N days"""
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    header, data = get_attendance_by_date_range(start_date, today, section)

    # Check if Section column exists
    has_section = len(header) > 1 and header[1] == "Section"
    start_idx = 2 if has_section else 1

    daily_counts = {}
    students = header[start_idx:] if len(header) > start_idx else []

    for i in range(days):
        day = start_date + timedelta(days=i)
        day_str = str(day)
        daily_counts[day_str] = {"present": 0,
                                 "absent": 0, "total": len(students)}

    for row in data:
        if not row:
            continue
        row_date = row[0]
        if row_date in daily_counts:
            present = row[start_idx:].count("P") if len(row) > start_idx else 0
            absent = row[start_idx:].count("A") if len(row) > start_idx else 0
            daily_counts[row_date]["present"] += present
            daily_counts[row_date]["absent"] += absent

    return daily_counts


def get_section_comparison():
    """Compare attendance between sections"""
    header, data = get_attendance_data()
    if not data:
        return {}

    section_stats = {}
    section_idx = 1 if len(header) > 1 and header[1] == "Section" else -1

    if section_idx < 0:
        return {}

    for row in data:
        if len(row) <= section_idx:
            continue

        section = row[section_idx]
        if section not in section_stats:
            section_stats[section] = {"present": 0, "total": 0}

        present = row[2:].count("P") if len(row) > 2 else 0
        total = len(row) - 2 if len(row) > 2 else 0

        section_stats[section]["present"] += present
        section_stats[section]["total"] += total

    return section_stats


def get_today_attendance_by_section():
    """Get today's attendance grouped by section (or most recent date if no data for today)"""
    today = str(date.today())
    header, data = get_attendance_data()

    if not data:
        return {}

    # Check if Section column exists
    has_section = len(header) > 1 and header[1] == "Section"

    # Find the most recent date in the data
    most_recent_date = None
    for row in data:
        if row and row[0]:
            try:
                row_date = datetime.strptime(row[0], "%Y-%m-%d").date()
                if most_recent_date is None or row_date > most_recent_date:
                    most_recent_date = row_date
            except ValueError:
                continue

    # Use today if available, otherwise use most recent date
    target_date = str(today) if most_recent_date and most_recent_date == date.today(
    ) else (str(most_recent_date) if most_recent_date else today)

    section_attendance = {}

    for row in data:
        if not row or row[0] != target_date:
            continue

        if has_section:
            section = row[1] if len(row) > 1 else "Unknown"
            present = row[2:].count("P") if len(row) > 2 else 0
        else:
            # Old format without Section column
            section = "Legacy Data"
            present = row[1:].count("P") if len(row) > 1 else 0

        if section not in section_attendance:
            section_attendance[section] = 0
        section_attendance[section] += present

    return section_attendance


def get_recent_activities(limit=5):
    """Get recent attendance activities with section info, grouped by date"""
    header, data = get_attendance_data()
    if not data:
        return []

    # Check if Section column exists
    has_section = len(header) > 1 and header[1] == "Section"

    # Group by date and section
    date_section_map = {}

    for row in data:
        if not row or not row[0]:
            continue

        date_str = row[0]

        if has_section:
            section = row[1] if len(row) > 1 else "Unknown"
            present = row[2:].count("P") if len(row) > 2 else 0
        else:
            section = "All Sections"
            present = row[1:].count("P") if len(row) > 1 else 0

        key = (date_str, section)
        if key not in date_section_map:
            date_section_map[key] = 0
        date_section_map[key] += present

    # Convert to list and sort by date (most recent first)
    activities = []
    for (date_str, section), present in date_section_map.items():
        activities.append({
            "date": date_str,
            "section": section,
            "present": present
        })

    # Sort by date descending
    activities.sort(key=lambda x: x["date"], reverse=True)

    # Return top N
    return activities[:limit]


def search_students(query):
    """Search students by name"""
    students = get_students_list()
    query = query.lower()
    return [s for s in students if query in s.lower()]
