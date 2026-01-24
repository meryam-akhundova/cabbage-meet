"""
Schedule parsers for CabbageMeet.

Supports parsing schedules from:
- Quest (pasted text format)
- iCalendar (.ics files)
"""

from __future__ import annotations

import re
import json
from datetime import datetime
from typing import List, Optional


class ScheduleParseError(Exception):
    """Custom exception for schedule parsing errors."""
    pass

class Meeting:
    def __init__(self, days: List[str], start_time: str, end_time: str, 
                 location: str, instructor: str, start_date: str, end_date: str, component: str = ""):
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.instructor = instructor
        self.start_date = start_date
        self.end_date = end_date
        self.component = component
    
    def to_dict(self):
        return {
            'days': self.days,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'location': self.location,
            'instructor': self.instructor,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'component': self.component
        }

class Course:
    def __init__(self):
        self.course_code = ""
        self.course_name = ""
        self.class_number = 0
        self.section = ""
        self.component = ""
        self.instructors = []
        self.units = 0.0
        self.status = ""
        self.grading_basis = ""
        self.meetings = []
    
    def to_dict(self):
        return {
            'course_code': self.course_code,
            'course_name': self.course_name,
            'class_number': self.class_number,
            'section': self.section,
            'component': self.component,
            'instructors': self.instructors,
            'units': self.units,
            'status': self.status,
            'grading_basis': self.grading_basis,
            'meetings': [m.to_dict() for m in self.meetings]
        }

class Schedule:
    def __init__(self):
        self.term = ""
        self.courses = []
    
    def to_dict(self):
        return {
            'term': self.term,
            'courses': [c.to_dict() for c in self.courses]
        }
    
    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

def parse_days(days_str: str) -> List[str]:
    """Parse day string like 'MWF' or 'TTh' into list ['M', 'W', 'F']"""
    if days_str == "TBA":
        return ["TBA"]
    
    days = []
    i = 0
    while i < len(days_str):
        # Handle "TTh" specially
        if i + 2 <= len(days_str) and days_str[i:i+2] == "Th":
            days.append("Th")
            i += 2
        elif days_str[i] == 'T' and i + 1 < len(days_str) and days_str[i+1] == 'h':
            days.append("Th")
            i += 2
        else:
            days.append(days_str[i])
            i += 1
    return days

