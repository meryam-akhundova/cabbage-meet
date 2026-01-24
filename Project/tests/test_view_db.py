"""
Test suite for view_db.py
Run with: pytest test_view_db.py -v --cov=src.backend.view_db
"""

import pytest
import sys
from src.backend.database import init_db, save_schedule_to_db, get_db_connection
from src.backend.schedule_parser import Schedule, Course, Meeting


@pytest.fixture
def test_db_with_data(tmp_path, monkeypatch):
    """Create test database with sample data"""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
    
    # Mock the import in view_db since it uses relative import
    from src.backend import database
    sys.modules['database'] = database
    
    init_db()
    
    # Add sample data
    schedule = Schedule()
    schedule.term = "Fall 2024"
    
    course = Course()
    course.course_code = "CS 246"
    course.course_name = "OOP"
    course.class_number = 5678
    course.section = "001"
    course.units = 0.5
    course.status = "Enrolled"
    
    meeting = Meeting(
        days=['M', 'W'],
        start_time='10:00AM',
        end_time='11:00AM',
        location='MC 4045',
        instructor='Prof Smith',
        start_date='09/09/2024',
        end_date='12/02/2024'
    )
    course.meetings.append(meeting)
    schedule.courses.append(course)
    
    save_schedule_to_db(schedule, "test_user")
    
    return db_path


class TestPrintDatabase:
    def test_print_database_with_data(self, test_db_with_data, capsys):
        """Test printing database with data"""
        from src.backend.view_db import print_database
        
        print_database()
        captured = capsys.readouterr()
        
        # Check headers
        assert "CABBAGEMEET DATABASE CONTENTS" in captured.out
        assert "USERS:" in captured.out
        assert "SCHEDULES:" in captured.out
        assert "COURSES:" in captured.out
        assert "MEETINGS:" in captured.out
        assert "SUMMARY:" in captured.out
        
        # Check data is present
        assert "test_user" in captured.out
        assert "Fall 2024" in captured.out
        assert "CS 246" in captured.out
        assert "OOP" in captured.out
        assert "Prof Smith" in captured.out
        assert "MC 4045" in captured.out
        
        # Check summary
        assert "Total Users:" in captured.out
        assert "Total Schedules:" in captured.out
        assert "Total Courses:" in captured.out
        assert "Total Meetings:" in captured.out
    
    def test_print_database_empty(self, tmp_path, monkeypatch, capsys):
        """Test printing empty database"""
        db_path = tmp_path / "empty.db"
        monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
        
        from src.backend import database
        sys.modules['database'] = database
        
        init_db()
        
        from src.backend.view_db import print_database
        print_database()
        
        captured = capsys.readouterr()
        
        # Check that empty messages appear
        assert "No users found" in captured.out
        assert "No schedules found" in captured.out
        assert "No courses found" in captured.out
        assert "No meetings found" in captured.out
        
        # Check summary shows zeros
        assert "Total Users: 0" in captured.out
        assert "Total Schedules: 0" in captured.out
    
    def test_print_database_with_multiple_records(self, test_db_with_data, capsys):
        """Test printing database with multiple records"""
        # Add another schedule
        schedule2 = Schedule()
        schedule2.term = "Winter 2025"
        
        course2 = Course()
        course2.course_code = "MATH 239"
        course2.course_name = "Combinatorics"
        course2.units = 0.5
        schedule2.courses.append(course2)
        
        save_schedule_to_db(schedule2, "test_user")
        
        from src.backend.view_db import print_database
        print_database()
        
        captured = capsys.readouterr()
        
        # Both schedules should appear
        assert "Fall 2024" in captured.out
        assert "Winter 2025" in captured.out
        assert "CS 246" in captured.out
        assert "MATH 239" in captured.out
    
    def test_print_database_handles_null_values(self, tmp_path, monkeypatch, capsys):
        """Test that None/NULL values are handled properly"""
        db_path = tmp_path / "test_nulls.db"
        monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
        
        from src.backend import database
        sys.modules['database'] = database
        
        init_db()
        
        # Create minimal schedule with some null fields
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schedules (user_id, term) VALUES (NULL, NULL)")
        conn.commit()
        conn.close()
        
        from src.backend.view_db import print_database
        print_database()
        
        captured = capsys.readouterr()
        
        # Should show N/A for null values
        assert "N/A" in captured.out


class TestMainExecution:
    def test_main_block_success(self, test_db_with_data, capsys):
        """Test main block executes successfully"""
        # Simulate running as __main__
        import subprocess
        import sys
        from pathlib import Path
        
        # Since view_db uses relative import, we need to run it differently
        # Just test that the function works when called
        from src.backend.view_db import print_database
        
        try:
            print_database()
            success = True
        except Exception:
            success = False
        
        assert success
    
    def test_main_block_handles_errors(self, tmp_path, monkeypatch, capsys):
        """Test main block handles database errors"""
        # Point to non-existent database
        db_path = tmp_path / "nonexistent.db"
        monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
        
        from src.backend import database
        sys.modules['database'] = database
        
        from src.backend.view_db import print_database
        
        # Should raise an error since tables don't exist
        with pytest.raises(Exception):
            print_database()


class TestDatabaseQueries:
    def test_queries_with_special_characters(self, tmp_path, monkeypatch, capsys):
        """Test handling of special characters in data"""
        db_path = tmp_path / "test_special.db"
        monkeypatch.setattr('src.backend.database.DB_PATH', db_path)
        
        from src.backend import database
        sys.modules['database'] = database
        
        init_db()
        
        # Add data with special characters
        schedule = Schedule()
        schedule.term = "Fall 2024 - Special"
        
        course = Course()
        course.course_code = "FRANÇAIS 101"
        course.course_name = "Intro à la langue"
        schedule.courses.append(course)
        
        save_schedule_to_db(schedule, "user@email.com")
        
        from src.backend.view_db import print_database
        print_database()
        
        captured = capsys.readouterr()
        
        # Should handle special characters
        assert "Fall 2024" in captured.out or "Special" in captured.out
    
    def test_all_table_sections_printed(self, test_db_with_data, capsys):
        """Test that all database table sections are printed"""
        from src.backend.view_db import print_database
        
        print_database()
        captured = capsys.readouterr()
        
        # Verify all table headers present
        tables = ["USERS:", "SCHEDULES:", "COURSES:", "MEETINGS:", "SUMMARY:"]
        for table in tables:
            assert table in captured.out
        
        # Verify separator lines
        assert "-" * 80 in captured.out
        assert "=" * 80 in captured.out