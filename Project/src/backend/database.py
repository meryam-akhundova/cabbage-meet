"""
Database models and connection setup for CabbageMeet.

This module provides database models and helper functions for storing schedules.
Uses SQLite for database storage.
"""

from __future__ import annotations

import sqlite3
import os
import re
from datetime import datetime, time, date
from typing import Optional, List, Dict, Any
from pathlib import Path

# Helper functions
def serialize_time(time_obj):
    """Convert time object to 12-hour format string (HH:MMAM/PM)."""
    if time_obj is None:
        return None
    if isinstance(time_obj, str):
        return time_obj

    if hasattr(time_obj, 'hour'):
        # Convert to 12-hour format with AM/PM
        hour = time_obj.hour
        minute = time_obj.minute
        am_pm = "AM"

        if hour >= 12:
            am_pm = "PM"
            if hour > 12:
                hour -= 12
        elif hour == 0:
            hour = 12

        return f"{hour}:{minute:02d}{am_pm}"

    return str(time_obj)

def serialize_date(date_obj):
    """Convert date object to string for JSON serialization."""
    if date_obj is None:
        return None
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d") if hasattr(date_obj, 'strftime') else str(date_obj)

# Database file path (in the backend directory)
DB_PATH = Path(__file__).parent / 'cabbagemeet.db'

# Register adapters for Python datetime objects
# This allows SQLite to work directly with Python datetime/date/time objects
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(time, lambda t: t.isoformat())

# Register converters to get Python objects back
def convert_timestamp(s):
    if not s:
        return None
    s = s.decode() if isinstance(s, bytes) else s
    return datetime.fromisoformat(s) if s else None

def convert_date(s):
    if not s:
        return None
    s = s.decode() if isinstance(s, bytes) else s
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None

def convert_time(s):
    if not s:
        return None
    s = s.decode() if isinstance(s, bytes) else s
    return datetime.strptime(s, "%H:%M:%S").time() if s else None

sqlite3.register_converter("TIMESTAMP", convert_timestamp)
sqlite3.register_converter("DATE", convert_date)
sqlite3.register_converter("TIME", convert_time)


def parse_date(date_str: str) -> Optional[date]:
    """Convert date from MM/DD/YYYY format to Python date object.
    
    Args:
        date_str: Date string in MM/DD/YYYY format
        
    Returns:
        Python date object or None if invalid
    """
    if not date_str or date_str.strip() == "":
        return None
    
    try:
        # Parse MM/DD/YYYY format
        date_obj = datetime.strptime(date_str.strip(), "%m/%d/%Y")
        return date_obj.date()
    except (ValueError, AttributeError):
        return None


def parse_time(time_str: str) -> Optional[time]:
    """Convert time from 12-hour format (HH:MMAM/PM) to Python time object.
    
    Args:
        time_str: Time string in format like "10:30AM" or "2:30PM"
        
    Returns:
        Python time object or None if invalid
    """
    if not time_str or time_str.strip() == "":
        return None
    
    time_str = time_str.strip().upper()
    
    # Handle TBA or empty
    if time_str == "TBA" or time_str == "":
        return None
    
    try:
        # Match patterns like "10:30AM", "2:30PM", "12:00PM"
        match = re.match(r'(\d{1,2}):(\d{2})(AM|PM)', time_str)
        if not match:
            return None
        
        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3)
        
        # Convert to 24-hour format
        if am_pm == "PM" and hour != 12:
            hour += 12
        elif am_pm == "AM" and hour == 12:
            hour = 0
        
        # Create and return time object
        return time(hour, minute)
    except (ValueError, AttributeError):
        return None