def parse_course(text: str) -> Course:
    """Parse a single course section from Quest text"""
    course = Course()
    lines = text.split('\n')
    
    # Parse course code and name (first line)
    header_match = re.search(r'([A-Z]+\s+\d+[A-Z]*)\s+-\s+(.+)', lines[0])
    if header_match:
        course.course_code = header_match.group(1)
        course.course_name = header_match.group(2)
    
    # Find Status/Units/Grading section
    for i, line in enumerate(lines):
        # Tab-separated format
        if line.strip() == "Status\tUnits\tGrading\tDeadlines":
            if i + 1 < len(lines):
                course.status = lines[i + 1].strip()
            if i + 2 < len(lines):
                try:
                    course.units = float(lines[i + 2].strip())
                except:
                    pass
            if i + 3 < len(lines):
                course.grading_basis = lines[i + 3].strip()
            break
        # Newline-separated format
        if line.strip() == "Status" and i + 7 < len(lines):
            if (lines[i + 1].strip() == "Units" and
                lines[i + 2].strip() == "Grading" and
                lines[i + 3].strip() == "Deadlines"):
                course.status = lines[i + 4].strip()
                try:
                    course.units = float(lines[i + 5].strip())
                except:
                    pass
                course.grading_basis = lines[i + 6].strip()
                break
    
    # Find the class table
    table_start = -1
    for i, line in enumerate(lines):
        # Tab-separated format
        if line.strip() == "Class Nbr\tSection\tComponent\tDays & Times\tRoom\tInstructor\tStart/End Date":
            table_start = i + 1
            break
        # Newline-separated format
        if line.strip() == "Class Nbr" and i + 6 < len(lines):
            if (lines[i + 1].strip() == "Section" and
                lines[i + 2].strip() == "Component" and
                lines[i + 3].strip() == "Days & Times"):
                table_start = i + 7
                break
    
    if table_start == -1:
        return course
    
    # Parse the table - each row is 7 lines (class_nbr, section, component, days&times, room, instructor, dates)
    # OR could be empty lines with just continuation
    i = table_start
    current_class_number = 0
    current_section = ""
    current_component = ""
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a new class entry (has a class number)
        if line.isdigit() and len(line) >= 4:
            # This is a class number
            current_class_number = int(line)
            
            # Get section (next line)
            if i + 1 < len(lines):
                current_section = lines[i + 1].strip()
            
            # Get component (next line)
            if i + 2 < len(lines):
                current_component = lines[i + 2].strip()
            
            # Get days & times (next line)
            days_and_times = ""
            if i + 3 < len(lines):
                days_and_times = lines[i + 3].strip()
            
            # Get room (next line)
            room = ""
            if i + 4 < len(lines):
                room = lines[i + 4].strip()
            
            # Get instructor (next line) - might span multiple lines
            instructor = ""
            if i + 5 < len(lines):
                instructor = lines[i + 5].strip()
                # Check if next line is also part of instructor (has comma at end)
                if i + 6 < len(lines) and instructor.endswith(','):
                    instructor += " " + lines[i + 6].strip()
                    i += 1
            
            # Get dates (next line)
            dates = ""
            if i + 6 < len(lines):
                dates = lines[i + 6].strip()
            
            # Store first class number as course's main info
            if course.class_number == 0:
                course.class_number = current_class_number
                course.section = current_section
                course.component = current_component
            
            # Parse the meeting
            if days_and_times and dates:
                meeting = parse_meeting_line(days_and_times, room, instructor, dates, current_component)
                if meeting:
                    course.meetings.append(meeting)
                    # Add instructor to course instructors list
                    if instructor and instructor != "To be Announced" and instructor not in course.instructors:
                        course.instructors.append(instructor)
            
            i += 7  # Move to next entry
        
        # Check for continuation lines (empty class number cell, just has days/times)
        elif not line and i + 3 < len(lines):
            # This might be a continuation - check if next few lines have meeting info
            days_and_times = lines[i + 3].strip() if i + 3 < len(lines) else ""
            room = lines[i + 4].strip() if i + 4 < len(lines) else ""
            instructor = lines[i + 5].strip() if i + 5 < len(lines) else ""
            
            # Check if instructor spans multiple lines
            if instructor.endswith(',') and i + 6 < len(lines):
                instructor += " " + lines[i + 6].strip()
                dates_line = i + 7
            else:
                dates_line = i + 6
            
            dates = lines[dates_line].strip() if dates_line < len(lines) else ""
            
            if days_and_times and dates:
                meeting = parse_meeting_line(days_and_times, room, instructor, dates, current_component)
                if meeting:
                    course.meetings.append(meeting)
                    if instructor and instructor != "To be Announced" and instructor not in course.instructors:
                        course.instructors.append(instructor)
            
            i += 7
        else:
            i += 1
    
    return course

def parse_meeting_line(days_and_times: str, room: str, instructor: str, dates: str, component: str = ""):
    """Parse a single meeting line"""
    # Parse days and times
    # Format: "MWF 10:30AM - 11:20AM" or "TBA"
    if days_and_times == "TBA":
        # Parse dates
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+-\s+(\d{2}/\d{2}/\d{4})', dates)
        if date_match:
            return Meeting(
                days=["TBA"],
                start_time="",
                end_time="",
                location=room,
                instructor=instructor,
                start_date=date_match.group(1),
                end_date=date_match.group(2),
                component=component
            )
        return None
    
    # Parse regular time format
    time_match = re.match(r'((?:Th|[MTWF])+)\s+(\d{1,2}:\d{2}[AP]M)\s+-\s+(\d{1,2}:\d{2}[AP]M)', days_and_times)
    if not time_match:
        return None
    
    days_str = time_match.group(1)
    start_time = time_match.group(2)
    end_time = time_match.group(3)
    
    days = parse_days(days_str)
    
    # Parse dates
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+-\s+(\d{2}/\d{2}/\d{4})', dates)
    if not date_match:
        return None
    
    start_date = date_match.group(1)
    end_date = date_match.group(2)
    
    return Meeting(
        days=days,
        start_time=start_time,
        end_time=end_time,
        location=room,
        instructor=instructor,
        start_date=start_date,
        end_date=end_date,
        component=component
    )

