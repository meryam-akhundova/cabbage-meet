from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.backend.schedule_parser import parse_quest_schedule, parse_icalendar, ScheduleParseError

from src.backend.database import (
    init_db, save_schedule_to_db, get_schedule_from_db, 
    get_user_schedules
)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    app.config.from_mapping(
        ENV=os.getenv("FLASK_ENV", "production"),
        DEBUG=os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes"),
    )
    
    # Initialize database on app creation
    init_db()

    @app.route("/")
    def index():
        return jsonify({"message": "Hello from backend", "env": app.config.get("ENV")})

    def _handle_import_error(e, error_type="schedule"):
        """Helper to handle import errors consistently."""
        if app.config.get("DEBUG"):
            import traceback
            traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"An error occurred while processing the {error_type}.",
            "details": str(e) if app.config.get("DEBUG") else "Please try again."
        }), 500

    def _process_schedule_import(schedule, user_id, schedule_name=None):
        """Common logic for processing and saving schedules."""
        if not schedule.courses:
            return jsonify({
                "success": False,
                "error": "Invalid format. Please retry.",
                "details": "No courses found."
            }), 400

        # Debug logging
        print(f"DEBUG: schedule_name parameter = '{schedule_name}'")
        print(f"DEBUG: schedule_name is truthy? {bool(schedule_name and schedule_name.strip())}")

        # Use provided name or generate default: "Schedule 1", "Schedule 2", etc.
        if schedule_name and schedule_name.strip():
            schedule.term = schedule_name.strip()
            print(f"DEBUG: Using provided name: '{schedule.term}'")
        else:
            from src.backend.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Count existing schedules to determine next number
            cursor.execute("SELECT COUNT(*) as count FROM schedules")
            count = cursor.fetchone()['count']
            schedule.term = f"Schedule {count + 1}"
            print(f"DEBUG: Generated default name: '{schedule.term}'")

            conn.close()

        schedule_dict = schedule.to_dict()
        db_schedule_id = save_schedule_to_db(schedule, user_id)
        
        return jsonify({
            "success": True,
            "message": "Schedule imported successfully",
            "schedule": schedule_dict,
            "coursesCount": len(schedule.courses),
            "scheduleId": db_schedule_id
        }), 200

    @app.route("/api/schedules", methods=["POST"])
    def import_schedule():
        """Import a schedule from Quest pasted text."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            schedule_text = data.get("scheduleText", "").strip()
            if not schedule_text:
                return jsonify({
                    "success": False,
                    "error": "Invalid format. Please retry.",
                    "details": "Schedule text is empty."
                }), 400
            
            schedule = parse_quest_schedule(schedule_text)
            schedule_name = data.get("scheduleName")
            return _process_schedule_import(schedule, data.get("userId"), schedule_name)

        except ScheduleParseError as e:
            return jsonify({"success": False, "error": "Invalid format. Please retry.", "details": str(e)}), 400
        except Exception as e:
            return _handle_import_error(e, "schedule")

    @app.route("/api/schedules/icalendar", methods=["POST"])
    def import_icalendar():
        """Import a schedule from iCalendar (.ics) file."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            ical_content = data.get("icalContent", "").strip()
            if not ical_content:
                return jsonify({
                    "success": False,
                    "error": "Invalid format. Please retry.",
                    "details": "iCalendar content is empty."
                }), 400
            
            schedule = parse_icalendar(ical_content)
            schedule_name = data.get("scheduleName")
            return _process_schedule_import(schedule, data.get("userId"), schedule_name)

        except ScheduleParseError as e:
            return jsonify({"success": False, "error": "Invalid format. Please retry.", "details": str(e)}), 400
        except Exception as e:
            return _handle_import_error(e, "iCalendar file")

    @app.route("/api/schedules/<int:schedule_id>", methods=["GET"])
    def get_schedule(schedule_id):
        """Get a specific schedule by ID."""
        try:
            schedule = get_schedule_from_db(schedule_id)
            if not schedule:
                return jsonify({"success": False, "error": "Schedule not found"}), 404
            
            return jsonify({"success": True, "schedule": schedule}), 200
        except Exception as e:
            return _handle_import_error(e, "schedule retrieval")

    @app.route("/api/schedules/latest", methods=["GET"])
    def get_latest_schedule():
        """Get the most recently imported schedule."""
        try:
            user_id = request.args.get("userId")
            schedules = get_user_schedules(user_id) if user_id else []
            
            if not schedules:
                # If no user schedules, get the most recent schedule from any user
                import sqlite3
                from src.backend.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT schedule_id FROM schedules ORDER BY created_at DESC LIMIT 1")
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    schedule = get_schedule_from_db(row['schedule_id'])
                    if schedule:
                        return jsonify({"success": True, "schedule": schedule}), 200
                
                return jsonify({"success": False, "error": "No schedules found"}), 404
            
            return jsonify({"success": True, "schedule": schedules[0]}), 200
        except Exception as e:
            return _handle_import_error(e, "schedule retrieval")

    @app.route("/api/courses/<int:course_id>", methods=["DELETE"])
    def delete_course(course_id):
        """Delete a course and its meetings."""
        try:
            from src.backend.database import delete_course_from_db
            success = delete_course_from_db(course_id)
            
            if success:
                return jsonify({"success": True, "message": "Course deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Course not found"}), 404
                
        except Exception as e:
            return _handle_import_error(e, "course deletion")

    @app.route("/api/courses/<int:course_id>", methods=["PUT"])
    def update_course(course_id):
        """Update course information."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            from src.backend.database import update_course_in_db
            success = update_course_in_db(course_id, data)
            
            if success:
                return jsonify({"success": True, "message": "Course updated successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Course not found"}), 404
                
        except Exception as e:
            return _handle_import_error(e, "course update")
        
    @app.route("/api/meetings/<int:course_id>", methods=["DELETE"])
    def delete_meeting(course_id):
        """Delete a specific meeting by day."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            day_of_week = data.get('day_of_week')
            if not day_of_week:
                return jsonify({"success": False, "error": "day_of_week is required"}), 400
            
            from src.backend.database import delete_meeting_from_db
            success = delete_meeting_from_db(course_id, day_of_week)
            
            if success:
                return jsonify({"success": True, "message": "Meeting deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Meeting not found"}), 404
                
        except Exception as e:
            return _handle_import_error(e, "meeting deletion")

    @app.route("/api/personal-events", methods=["GET"])
    def get_personal_events_route():
        """Get all personal events."""
        try:
            user_id = request.args.get("userId")
            from src.backend.database import get_personal_events
            events = get_personal_events(user_id)
            
            return jsonify({"success": True, "events": events}), 200
        except Exception as e:
            return _handle_import_error(e, "personal events retrieval")


    @app.route("/api/personal-events", methods=["POST"])
    def create_personal_event():
        """Create a new personal event."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            required_fields = ['title', 'group_id', 'start_datetime', 'duration']
            for field in required_fields:
                if field not in data:
                    return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
            
            from src.backend.database import save_personal_event
            event_id = save_personal_event(data, data.get('userId'))
            
            return jsonify({
                "success": True,
                "message": "Event created successfully",
                "event_id": event_id
            }), 201
        except Exception as e:
            return _handle_import_error(e, "personal event creation")


    @app.route("/api/personal-events/<int:event_id>", methods=["PUT"])
    def update_personal_event_route(event_id):
        """Update a personal event."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            from src.backend.database import update_personal_event
            success = update_personal_event(event_id, data)
            
            if success:
                return jsonify({"success": True, "message": "Event updated successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Event not found"}), 404
        except Exception as e:
            return _handle_import_error(e, "personal event update")


    @app.route("/api/personal-events/<int:event_id>", methods=["DELETE"])
    def delete_personal_event_route(event_id):
        """Delete a personal event."""
        try:
            from src.backend.database import delete_personal_event
            success = delete_personal_event(event_id)
            
            if success:
                return jsonify({"success": True, "message": "Event deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Event not found"}), 404
        except Exception as e:
            return _handle_import_error(e, "personal event deletion")

    @app.route("/api/task-groups", methods=["GET"])
    def get_task_groups_route():
        """Get all task groups."""
        try:
            user_id = request.args.get("userId")
            from src.backend.database import get_task_groups
            groups = get_task_groups(user_id)
            
            return jsonify({"success": True, "groups": groups}), 200
        except Exception as e:
            return _handle_import_error(e, "task groups retrieval")


    @app.route("/api/task-groups", methods=["POST"])
    def create_task_group():
        """Create a new task group."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            required_fields = ['group_id', 'name', 'color']
            for field in required_fields:
                if field not in data:
                    return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
            
            from src.backend.database import save_task_group
            success = save_task_group(data, data.get('userId'))
            
            return jsonify({
                "success": True,
                "message": "Task group created successfully"
            }), 201
        except Exception as e:
            return _handle_import_error(e, "task group creation")


    @app.route("/api/task-groups/<group_id>", methods=["PUT"])
    def update_task_group_route(group_id):
        """Update a task group."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400
            
            from src.backend.database import update_task_group
            success = update_task_group(group_id, data)
            
            if success:
                return jsonify({"success": True, "message": "Task group updated successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Task group not found"}), 404
        except Exception as e:
            return _handle_import_error(e, "task group update")


    @app.route("/api/task-groups/<group_id>", methods=["DELETE"])
    def delete_task_group_route(group_id):
        """Delete a task group."""
        try:
            from src.backend.database import delete_task_group
            success = delete_task_group(group_id)
            
            if success:
                return jsonify({"success": True, "message": "Task group deleted successfully"}), 200
            else:
                return jsonify({"success": False, "error": "Task group not found"}), 404
        except Exception as e:
            return _handle_import_error(e, "task group deletion")
    
    @app.route("/api/schedules/all", methods=["GET"])
    def get_all_schedules():
        """Get all imported schedules with basic info."""
        try:
            from src.backend.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    s.schedule_id,
                    s.term,
                    s.created_at,
                    COUNT(c.course_id) as course_count
                FROM schedules s
                LEFT JOIN courses c ON s.schedule_id = c.schedule_id
                GROUP BY s.schedule_id
                ORDER BY s.created_at DESC
            ''')
            
            schedules = []
            for row in cursor.fetchall():
                schedules.append({
                    'schedule_id': row['schedule_id'],
                    'term': row['term'],
                    'created_at': row['created_at'],
                    'course_count': row['course_count']
                })
            
            conn.close()
            return jsonify({'success': True, 'schedules': schedules}), 200
        except Exception as e:
            return _handle_import_error(e, "schedules retrieval")


    @app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
    def delete_schedule(schedule_id):
        """Delete an entire schedule with all its courses and meetings."""
        try:
            from src.backend.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT schedule_id FROM schedules WHERE schedule_id = ?', (schedule_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': 'Schedule not found'}), 404
            
            # Delete meetings, courses, then schedule
            cursor.execute('''
                DELETE FROM meetings 
                WHERE course_id IN (SELECT course_id FROM courses WHERE schedule_id = ?)
            ''', (schedule_id,))
            cursor.execute('DELETE FROM courses WHERE schedule_id = ?', (schedule_id,))
            cursor.execute('DELETE FROM schedules WHERE schedule_id = ?', (schedule_id,))
            
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Schedule deleted successfully'}), 200
        except Exception as e:
            return _handle_import_error(e, "schedule deletion")

    @app.route("/api/schedules/<int:schedule_id>/rename", methods=["PATCH"])
    def rename_schedule(schedule_id):
        """Rename a schedule."""
        try:
            data = request.get_json()
            new_name = data.get('name', '').strip()

            if not new_name:
                return jsonify({'success': False, 'error': 'Name cannot be empty'}), 400

            from src.backend.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if schedule exists
            cursor.execute('SELECT schedule_id FROM schedules WHERE schedule_id = ?', (schedule_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': 'Schedule not found'}), 404

            # Update the name
            cursor.execute('UPDATE schedules SET term = ? WHERE schedule_id = ?', (new_name, schedule_id))

            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Schedule renamed successfully', 'name': new_name}), 200
        except Exception as e:
            return _handle_import_error(e, "schedule rename")

    @app.route("/api/meeting-suggestions", methods=["POST"])
    def suggest_meeting_times_endpoint():
        """
        Suggest meeting times based on common free time and preferences.

        Request body:
        {
            "schedule_ids": [1, 2, 3],
            "preferred_days": ["M", "W", "F", "S", "Su"],  // M, T, W, Th, F, S (Sat), Su (Sun)
            "duration_minutes": 60,
            "max_suggestions": 3
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid request. Expected JSON body."}), 400

            schedule_ids = data.get("schedule_ids", [])
            preferred_days = data.get("preferred_days", ["M", "T", "W", "Th", "F", "S", "Su"])
            duration_minutes = data.get("duration_minutes", 60)
            max_suggestions = data.get("max_suggestions", 3)
            start_time_filter = data.get("start_time")  # Optional, e.g., "09:00"
            end_time_filter = data.get("end_time")      # Optional, e.g., "17:00"

            if not schedule_ids:
                return jsonify({
                    "success": False,
                    "error": "schedule_ids required"
                }), 400

            # Use existing helper function to get free times
            from src.backend.free_time_algorithm import get_free_time_for_schedule_ids, suggest_meeting_times
            from datetime import datetime, timedelta

            # Calculate this week's date range
            today = datetime.now().date()
            # Get Monday of this week
            days_since_monday = (today.weekday()) % 7  # Monday = 0
            week_start = today - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)  # Sunday

            # Get all common free time for this week
            free_times = get_free_time_for_schedule_ids(
                schedule_ids,
                options={
                    'min_duration': duration_minutes,
                }
            )

            # Filter and get top suggestions
            suggestions = suggest_meeting_times(
                free_times,
                preferred_days,
                duration_minutes,
                max_suggestions,
                start_time_filter,
                end_time_filter
            )

            return jsonify({
                "success": True,
                "suggestions": suggestions,
                "total_available": len([
                    block for block in free_times
                    if block['day'] in preferred_days and block['duration_minutes'] >= duration_minutes
                ]),
                "week_range": {
                    "start": week_start.isoformat(),
                    "end": week_end.isoformat()
                }
            }), 200

        except Exception as e:
            return _handle_import_error(e, "meeting suggestion")

    return app


def _main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT", "5000"))
    except (TypeError, ValueError):
        port = 5000
    debug = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    app = create_app()
    print(f"Starting Flask app on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    _main()