def get_db_connection():
    """Get database connection.
    
    Returns:
        Database connection object with row factory set to Row
    """
    # Use detect_types to enable automatic conversion
    conn = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize the database with required tables.
    Creates tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT REFERENCES users(user_id),
            term TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER REFERENCES schedules(schedule_id) ON DELETE CASCADE,
            course_code TEXT NOT NULL,
            course_name TEXT,
            class_number INTEGER,
            section TEXT,
            component TEXT,
            units REAL,
            status TEXT,
            grading_basis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create meetings table
    # SQLite doesn't have separate DATE/TIME types, but we use TEXT with ISO format
    # which SQLite can recognize and use for date/time operations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
            day_of_week TEXT NOT NULL,
            start_time TIME,
            end_time TIME,
            location TEXT,
            instructor TEXT,
            start_date DATE,
            end_date DATE,
            component TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_user_id ON schedules(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_courses_schedule_id ON courses(schedule_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_course_id ON meetings(course_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_day_time ON meetings(day_of_week, start_time)')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personal_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT NOT NULL,
            group_id TEXT NOT NULL,
            start_datetime TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_user_id ON personal_events(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_start ON personal_events(start_datetime)')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_groups (
            group_id TEXT PRIMARY KEY,
            user_id TEXT,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            is_course INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_user_id ON personal_events(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_start ON personal_events(start_datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_groups_user_id ON task_groups(user_id)')

    conn.commit()
    conn.close()


def save_schedule_to_db(schedule, user_id: Optional[str] = None) -> int:
    """Save a parsed schedule to the database.
    
    Args:
        schedule: Schedule object from quest_parser
        user_id: Optional user ID (for future authentication)
        
    Returns:
        schedule_id: The ID of the saved schedule
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create or get user if user_id is provided
        if user_id:
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = cursor.fetchone()
            if not user:
                cursor.execute(
                    "INSERT INTO users (user_id, name) VALUES (?, ?)",
                    (user_id, f"User {user_id}")
                )
        
        # Create schedule record
        cursor.execute(
            "INSERT INTO schedules (user_id, term) VALUES (?, ?)",
            (user_id, schedule.term)
        )
        schedule_id = cursor.lastrowid
        
        # Insert courses and meetings
        for course in schedule.courses:
            cursor.execute(
                """INSERT INTO courses 
                   (schedule_id, course_code, course_name, class_number, section, 
                    component, units, status, grading_basis)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (schedule_id, course.course_code, course.course_name,
                 course.class_number, course.section, course.component,
                 course.units, course.status, course.grading_basis)
            )
            course_id = cursor.lastrowid
            
            # Insert meetings (one record per day)
            for meeting in course.meetings:
                # Convert to Python date/time objects (SQLite adapters will handle conversion)
                start_date_obj = parse_date(meeting.start_date)
                end_date_obj = parse_date(meeting.end_date)
                start_time_obj = parse_time(meeting.start_time)
                end_time_obj = parse_time(meeting.end_time)
                
                for day in meeting.days:
                    cursor.execute(
                        """INSERT INTO meetings 
                           (course_id, day_of_week, start_time, end_time,
                            location, instructor, start_date, end_date, component)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (course_id, day, start_time_obj, end_time_obj,
                         meeting.location, meeting.instructor,
                         start_date_obj, end_date_obj, meeting.component)
                    )
        
        conn.commit()
        return schedule_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_schedule_from_db(schedule_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a schedule from the database.
    
    Args:
        schedule_id: The ID of the schedule to retrieve
        
    Returns:
        Dictionary representation of the schedule, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get schedule
        cursor.execute(
            "SELECT * FROM schedules WHERE schedule_id = ?",
            (schedule_id,)
        )
        schedule_row = cursor.fetchone()
        
        if not schedule_row:
            return None
        
        schedule_dict = {
            'schedule_id': schedule_row['schedule_id'],
            'user_id': schedule_row['user_id'],
            'term': schedule_row['term'],
            'created_at': schedule_row['created_at'],
            'updated_at': schedule_row['updated_at'],
            'courses': []
        }
        
        # Get courses
        cursor.execute(
            "SELECT * FROM courses WHERE schedule_id = ?",
            (schedule_id,)
        )
        courses = cursor.fetchall()
        
        for course_row in courses:
            course_dict = {
                'course_id': course_row['course_id'],
                'course_code': course_row['course_code'],
                'course_name': course_row['course_name'],
                'class_number': course_row['class_number'],
                'section': course_row['section'],
                'component': course_row['component'],
                'units': course_row['units'],
                'status': course_row['status'],
                'grading_basis': course_row['grading_basis'],
                'meetings': []
            }
            
            # Get meetings for this course
            cursor.execute(
                "SELECT * FROM meetings WHERE course_id = ?",
                (course_row['course_id'],)
            )
            meetings = cursor.fetchall()
            
            # Group meetings by time/location/instructor/date (since we store one row per day)
            # Use a tuple of (start_time, end_time, location, instructor, start_date, end_date) as key
            meetings_grouped = {}
            for meeting_row in meetings:
                key = (
                    meeting_row['start_time'],
                    meeting_row['end_time'],
                    meeting_row['location'],
                    meeting_row['instructor'],
                    meeting_row['start_date'],
                    meeting_row['end_date']
                    
                )
                
                if key not in meetings_grouped:
                    meetings_grouped[key] = {
                        'days': [],
                        'start_time': serialize_time(meeting_row['start_time']),
                        'end_time': serialize_time(meeting_row['end_time']),
                        'location': meeting_row['location'],
                        'instructor': meeting_row['instructor'],
                        'start_date': serialize_date(meeting_row['start_date']),
                        'end_date': serialize_date(meeting_row['end_date']),
                        'component': meeting_row['component'] or ''
                    }
                
                # Add the day to the days list
                day = meeting_row['day_of_week']
                if day not in meetings_grouped[key]['days']:
                    meetings_grouped[key]['days'].append(day)
            
            # Convert grouped meetings to list
            for meeting_data in meetings_grouped.values():
                course_dict['meetings'].append(meeting_data)
            
            schedule_dict['courses'].append(course_dict)
        
        return schedule_dict
        
    finally:
        conn.close()


def get_user_schedules(user_id: str) -> List[Dict[str, Any]]:
    """Get all schedules for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of schedule dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT schedule_id FROM schedules WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        schedule_ids = cursor.fetchall()
        
        schedules = []
        for row in schedule_ids:
            schedule = get_schedule_from_db(row['schedule_id'])
            if schedule:
                schedules.append(schedule)
        
        return schedules
        
    finally:
        conn.close()

def create_personal_events_table():
    """Create table for personal events if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                title TEXT NOT NULL,
                group_id TEXT NOT NULL,
                start_datetime TIMESTAMP NOT NULL,
                duration INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_user_id ON personal_events(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personal_events_start ON personal_events(start_datetime)')
        
        conn.commit()
        print("Personal events table created successfully")
    except Exception as e:
        print(f"Error creating personal events table: {e}")
    finally:
        conn.close()

def delete_course_from_db(course_id: int) -> bool:
    """Delete a course and all its meetings from the database.
    
    Args:
        course_id: The ID of the course to delete
        
    Returns:
        True if deletion was successful, False if course not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if course exists
        cursor.execute("SELECT course_id FROM courses WHERE course_id = ?", (course_id,))
        if not cursor.fetchone():
            return False
        
        # Delete meetings
        cursor.execute("DELETE FROM meetings WHERE course_id = ?", (course_id,))
        
        # Delete course
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        
        # Update schedule's updated_at timestamp
        cursor.execute("""
            UPDATE schedules 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE schedule_id = (SELECT schedule_id FROM courses WHERE course_id = ?)
        """, (course_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_course_in_db(course_id: int, updates: Dict[str, Any]) -> bool:
    """Update course information in the database.
    
    Args:
        course_id: The ID of the course to update
        updates: Dictionary of fields to update
        
    Returns:
        True if update was successful, False if course not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if course exists
        cursor.execute("SELECT course_id FROM courses WHERE course_id = ?", (course_id,))
        if not cursor.fetchone():
            return False
        
        # Build update query dynamically based on provided fields
        allowed_fields = ['course_code', 'course_name', 'section', 'component', 
                         'units', 'status', 'grading_basis']
        
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = ?")
                values.append(updates[field])
        
        if not update_fields:
            return True  # Nothing to update
        
        values.append(course_id)
        query = f"UPDATE courses SET {', '.join(update_fields)} WHERE course_id = ?"
        
        cursor.execute(query, values)
        
        # Update schedule's updated_at timestamp
        cursor.execute("""
            UPDATE schedules 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE schedule_id = (SELECT schedule_id FROM courses WHERE course_id = ?)
        """, (course_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def add_component_to_meetings():
    """Add component column to meetings table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE meetings ADD COLUMN component TEXT")
        conn.commit()
        print("Added component column to meetings table")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("Component column already exists")
        else:
            print(f"Error adding component column: {e}")
    finally:
        conn.close()


def delete_meeting_from_db(course_id: int, day_of_week: str) -> bool:
    """Delete a specific meeting for a course on a specific day.
    
    Args:
        course_id: The ID of the course
        day_of_week: The day to delete (e.g., 'Mon', 'Tue', etc.)
        
    Returns:
        True if deletion was successful, False if meeting not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if meeting exists
        cursor.execute(
            "SELECT meeting_id FROM meetings WHERE course_id = ? AND day_of_week = ?",
            (course_id, day_of_week)
        )
        if not cursor.fetchone():
            return False
        
        # Delete the specific meeting
        cursor.execute(
            "DELETE FROM meetings WHERE course_id = ? AND day_of_week = ?",
            (course_id, day_of_week)
        )
        
        # Check if this course has any remaining meetings
        cursor.execute(
            "SELECT COUNT(*) as count FROM meetings WHERE course_id = ?",
            (course_id,)
        )
        remaining = cursor.fetchone()['count']
        
        # If no meetings left, delete the course record too
        if remaining == 0:
            cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        
        # Update schedule's updated_at timestamp
        cursor.execute("""
            UPDATE schedules 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE schedule_id IN (
                SELECT schedule_id FROM courses WHERE course_id = ?
            )
        """, (course_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_personal_event(event_data: Dict[str, Any], user_id: Optional[str] = None) -> int:
    """Save a personal event to the database.
    
    Args:
        event_data: Dictionary with keys: title, group_id, start_datetime, duration
        user_id: Optional user ID
        
    Returns:
        event_id: The ID of the saved event
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO personal_events 
               (user_id, title, group_id, start_datetime, duration)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, event_data['title'], event_data['group_id'],
             event_data['start_datetime'], event_data['duration'])
        )
        event_id = cursor.lastrowid
        conn.commit()
        return event_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_personal_events(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all personal events, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        List of personal event dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if user_id:
            cursor.execute(
                "SELECT * FROM personal_events WHERE user_id = ? ORDER BY start_datetime",
                (user_id,)
            )
        else:
            cursor.execute("SELECT * FROM personal_events ORDER BY start_datetime")
        
        events = cursor.fetchall()
        return [dict(event) for event in events]
    finally:
        conn.close()


def update_personal_event(event_id: int, updates: Dict[str, Any]) -> bool:
    """Update a personal event.
    
    Args:
        event_id: The ID of the event to update
        updates: Dictionary of fields to update
        
    Returns:
        True if update was successful, False if event not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if event exists
        cursor.execute("SELECT event_id FROM personal_events WHERE event_id = ?", (event_id,))
        if not cursor.fetchone():
            return False
        
        # Build update query
        allowed_fields = ['title', 'group_id', 'start_datetime', 'duration']
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = ?")
                values.append(updates[field])
        
        if not update_fields:
            return True
        
        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(event_id)
        
        query = f"UPDATE personal_events SET {', '.join(update_fields)} WHERE event_id = ?"
        cursor.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_personal_event(event_id: int) -> bool:
    """Delete a personal event.
    
    Args:
        event_id: The ID of the event to delete
        
    Returns:
        True if deletion was successful, False if event not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT event_id FROM personal_events WHERE event_id = ?", (event_id,))
        if not cursor.fetchone():
            return False
        
        cursor.execute("DELETE FROM personal_events WHERE event_id = ?", (event_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def save_task_group(group_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
    """Save a task group to the database.
    
    Args:
        group_data: Dictionary with keys: group_id, name, color, is_course
        user_id: Optional user ID
        
    Returns:
        True if saved successfully
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if group already exists
        cursor.execute("SELECT group_id FROM task_groups WHERE group_id = ?", (group_data['group_id'],))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing group
            cursor.execute(
                """UPDATE task_groups 
                   SET name = ?, color = ?, is_course = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE group_id = ?""",
                (group_data['name'], group_data['color'], 
                 1 if group_data.get('is_course', False) else 0, group_data['group_id'])
            )
        else:
            # Insert new group
            cursor.execute(
                """INSERT INTO task_groups 
                   (group_id, user_id, name, color, is_course)
                   VALUES (?, ?, ?, ?, ?)""",
                (group_data['group_id'], user_id, group_data['name'], 
                 group_data['color'], 1 if group_data.get('is_course', False) else 0)
            )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_task_groups(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all task groups, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        List of task group dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if user_id:
            cursor.execute(
                "SELECT * FROM task_groups WHERE user_id = ? OR user_id IS NULL ORDER BY created_at",
                (user_id,)
            )
        else:
            cursor.execute("SELECT * FROM task_groups ORDER BY created_at")
        
        groups = cursor.fetchall()
        result = []
        for group in groups:
            result.append({
                'id': group['group_id'],
                'name': group['name'],
                'color': group['color'],
                'isCourse': bool(group['is_course'])
            })
        return result
    finally:
        conn.close()


def update_task_group(group_id: str, updates: Dict[str, Any]) -> bool:
    """Update a task group.
    
    Args:
        group_id: The ID of the group to update
        updates: Dictionary of fields to update (name, color)
        
    Returns:
        True if update was successful, False if group not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT group_id FROM task_groups WHERE group_id = ?", (group_id,))
        if not cursor.fetchone():
            return False
        
        update_fields = []
        values = []
        
        if 'name' in updates:
            update_fields.append("name = ?")
            values.append(updates['name'])
        
        if 'color' in updates:
            update_fields.append("color = ?")
            values.append(updates['color'])
        
        if not update_fields:
            return True
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(group_id)
        
        query = f"UPDATE task_groups SET {', '.join(update_fields)} WHERE group_id = ?"
        cursor.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_task_group(group_id: str) -> bool:
    """Delete a task group.
    
    Args:
        group_id: The ID of the group to delete
        
    Returns:
        True if deletion was successful, False if group not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT group_id FROM task_groups WHERE group_id = ?", (group_id,))
        if not cursor.fetchone():
            return False
        
        cursor.execute("DELETE FROM task_groups WHERE group_id = ?", (group_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()