def parse_quest_schedule(text: str) -> Schedule:
    """Parse entire Quest schedule text.
    
    Args:
        text: The pasted Quest schedule text
        
    Returns:
        Schedule object with parsed courses
        
    Raises:
        ScheduleParseError: If the schedule format is invalid or cannot be parsed
    """
    if not text or not text.strip():
        raise ScheduleParseError("Schedule text is empty")
    
    schedule = Schedule()
    
    # Extract term
    term_match = re.search(r'(Fall|Winter|Spring)\s+(\d{4})', text)
    if term_match:
        schedule.term = term_match.group(0)
    
    # Split by courses
    # Each course starts with "COURSE_CODE - Course Name"
    # Course codes can have letters after numbers (e.g., ENGL 100B)
    course_pattern = r'([A-Z]+\s+\d+[A-Z]*)\s+-\s+([^\n]+)\n'
    
    # Find all course start positions
    course_starts = []
    for match in re.finditer(course_pattern, text):
        # Make sure it's followed by "Status" to confirm it's a course header
        text_after = text[match.end():match.end()+100]
        if 'Status' in text_after and 'Units' in text_after:
            course_starts.append(match.start())
    
    # If no courses found, raise an error
    if not course_starts:
        raise ScheduleParseError(
            "No courses found in schedule. "
            "Please ensure you pasted the complete schedule from Quest."
        )
    
    # Extract each course section
    for i in range(len(course_starts)):
        start = course_starts[i]
        end = course_starts[i + 1] if i + 1 < len(course_starts) else len(text)
        
        course_text = text[start:end]
        try:
            course = parse_course(course_text)
            
            if course.course_code:
                schedule.courses.append(course)
        except Exception as e:
            # Log the error but continue parsing other courses
            # This allows partial success if one course fails
            print(f"Warning: Failed to parse course: {e}")
            continue
    
    # Validate that we got at least one valid course
    if not schedule.courses:
        raise ScheduleParseError(
            "Could not parse any courses from the schedule. "
            "Please check the format and try again."
        )
    
    return schedule

def print_schedule_summary(schedule: Schedule):
    """Print a nice readable summary of the schedule"""
    print(f"\n=== {schedule.term} Schedule ===\n")
    
    for course in schedule.courses:
        print(f"📚 {course.course_code} - {course.course_name}")
        print(f"   Status: {course.status} | Units: {course.units:.2f}")
        print(f"   Class #{course.class_number} | Section {course.section} | {course.component}")
        
        if course.instructors:
            print(f"   👨‍🏫 Instructors: {', '.join(course.instructors)}")
        
        if course.meetings:
            print(f"   📅 Meetings ({len(course.meetings)}):")
            for meeting in course.meetings:
                if meeting.days and meeting.days[0] == "TBA":
                    print(f"      TBA @ {meeting.location}")
                    print(f"         {meeting.start_date} to {meeting.end_date}")
                else:
                    days_str = ''.join(meeting.days)
                    print(f"      {days_str} {meeting.start_time} - {meeting.end_time}")
                    print(f"         @ {meeting.location} | {meeting.instructor}")
                    print(f"         {meeting.start_date} to {meeting.end_date}")
        else:
            print(f"   ⚠️  No meetings found")
        print()

