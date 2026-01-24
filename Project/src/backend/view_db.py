"""
View database contents for CabbageMeet.

This script prints all data from the database in a readable format.
"""

from database import get_db_connection


def print_database():
    """Print all database contents."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("CABBAGEMEET DATABASE CONTENTS")
    print("=" * 80)
    print()
    
    # Print users
    print("USERS:")
    print("-" * 80)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"  User ID: {user['user_id']}")
            print(f"  Name: {user['name']}")
            print(f"  Email: {user['email'] or 'N/A'}")
            print(f"  Created: {user['created_at']}")
            print()
    else:
        print("  No users found.")
    print()
    
    # Print schedules
    print("SCHEDULES:")
    print("-" * 80)
    cursor.execute("SELECT * FROM schedules")
    schedules = cursor.fetchall()
    if schedules:
        for schedule in schedules:
            print(f"  Schedule ID: {schedule['schedule_id']}")
            print(f"  User ID: {schedule['user_id'] or 'N/A'}")
            print(f"  Term: {schedule['term'] or 'N/A'}")
            print(f"  Created: {schedule['created_at']}")
            print(f"  Updated: {schedule['updated_at']}")
            print()
    else:
        print("  No schedules found.")
    print()
    
    # Print courses
    print("COURSES:")
    print("-" * 80)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    if courses:
        for course in courses:
            print(f"  Course ID: {course['course_id']}")
            print(f"  Schedule ID: {course['schedule_id']}")
            print(f"  Course Code: {course['course_code']}")
            print(f"  Course Name: {course['course_name'] or 'N/A'}")
            print(f"  Class #: {course['class_number'] or 'N/A'}")
            print(f"  Section: {course['section'] or 'N/A'}")
            print(f"  Component: {course['component'] or 'N/A'}")
            print(f"  Units: {course['units'] or 'N/A'}")
            print(f"  Status: {course['status'] or 'N/A'}")
            print()
    else:
        print("  No courses found.")
    print()
    
    # Print meetings
    print("MEETINGS:")
    print("-" * 80)
    cursor.execute("SELECT * FROM meetings")
    meetings = cursor.fetchall()
    if meetings:
        for meeting in meetings:
            print(f"  Meeting ID: {meeting['meeting_id']}")
            print(f"  Course ID: {meeting['course_id']}")
            print(f"  Day: {meeting['day_of_week']}")
            print(f"  Time: {meeting['start_time'] or 'N/A'} - {meeting['end_time'] or 'N/A'}")
            print(f"  Location: {meeting['location'] or 'N/A'}")
            print(f"  Instructor: {meeting['instructor'] or 'N/A'}")
            print(f"  Dates: {meeting['start_date'] or 'N/A'} to {meeting['end_date'] or 'N/A'}")
            print()
    else:
        print("  No meetings found.")
    print()
    
    # Print summary statistics
    print("SUMMARY:")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM schedules")
    schedule_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM courses")
    course_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM meetings")
    meeting_count = cursor.fetchone()['count']
    
    print(f"  Total Users: {user_count}")
    print(f"  Total Schedules: {schedule_count}")
    print(f"  Total Courses: {course_count}")
    print(f"  Total Meetings: {meeting_count}")
    print()
    
    conn.close()
    print("=" * 80)


if __name__ == "__main__":
    try:
        print_database()
    except Exception as e:
        print(f"Error reading database: {e}")
        import traceback
        traceback.print_exc()

