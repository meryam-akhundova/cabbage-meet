"""
Test suite for main.py - Targeting 70%+ coverage
Run with: pytest test_main.py -v --cov=src.backend.main
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.backend.main import create_app
from src.backend.database import init_db


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app(tmp_path, monkeypatch):
    """Create app with test database"""
    db_path = tmp_path / "test.db"
    
    # Patch the database path
    monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
    
    # Mock the relative imports used in main.py
    import sys
    from src.backend import database, free_time_algorithm
    
    # Make relative imports work
    if 'database' not in sys.modules:
        sys.modules['database'] = database
    if 'free_time_algorithm' not in sys.modules:
        sys.modules['free_time_algorithm'] = free_time_algorithm
    
    init_db()
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    return app


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def sample_quest_schedule():
    """Sample Quest schedule text"""
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
MWF 10:00AM - 11:00AM
MC 4045
John Smith
09/09/2024 - 12/02/2024"""


# ============================================================================
# Basic Route Tests
# ============================================================================

class TestBasicRoutes:
    def test_index_route(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'env' in data


# ============================================================================
# Schedule Import Tests
# ============================================================================

class TestScheduleImport:
    def test_import_quest_schedule_success(self, client, sample_quest_schedule):
        """Test successful Quest schedule import"""
        response = client.post('/api/schedules', 
            json={'scheduleText': sample_quest_schedule})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'scheduleId' in data
        assert data['coursesCount'] > 0
    
    def test_import_quest_schedule_with_name(self, client, sample_quest_schedule):
        """Test Quest import with custom name"""
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule, 'scheduleName': 'My Schedule'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['schedule']['term'] == 'My Schedule'
    
    def test_import_schedule_no_json(self, client):
        """Test import without JSON body"""
        response = client.post('/api/schedules')
        # Flask raises 500 when get_json() fails without proper Content-Type
        assert response.status_code in [400, 500]
    
    def test_import_schedule_empty_text(self, client):
        """Test import with empty schedule text"""
        response = client.post('/api/schedules', json={'scheduleText': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'empty' in data['details'].lower()
    
    def test_import_schedule_invalid_format(self, client):
        """Test import with invalid schedule format"""
        response = client.post('/api/schedules', json={'scheduleText': 'Invalid data'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


# ============================================================================
# iCalendar Import Tests
# ============================================================================

class TestICalendarImport:
    def test_import_icalendar_success(self, client):
        """Test successful iCalendar import"""
        ical = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Fall 2024
BEGIN:VEVENT
DTSTART:20240909T100000
DTEND:20240909T110000
SUMMARY:CS 246 - OOP
LOCATION:MC 4045
END:VEVENT
END:VCALENDAR"""
        
        response = client.post('/api/schedules/icalendar',
            json={'icalContent': ical})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_import_icalendar_empty(self, client):
        """Test iCalendar import with empty content"""
        response = client.post('/api/schedules/icalendar', json={'icalContent': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_import_icalendar_no_json(self, client):
        """Test iCalendar import without JSON"""
        response = client.post('/api/schedules/icalendar')
        assert response.status_code in [400, 500]


# ============================================================================
# Schedule Retrieval Tests
# ============================================================================

class TestScheduleRetrieval:
    def test_get_schedule_by_id(self, client, sample_quest_schedule):
        """Test retrieving schedule by ID"""
        # First import a schedule
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        # Then retrieve it
        response = client.get(f'/api/schedules/{schedule_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['schedule']['schedule_id'] == schedule_id
    
    def test_get_schedule_not_found(self, client):
        """Test retrieving non-existent schedule"""
        response = client.get('/api/schedules/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_latest_schedule(self, client, sample_quest_schedule):
        """Test getting latest schedule"""
        # Import a schedule first
        client.post('/api/schedules', json={'scheduleText': sample_quest_schedule})
        
        response = client.get('/api/schedules/latest')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'schedule' in data
    
    def test_get_latest_schedule_no_schedules(self, client):
        """Test getting latest when no schedules exist"""
        response = client.get('/api/schedules/latest')
        assert response.status_code == 404
    
    def test_get_all_schedules(self, client, sample_quest_schedule):
        """Test getting all schedules"""
        # Import schedules
        client.post('/api/schedules', json={'scheduleText': sample_quest_schedule})
        
        response = client.get('/api/schedules/all')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['schedules']) > 0


# ============================================================================
# Course Operations Tests
# ============================================================================

class TestCourseOperations:
    def test_delete_course(self, client, sample_quest_schedule):
        """Test deleting a course"""
        # Import schedule and get course ID
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        schedule = client.get(f'/api/schedules/{schedule_id}').get_json()
        course_id = schedule['schedule']['courses'][0]['course_id']
        
        # Delete the course
        response = client.delete(f'/api/courses/{course_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_course_not_found(self, client):
        """Test deleting non-existent course"""
        response = client.delete('/api/courses/99999')
        assert response.status_code == 404
    
    def test_update_course(self, client, sample_quest_schedule):
        """Test updating course"""
        # Import and get course ID
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        schedule = client.get(f'/api/schedules/{schedule_id}').get_json()
        course_id = schedule['schedule']['courses'][0]['course_id']
        
        # Update course
        response = client.put(f'/api/courses/{course_id}',
            json={'course_name': 'Updated Name'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_course_no_json(self, client):
        """Test updating course without JSON"""
        response = client.put('/api/courses/1')
        assert response.status_code in [400, 500]
    
    def test_update_course_not_found(self, client):
        """Test updating non-existent course"""
        response = client.put('/api/courses/99999', json={'units': 1.0})
        assert response.status_code == 404


# ============================================================================
# Meeting Operations Tests
# ============================================================================

class TestMeetingOperations:
    def test_delete_meeting(self, client, sample_quest_schedule):
        """Test deleting a meeting"""
        # Import schedule
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        schedule = client.get(f'/api/schedules/{schedule_id}').get_json()
        course_id = schedule['schedule']['courses'][0]['course_id']
        
        # Delete meeting for Monday
        response = client.delete(f'/api/meetings/{course_id}',
            json={'day_of_week': 'M'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_meeting_no_json(self, client):
        """Test deleting meeting without JSON"""
        response = client.delete('/api/meetings/1')
        assert response.status_code in [400, 500]
    
    def test_delete_meeting_no_day(self, client):
        """Test deleting meeting without day_of_week"""
        response = client.delete('/api/meetings/1', json={})
        assert response.status_code == 400
    
    def test_delete_meeting_not_found(self, client):
        """Test deleting non-existent meeting"""
        response = client.delete('/api/meetings/99999',
            json={'day_of_week': 'M'})
        assert response.status_code == 404


# ============================================================================
# Schedule Management Tests
# ============================================================================

class TestScheduleManagement:
    def test_delete_schedule(self, client, sample_quest_schedule):
        """Test deleting entire schedule"""
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        response = client.delete(f'/api/schedules/{schedule_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_schedule_not_found(self, client):
        """Test deleting non-existent schedule"""
        response = client.delete('/api/schedules/99999')
        assert response.status_code == 404
    
    def test_rename_schedule(self, client, sample_quest_schedule):
        """Test renaming schedule"""
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        response = client.patch(f'/api/schedules/{schedule_id}/rename',
            json={'name': 'New Name'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['name'] == 'New Name'
    
    def test_rename_schedule_empty_name(self, client, sample_quest_schedule):
        """Test renaming with empty name"""
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        response = client.patch(f'/api/schedules/{schedule_id}/rename',
            json={'name': ''})
        assert response.status_code == 400
    
    def test_rename_schedule_not_found(self, client):
        """Test renaming non-existent schedule"""
        response = client.patch('/api/schedules/99999/rename',
            json={'name': 'Test'})
        assert response.status_code == 404


# ============================================================================
# Personal Events Tests
# ============================================================================

class TestPersonalEvents:
    def test_create_personal_event(self, client):
        """Test creating personal event"""
        event_data = {
            'title': 'Study Session',
            'group_id': 'group1',
            'start_datetime': '2024-09-09T14:00:00',
            'duration': 60
        }
        
        response = client.post('/api/personal-events', json=event_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'event_id' in data
    
    def test_create_personal_event_missing_field(self, client):
        """Test creating event with missing required field"""
        response = client.post('/api/personal-events',
            json={'title': 'Test'})
        assert response.status_code == 400
    
    def test_get_personal_events(self, client):
        """Test getting personal events"""
        response = client.get('/api/personal-events')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'events' in data
    
    def test_update_personal_event(self, client):
        """Test updating personal event"""
        # Create event first
        event_data = {
            'title': 'Original',
            'group_id': 'group1',
            'start_datetime': '2024-09-09T14:00:00',
            'duration': 60
        }
        response = client.post('/api/personal-events', json=event_data)
        event_id = response.get_json()['event_id']
        
        # Update it
        response = client.put(f'/api/personal-events/{event_id}',
            json={'title': 'Updated'})
        assert response.status_code == 200
    
    def test_update_personal_event_not_found(self, client):
        """Test updating non-existent event"""
        response = client.put('/api/personal-events/99999',
            json={'title': 'Test'})
        assert response.status_code == 404
    
    def test_delete_personal_event(self, client):
        """Test deleting personal event"""
        # Create event
        event_data = {
            'title': 'To Delete',
            'group_id': 'group1',
            'start_datetime': '2024-09-09T14:00:00',
            'duration': 60
        }
        response = client.post('/api/personal-events', json=event_data)
        event_id = response.get_json()['event_id']
        
        # Delete it
        response = client.delete(f'/api/personal-events/{event_id}')
        assert response.status_code == 200
    
    def test_delete_personal_event_not_found(self, client):
        """Test deleting non-existent event"""
        response = client.delete('/api/personal-events/99999')
        assert response.status_code == 404


# ============================================================================
# Task Groups Tests
# ============================================================================

class TestTaskGroups:
    def test_create_task_group(self, client):
        """Test creating task group"""
        group_data = {
            'group_id': 'group1',
            'name': 'Homework',
            'color': '#FF0000'
        }
        
        response = client.post('/api/task-groups', json=group_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_create_task_group_missing_field(self, client):
        """Test creating group with missing field"""
        response = client.post('/api/task-groups',
            json={'name': 'Test'})
        assert response.status_code == 400
    
    def test_get_task_groups(self, client):
        """Test getting task groups"""
        response = client.get('/api/task-groups')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'groups' in data
    
    def test_update_task_group(self, client):
        """Test updating task group"""
        # Create group
        group_data = {
            'group_id': 'group1',
            'name': 'Original',
            'color': '#FF0000'
        }
        client.post('/api/task-groups', json=group_data)
        
        # Update it
        response = client.put('/api/task-groups/group1',
            json={'name': 'Updated'})
        assert response.status_code == 200
    
    def test_update_task_group_not_found(self, client):
        """Test updating non-existent group"""
        response = client.put('/api/task-groups/nonexistent',
            json={'name': 'Test'})
        assert response.status_code == 404
    
    def test_delete_task_group(self, client):
        """Test deleting task group"""
        # Create group
        group_data = {
            'group_id': 'group1',
            'name': 'To Delete',
            'color': '#FF0000'
        }
        client.post('/api/task-groups', json=group_data)
        
        # Delete it
        response = client.delete('/api/task-groups/group1')
        assert response.status_code == 200
    
    def test_delete_task_group_not_found(self, client):
        """Test deleting non-existent group"""
        response = client.delete('/api/task-groups/nonexistent')
        assert response.status_code == 404


# ============================================================================
# Meeting Suggestions Tests
# ============================================================================

class TestMeetingSuggestions:
    def test_suggest_meeting_times(self, client, sample_quest_schedule):
        """Test meeting time suggestions"""
        # Import schedule
        response = client.post('/api/schedules',
            json={'scheduleText': sample_quest_schedule})
        schedule_id = response.get_json()['scheduleId']
        
        # Get suggestions
        response = client.post('/api/meeting-suggestions', json={
            'schedule_ids': [schedule_id],
            'preferred_days': ['M', 'W', 'F'],
            'duration_minutes': 60
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'suggestions' in data
    
    def test_suggest_meeting_times_no_schedules(self, client):
        """Test suggestions with no schedule IDs"""
        response = client.post('/api/meeting-suggestions',
            json={'schedule_ids': []})
        assert response.status_code == 400