def main():
    try:
        with open('quest_schedule.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: Could not find 'quest_schedule.txt'")
        print("Make sure the file is in the same directory as this script.")
        return
    
    print("Parsing Quest schedule...")
    schedule = parse_quest_schedule(text)
    
    print(f"Found {len(schedule.courses)} courses")
    
    print_schedule_summary(schedule)
    
    schedule.save_to_file('my_schedule.json')
    print("✅ Saved to my_schedule.json")


# ============================================================================
# iCalendar Parser
# ============================================================================

def parse_icalendar(ical_content: str) -> Schedule:
    """Parse iCalendar content and convert to Schedule object.
    
    Args:
        ical_content: The content of an .ics file
        
    Returns:
        Schedule object with parsed courses and meetings
        
    Raises:
        ScheduleParseError: If the iCalendar format is invalid
    """
    if not ical_content or not ical_content.strip():
        raise ScheduleParseError("iCalendar content is empty")
    
    schedule = Schedule()
    
    # Extract term from calendar name or use default
    calendar_name_match = re.search(r'X-WR-CALNAME[:\s]+([^\r\n]+)', ical_content, re.IGNORECASE)
    if calendar_name_match:
        schedule.term = calendar_name_match.group(1).strip()
    else:
        schedule.term = "Imported Calendar"
    
    # Find all VEVENT blocks (each represents a class/meeting)
    vevent_pattern = r'BEGIN:VEVENT([\s\S]*?)END:VEVENT'
    vevents = re.findall(vevent_pattern, ical_content, re.IGNORECASE)
    
    if not vevents:
        raise ScheduleParseError("No events found in iCalendar file")
    
    # Group events by course
    courses_dict = {}
    
    for vevent in vevents:
        summary = _extract_ical_property(vevent, 'SUMMARY')
        dtstart = _extract_ical_property(vevent, 'DTSTART')
        dtend = _extract_ical_property(vevent, 'DTEND')
        location = _extract_ical_property(vevent, 'LOCATION')
        
        if not summary or not dtstart:
            continue
        
        start_dt = _parse_ical_datetime(dtstart)
        end_dt = _parse_ical_datetime(dtend) if dtend else None
        
        if not start_dt:
            continue
        
        # Determine course code from summary
        course_code_match = re.match(r'([A-Z]+\s+\d+)', summary)
        course_code = course_code_match.group(1) if course_code_match else summary.split()[0] if summary.split() else "UNKNOWN"
        course_name = summary.replace(course_code, "").strip(" -")
        
        # Get or create course
        if course_code not in courses_dict:
            course = Course()
            course.course_code = course_code
            course.course_name = course_name
            course.status = "Enrolled"
            courses_dict[course_code] = course
        else:
            course = courses_dict[course_code]
        
        # Determine day of week
        day_abbrev = _get_day_abbreviation(start_dt.weekday())
        
        # Parse time
        start_time_str = start_dt.strftime("%I:%M%p").lstrip('0')
        end_time_str = end_dt.strftime("%I:%M%p").lstrip('0') if end_dt else ""
        
        # Parse dates
        start_date_str = start_dt.strftime("%m/%d/%Y")
        end_date_str = end_dt.strftime("%m/%d/%Y") if end_dt else start_date_str
        
        # Check if this meeting already exists (same time, location)
        meeting_exists = False
        for existing_meeting in course.meetings:
            if (existing_meeting.start_time == start_time_str and
                existing_meeting.end_time == end_time_str and
                existing_meeting.location == (location or "TBA")):
                if day_abbrev not in existing_meeting.days:
                    existing_meeting.days.append(day_abbrev)
                if start_date_str < existing_meeting.start_date:
                    existing_meeting.start_date = start_date_str
                if end_date_str > existing_meeting.end_date:
                    existing_meeting.end_date = end_date_str
                meeting_exists = True
                break
        
        if not meeting_exists:
            meeting = Meeting(
                days=[day_abbrev],
                start_time=start_time_str,
                end_time=end_time_str,
                location=location or "TBA",
                instructor="",
                start_date=start_date_str,
                end_date=end_date_str
            )
            course.meetings.append(meeting)
    
    schedule.courses = list(courses_dict.values())
    
    if not schedule.courses:
        raise ScheduleParseError("No valid courses found in iCalendar file")
    
    return schedule


def _extract_ical_property(content: str, prop_name: str) -> Optional[str]:
    """Extract a property value from iCalendar content."""
    pattern = rf'{prop_name}[:\s]+([^\r\n]+)'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        value = value.replace('\\,', ',').replace('\\;', ';').replace('\\n', '\n')
        return value
    return None


def _parse_ical_datetime(dt_str: str) -> Optional[datetime]:
    """Parse iCalendar datetime string (YYYYMMDDTHHMMSS format)."""
    if not dt_str:
        return None
    
    dt_str = dt_str.replace('Z', '').strip()
    
    if 'T' in dt_str and len(dt_str) >= 15:
        try:
            date_part = dt_str[:8]
            time_part = dt_str[9:15]
            return datetime(
                int(date_part[:4]), int(date_part[4:6]), int(date_part[6:8]),
                int(time_part[:2]), int(time_part[2:4]), int(time_part[4:6])
            )
        except (ValueError, IndexError):
            pass
    
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def _get_day_abbreviation(weekday: int) -> str:
    """Convert Python weekday (0=Monday) to abbreviation."""
    days = ['M', 'T', 'W', 'Th', 'F', 'S', 'Su']
    return days[weekday] if 0 <= weekday < len(days) else 'M'


if __name__ == "__main__":
    main()