"""
Test suite for schedule_parser.py - Targeting 70%+ coverage
Run with: pytest test_schedule_parser.py -v --cov=src.backend.schedule_parser
"""

import pytest
import json
from src.backend.schedule_parser import (
    ScheduleParseError, Meeting, Course, Schedule,
    parse_days, parse_course, parse_meeting_line,
    parse_quest_schedule, parse_icalendar,
    _extract_ical_property, _parse_ical_datetime, _get_day_abbreviation
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_quest_schedule():
    return """Fall 2024

CS 246 - Object-Oriented Software Development

Status
Units
Grading
Deadlines
Enrolled
0.50
Numeric
Class Nbr
Section
Component
Days & Times
Room
Instructor
Start/End Date
5678
001
LEC
TTh 10:00AM - 11:20AM
MC 4045
John Smith
09/09/2024 - 12/02/2024

TUT
F 2:30PM - 3:20PM
MC 2017
Jane Doe
09/09/2024 - 12/02/2024

MATH 239 - Introduction to Combinatorics

Status
Units
Grading
Deadlines
Enrolled
0.50
Numeric
Class Nbr
Section
Component
Days & Times
Room
Instructor
Start/End Date
1234
001
LEC
MWF 11:30AM - 12:20PM
MC 4020
Alice Johnson
09/09/2024 - 12/02/2024"""


# ============================================================================
# Class Tests
# ============================================================================

class TestMeeting:
    def test_meeting_to_dict(self):
        meeting = Meeting(['M', 'W'], '10:00AM', '11:00AM', 'MC 4045', 'Prof', '09/09/2024', '12/02/2024')
        result = meeting.to_dict()
        assert result['days'] == ['M', 'W']
        assert result['start_time'] == '10:00AM'
        assert result['location'] == 'MC 4045'


class TestCourse:
    def test_course_initialization(self):
        course = Course()
        assert course.course_code == ""
        assert course.meetings == []
        assert course.class_number == 0
    
    def test_course_to_dict_with_meetings(self):
        course = Course()
        course.course_code = "CS 246"
        meeting = Meeting(['M'], '10:00AM', '11:00AM', 'Room', 'Prof', '01/01/2024', '04/30/2024')
        course.meetings.append(meeting)
        
        result = course.to_dict()
        assert result['course_code'] == "CS 246"
        assert len(result['meetings']) == 1


class TestSchedule:
    def test_schedule_to_dict(self):
        schedule = Schedule()
        schedule.term = "Fall 2024"
        course = Course()
        course.course_code = "CS 101"
        schedule.courses.append(course)
        
        result = schedule.to_dict()
        assert result['term'] == "Fall 2024"
        assert len(result['courses']) == 1
    
    def test_schedule_save_to_file(self, tmp_path):
        schedule = Schedule()
        schedule.term = "Winter 2025"
        
        file_path = tmp_path / "test.json"
        schedule.save_to_file(str(file_path))
        
        with open(file_path) as f:
            data = json.load(f)
        assert data['term'] == "Winter 2025"


# ============================================================================
# Parsing Function Tests
# ============================================================================

class TestParseDays:
    def test_parse_mwf(self):
        assert parse_days('MWF') == ['M', 'W', 'F']
    
    def test_parse_tth(self):
        assert parse_days('TTh') == ['T', 'Th']
    
    def test_parse_tba(self):
        assert parse_days('TBA') == ['TBA']
    
    def test_parse_empty(self):
        assert parse_days('') == []


class TestParseMeetingLine:
    def test_regular_meeting(self):
        meeting = parse_meeting_line(
            'MWF 10:30AM - 11:20AM',
            'MC 4045',
            'John Smith',
            '09/09/2024 - 12/02/2024'
        )
        assert meeting.days == ['M', 'W', 'F']
        assert meeting.start_time == '10:30AM'
        assert meeting.end_time == '11:20AM'
    
    def test_tba_meeting(self):
        meeting = parse_meeting_line('TBA', 'Online', 'TBA', '01/01/2024 - 04/30/2024')
        assert meeting.days == ['TBA']
        assert meeting.start_time == ''
    
    def test_invalid_time_format(self):
        meeting = parse_meeting_line('MWF InvalidTime', 'Room', 'Prof', '01/01/2024 - 04/30/2024')
        assert meeting is None
    
    def test_invalid_date_format(self):
        meeting = parse_meeting_line('MWF 10:00AM - 11:00AM', 'Room', 'Prof', 'BadDate')
        assert meeting is None


class TestParseCourse:
    def test_parse_basic_course(self):
        text = """CS 246 - Object-Oriented Software Development

Status
Units
Grading
Deadlines
Enrolled
0.50
Numeric

Class Nbr
Section
Component
Days & Times
Room
Instructor
Start/End Date
5678
001
LEC
MWF 10:00AM - 11:00AM
MC 4045
John Smith
09/09/2024 - 12/02/2024"""
        
        course = parse_course(text)
        assert course.course_code == "CS 246"
        assert course.course_name == "Object-Oriented Software Development"
        assert course.units == 0.5
        assert course.status == "Enrolled"
    
    def test_parse_course_with_multiple_meetings(self):
        text = """CS 246 - OOP

Status
Units
Grading
Deadlines
Enrolled
0.50
Numeric

Class Nbr
Section
Component
Days & Times
Room
Instructor
Start/End Date
5678
001
LEC
MWF 10:00AM - 11:00AM
MC 4045
John Smith
09/09/2024 - 12/02/2024



F 2:30PM - 3:20PM
MC 2017
Jane Doe
09/09/2024 - 12/02/2024"""
        
        course = parse_course(text)
        assert len(course.meetings) >= 1
        assert "John Smith" in course.instructors


class TestParseQuestSchedule:
    def test_parse_valid_schedule(self, sample_quest_schedule):
        schedule = parse_quest_schedule(sample_quest_schedule)
        assert schedule.term == "Fall 2024"
        assert len(schedule.courses) == 2
        assert schedule.courses[0].course_code == "CS 246"
    
    def test_parse_empty_schedule(self):
        with pytest.raises(ScheduleParseError, match="Schedule text is empty"):
            parse_quest_schedule("")
    
    def test_parse_whitespace_only(self):
        with pytest.raises(ScheduleParseError, match="Schedule text is empty"):
            parse_quest_schedule("   \n  ")
    
    def test_parse_no_courses(self):
        with pytest.raises(ScheduleParseError, match="No courses found"):
            parse_quest_schedule("Fall 2024\n\nRandom text")


# ============================================================================
# iCalendar Tests
# ============================================================================

class TestParseIcalendar:
    def test_parse_valid_icalendar(self):
        ical = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Fall 2024 Schedule
BEGIN:VEVENT
DTSTART:20240909T100000
DTEND:20240909T110000
SUMMARY:CS 246 - OOP
LOCATION:MC 4045
END:VEVENT
END:VCALENDAR"""
        
        schedule = parse_icalendar(ical)
        assert schedule.term == "Fall 2024 Schedule"
        assert len(schedule.courses) >= 1
    
    def test_parse_empty_icalendar(self):
        with pytest.raises(ScheduleParseError, match="iCalendar content is empty"):
            parse_icalendar("")
    
    def test_parse_no_events(self):
        ical = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
        with pytest.raises(ScheduleParseError, match="No events found"):
            parse_icalendar(ical)


class TestIcalHelpers:
    def test_extract_property(self):
        content = "SUMMARY:CS 246\nLOCATION:MC 4045"
        assert _extract_ical_property(content, 'SUMMARY') == "CS 246"
        assert _extract_ical_property(content, 'LOCATION') == "MC 4045"
        assert _extract_ical_property(content, 'MISSING') is None
    
    def test_parse_datetime(self):
        dt = _parse_ical_datetime('20240909T100000')
        assert dt.year == 2024
        assert dt.month == 9
        assert dt.day == 9
        assert dt.hour == 10
    
    def test_parse_datetime_with_z(self):
        dt = _parse_ical_datetime('20240909T100000Z')
        assert dt is not None
    
    def test_parse_invalid_datetime(self):
        assert _parse_ical_datetime('invalid') is None
        assert _parse_ical_datetime('') is None
    
    def test_get_day_abbreviation(self):
        assert _get_day_abbreviation(0) == 'M'
        assert _get_day_abbreviation(1) == 'T'
        assert _get_day_abbreviation(3) == 'Th'
        assert _get_day_abbreviation(6) == 'Su'