"""
Test suite for database.py - Targeting 70%+ coverage
Run with: pytest test_database.py -v --cov=src.backend.database
"""

import pytest
import sqlite3
from datetime import datetime, time, date
from pathlib import Path
from src.backend.database import (
    serialize_time, serialize_date, parse_date, parse_time,
    get_db_connection, init_db, save_schedule_to_db, get_schedule_from_db,
    get_user_schedules, delete_course_from_db, update_course_in_db,
    delete_meeting_from_db, save_personal_event, get_personal_events,
    update_personal_event, delete_personal_event, save_task_group,
    get_task_groups, update_task_group, delete_task_group
)
from src.backend.schedule_parser import Schedule, Course, Meeting


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a temporary test database"""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
    init_db()
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def sample_schedule():
    """Create a sample schedule for testing"""
    schedule = Schedule()
    schedule.term = "Fall 2024"
    
    course = Course()
    course.course_code = "CS 246"
    course.course_name = "OOP"
    course.class_number = 5678
    course.section = "001"
    course.component = "LEC"
    course.units = 0.5
    course.status = "Enrolled"
    course.grading_basis = "Numeric"
    
    meeting = Meeting(
        days=['M', 'W', 'F'],
        start_time='10:00AM',
        end_time='11:00AM',
        location='MC 4045',
        instructor='John Smith',
        start_date='09/09/2024',
        end_date='12/02/2024'
    )
    meeting.component = "LEC"
    course.meetings.append(meeting)
    schedule.courses.append(course)
    
    return schedule


# ============================================================================
# Test Serialization Functions
# ============================================================================

class TestSerializationFunctions:
    def test_serialize_time_from_time_object(self):
        t = time(10, 30)
        result = serialize_time(t)
        assert result == "10:30AM"
    
    def test_serialize_time_from_afternoon(self):
        t = time(14, 30)
        result = serialize_time(t)
        assert result == "2:30PM"
    
    def test_serialize_time_from_noon(self):
        t = time(12, 0)
        result = serialize_time(t)
        assert result == "12:00PM"
    
    def test_serialize_time_from_midnight(self):
        t = time(0, 0)
        result = serialize_time(t)
        assert result == "12:00AM"
    
    def test_serialize_time_from_string(self):
        result = serialize_time("10:30AM")
        assert result == "10:30AM"
    
    def test_serialize_time_none(self):
        assert serialize_time(None) is None
    
    def test_serialize_date_from_date_object(self):
        d = date(2024, 9, 9)
        result = serialize_date(d)
        assert result == "2024-09-09"
    
    def test_serialize_date_from_string(self):
        result = serialize_date("2024-09-09")
        assert result == "2024-09-09"
    
    def test_serialize_date_none(self):
        assert serialize_date(None) is None


# ============================================================================
# Test Parsing Functions
# ============================================================================

class TestParseDate:
    def test_parse_valid_date(self):
        result = parse_date("09/09/2024")
        assert result == date(2024, 9, 9)
    
    def test_parse_date_with_whitespace(self):
        result = parse_date("  09/09/2024  ")
        assert result == date(2024, 9, 9)
    
    def test_parse_invalid_date(self):
        result = parse_date("invalid")
        assert result is None
    
    def test_parse_empty_date(self):
        assert parse_date("") is None
        assert parse_date("   ") is None
    
    def test_parse_none_date(self):
        assert parse_date(None) is None


class TestParseTime:
    def test_parse_morning_time(self):
        result = parse_time("10:30AM")
        assert result == time(10, 30)
    
    def test_parse_afternoon_time(self):
        result = parse_time("2:30PM")
        assert result == time(14, 30)
    
    def test_parse_noon(self):
        result = parse_time("12:00PM")
        assert result == time(12, 0)
    
    def test_parse_midnight(self):
        result = parse_time("12:00AM")
        assert result == time(0, 0)
    
    def test_parse_time_lowercase(self):
        result = parse_time("10:30am")
        assert result == time(10, 30)
    
    def test_parse_time_tba(self):
        result = parse_time("TBA")
        assert result is None
    
    def test_parse_time_empty(self):
        assert parse_time("") is None
        assert parse_time("   ") is None
    
    def test_parse_time_invalid(self):
        result = parse_time("invalid")
        assert result is None


# ============================================================================
# Test Database Connection
# ============================================================================

class TestDatabaseConnection:
    def test_get_db_connection(self, test_db):
        conn = get_db_connection()
        assert conn is not None
        assert conn.row_factory == sqlite3.Row
        conn.close()
    
    def test_init_db_creates_tables(self, test_db):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'users' in tables
        assert 'schedules' in tables
        assert 'courses' in tables
        assert 'meetings' in tables
        assert 'personal_events' in tables
        assert 'task_groups' in tables
        
        conn.close()


# ============================================================================
# Test Schedule Operations
# ============================================================================

class TestScheduleOperations:
    def test_save_schedule_to_db(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        assert schedule_id > 0
        
        # Verify it was saved
        schedule = get_schedule_from_db(schedule_id)
        assert schedule is not None
        assert schedule['term'] == "Fall 2024"
        assert len(schedule['courses']) == 1
    
    def test_save_schedule_without_user(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule)
        assert schedule_id > 0
    
    def test_get_schedule_from_db_not_found(self, test_db):
        result = get_schedule_from_db(9999)
        assert result is None
    
    def test_get_schedule_with_meetings(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        schedule = get_schedule_from_db(schedule_id)
        
        assert len(schedule['courses']) == 1
        course = schedule['courses'][0]
        assert course['course_code'] == "CS 246"
        assert len(course['meetings']) == 1
        
        meeting = course['meetings'][0]
        assert 'M' in meeting['days']
        assert 'W' in meeting['days']
        assert 'F' in meeting['days']
    
    def test_get_user_schedules(self, test_db, sample_schedule):
        # Save multiple schedules
        schedule_id1 = save_schedule_to_db(sample_schedule, "user1")
        schedule_id2 = save_schedule_to_db(sample_schedule, "user1")
        
        schedules = get_user_schedules("user1")
        assert len(schedules) == 2
    
    def test_get_user_schedules_empty(self, test_db):
        schedules = get_user_schedules("nonexistent")
        assert schedules == []


# ============================================================================
# Test Course Operations
# ============================================================================

class TestCourseOperations:
    def test_delete_course_from_db(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        schedule = get_schedule_from_db(schedule_id)
        course_id = schedule['courses'][0]['course_id']
        
        result = delete_course_from_db(course_id)
        assert result is True
        
        # Verify it was deleted
        schedule = get_schedule_from_db(schedule_id)
        assert len(schedule['courses']) == 0
    
    def test_delete_course_not_found(self, test_db):
        result = delete_course_from_db(9999)
        assert result is False
    
    def test_update_course_in_db(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        schedule = get_schedule_from_db(schedule_id)
        course_id = schedule['courses'][0]['course_id']
        
        updates = {'course_name': 'Updated Name', 'units': 1.0}
        result = update_course_in_db(course_id, updates)
        assert result is True
        
        # Verify updates
        schedule = get_schedule_from_db(schedule_id)
        course = schedule['courses'][0]
        assert course['course_name'] == 'Updated Name'
        assert course['units'] == 1.0
    
    def test_update_course_not_found(self, test_db):
        result = update_course_in_db(9999, {'units': 1.0})
        assert result is False
    
    def test_update_course_no_updates(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        schedule = get_schedule_from_db(schedule_id)
        course_id = schedule['courses'][0]['course_id']
        
        result = update_course_in_db(course_id, {})
        assert result is True


# ============================================================================
# Test Meeting Operations
# ============================================================================

class TestMeetingOperations:
    def test_delete_meeting_from_db(self, test_db, sample_schedule):
        schedule_id = save_schedule_to_db(sample_schedule, "test_user")
        schedule = get_schedule_from_db(schedule_id)
        course_id = schedule['courses'][0]['course_id']
        
        result = delete_meeting_from_db(course_id, 'M')
        assert result is True
        
        # Verify meeting was deleted
        schedule = get_schedule_from_db(schedule_id)
        course = schedule['courses'][0]
        meeting = course['meetings'][0]
        assert 'M' not in meeting['days']
    
    def test_delete_meeting_not_found(self, test_db):
        result = delete_meeting_from_db(9999, 'M')
        assert result is False


# ============================================================================
# Test Personal Events
# ============================================================================

class TestPersonalEvents:
    def test_save_personal_event(self, test_db):
        event_data = {
            'title': 'Study Session',
            'group_id': 'group1',
            'start_datetime': datetime(2024, 9, 9, 14, 0),
            'duration': 60
        }
        
        event_id = save_personal_event(event_data, "test_user")
        assert event_id > 0
    
    def test_get_personal_events(self, test_db):
        event_data = {
            'title': 'Event 1',
            'group_id': 'group1',
            'start_datetime': datetime(2024, 9, 9, 14, 0),
            'duration': 60
        }
        save_personal_event(event_data, "user1")
        
        events = get_personal_events("user1")
        assert len(events) == 1
        assert events[0]['title'] == 'Event 1'
    
    def test_get_personal_events_all(self, test_db):
        event_data = {
            'title': 'Event 1',
            'group_id': 'group1',
            'start_datetime': datetime(2024, 9, 9, 14, 0),
            'duration': 60
        }
        save_personal_event(event_data, "user1")
        
        events = get_personal_events()
        assert len(events) >= 1
    
    def test_update_personal_event(self, test_db):
        event_data = {
            'title': 'Original',
            'group_id': 'group1',
            'start_datetime': datetime(2024, 9, 9, 14, 0),
            'duration': 60
        }
        event_id = save_personal_event(event_data, "user1")
        
        result = update_personal_event(event_id, {'title': 'Updated', 'duration': 90})
        assert result is True
        
        events = get_personal_events("user1")
        assert events[0]['title'] == 'Updated'
        assert events[0]['duration'] == 90
    
    def test_update_personal_event_not_found(self, test_db):
        result = update_personal_event(9999, {'title': 'Test'})
        assert result is False
    
    def test_delete_personal_event(self, test_db):
        event_data = {
            'title': 'To Delete',
            'group_id': 'group1',
            'start_datetime': datetime(2024, 9, 9, 14, 0),
            'duration': 60
        }
        event_id = save_personal_event(event_data, "user1")
        
        result = delete_personal_event(event_id)
        assert result is True
        
        events = get_personal_events("user1")
        assert len(events) == 0
    
    def test_delete_personal_event_not_found(self, test_db):
        result = delete_personal_event(9999)
        assert result is False


# ============================================================================
# Test Task Groups
# ============================================================================

class TestTaskGroups:
    def test_save_task_group(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'Homework',
            'color': '#FF0000',
            'is_course': False
        }
        
        result = save_task_group(group_data, "user1")
        assert result is True
    
    def test_save_task_group_update_existing(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'Original',
            'color': '#FF0000',
            'is_course': False
        }
        save_task_group(group_data, "user1")
        
        # Update
        group_data['name'] = 'Updated'
        result = save_task_group(group_data, "user1")
        assert result is True
        
        groups = get_task_groups("user1")
        assert len(groups) == 1
        assert groups[0]['name'] == 'Updated'
    
    def test_get_task_groups(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'Group 1',
            'color': '#FF0000',
            'is_course': True
        }
        save_task_group(group_data, "user1")
        
        groups = get_task_groups("user1")
        assert len(groups) == 1
        assert groups[0]['name'] == 'Group 1'
        assert groups[0]['isCourse'] is True
    
    def test_get_task_groups_all(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'Group 1',
            'color': '#FF0000',
            'is_course': False
        }
        save_task_group(group_data, "user1")
        
        groups = get_task_groups()
        assert len(groups) >= 1
    
    def test_update_task_group(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'Original',
            'color': '#FF0000',
            'is_course': False
        }
        save_task_group(group_data, "user1")
        
        result = update_task_group('group1', {'name': 'Updated', 'color': '#00FF00'})
        assert result is True
        
        groups = get_task_groups("user1")
        assert groups[0]['name'] == 'Updated'
        assert groups[0]['color'] == '#00FF00'
    
    def test_update_task_group_not_found(self, test_db):
        result = update_task_group('nonexistent', {'name': 'Test'})
        assert result is False
    
    def test_delete_task_group(self, test_db):
        group_data = {
            'group_id': 'group1',
            'name': 'To Delete',
            'color': '#FF0000',
            'is_course': False
        }
        save_task_group(group_data, "user1")
        
        result = delete_task_group('group1')
        assert result is True
        
        groups = get_task_groups("user1")
        assert len(groups) == 0
    
    def test_delete_task_group_not_found(self, test_db):
        result = delete_task_group('nonexistent')
        assert result is False