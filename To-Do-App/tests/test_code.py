
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pytest

# ensure src is on sys.path so we can import app.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import app as app_module

def _create_tasks_table(db_path):
	# create tasks table matching app usage
	conn = sqlite3.connect(str(db_path))
	conn.execute('''
	CREATE TABLE tasks (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		item TEXT UNIQUE,
		type TEXT,
		started TIMESTAMP,
		due TIMESTAMP,
		done TIMESTAMP
	)
	''')
	conn.commit()
	conn.close()

def test_add_new_task(tmp_path, monkeypatch):
	# create a temporary SQLite database
	db_path = tmp_path / "todo_test.db"
	_create_tasks_table(db_path)

	def get_db_connection():
		conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
		conn.row_factory = sqlite3.Row
		return conn

	monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)

	client = app_module.app.test_client()
	# add a new task
	resp = client.post('/add', data={
		'task': 'Test Task',
		'type': 'general',
		'due_date': '2025-01-01'
	}, follow_redirects=True)

	assert resp.status_code == 200

	# verify the task was inserted
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	row = conn.execute("SELECT item, type FROM tasks WHERE item = ?", ('Test Task',)).fetchone()
	conn.close()

	assert row is not None
	assert row['item'] == 'Test Task'
	assert row['type'] == 'general'

def test_add_duplicate_task_shows_error(tmp_path, monkeypatch):
	# create a temporary SQLite database
	db_path = tmp_path / "todo_test.db"
	_create_tasks_table(db_path)

	def get_db_connection():
		conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
		conn.row_factory = sqlite3.Row
		return conn

	monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)

	client = app_module.app.test_client()

	# insert first time
	resp1 = client.post('/add', data={
		'task': 'Dup Task',
		'type': 'general',
		'due_date': '2025-01-01'
	}, follow_redirects=True)
	assert resp1.status_code == 200

	# attempt to insert duplicate
	resp2 = client.post('/add', data={
		'task': 'Dup Task',
		'type': 'general',
		'due_date': '2025-01-01'
	}, follow_redirects=True)

	# the app flashes an error message when duplicate is detected
	assert resp2.status_code == 200
	assert b"That task already exists" in resp2.data



# Tests if tasks due today are returned.


def test_today_returns_only_tasks_due_today(monkeypatch):
    fixed_today = datetime(2025, 11, 4)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_today

    # Patch datetime in the app module
    monkeypatch.setattr(app_module, "datetime", FixedDateTime)

    today_str = fixed_today.strftime('%Y-%m-%d')
    yesterday_str = (fixed_today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow_str = (fixed_today + timedelta(days=1)).strftime('%Y-%m-%d')

    tasks = [
        {"item": "Task Today 1", "due": today_str},
        {"item": "Task Today 2", "due": today_str},
        {"item": "Task Yesterday", "due": yesterday_str},
        {"item": "Task Tomorrow", "due": tomorrow_str},
        {"item": "Task None", "due": None},
    ]

    result = app_module.today(tasks)

    assert len(result) == 2
    assert all("Task Today" in t["item"] for t in result)


# Test for when there are no tasks due today.

def test_today_with_empty_list():
    """Empty input should return empty list."""
    result = app_module.today([])
    assert result == []

# Checks if tommorow function returns all the tasks due tommorow.

def test_tomorrow_returns_only_tasks_due_tomorrow():
	tomorrow_date = (datetime.now() + timedelta(days=1))
	tasks = [
        {"item": "Task Today", "due": datetime.now().isoformat()},
        {"item": "Task Tomorrow", "due": tomorrow_date.isoformat()},
		{"item": "ALSO TMR", "due": tomorrow_date},
        {"item": "Task Later", "due": (tomorrow_date + timedelta(days=1)).isoformat()},
    ]
	print(tasks)

	result = app_module.tomorrow(tasks)

	assert len(result) == 2
	assert result[0]["item"] == "Task Tomorrow"
	assert result[1]["item"] == "ALSO TMR"

# Checks if the tommorow function skips tasks with no due date.

def test_tomorrow_skips_tasks_with_no_due_date():
    tomorrow_date = (datetime.now() + timedelta(days=1))
    tasks = [
        {"item": "No Due", "due": None},
        {"item": "Tomorrow", "due": tomorrow_date.isoformat()},
    ]

    result = app_module.tomorrow(tasks)

    assert len(result) == 1
    assert result[0]["item"] == "Tomorrow"

def test_next_returns_earliest_upcoming_task():
    from datetime import datetime, timedelta

    # (id, item, type, started, due, done)
    task1 = (1, "Task 1", "general", datetime.now(), datetime.now() + timedelta(days=3), None)
    task2 = (2, "Task 2", "general", datetime.now(), datetime.now() + timedelta(days=1), None)
    task3 = (3, "Task 3", "general", datetime.now(), datetime.now() + timedelta(days=5), None)
    task_list = [task1, task2, task3]

    with app_module.app.test_request_context():
        result = app_module.next(task_list)
        assert result == task2  # earliest due task


def test_next_returns_none_if_no_upcoming_tasks():
    from datetime import datetime, timedelta

    task_past = (1, "Old Task", "general", datetime.now(), datetime.now() - timedelta(days=2), None)
    task_done = (2, "Done Task", "general", datetime.now(), datetime.now() + timedelta(days=1), datetime.now())
    task_list = [task_past, task_done]

    with app_module.app.test_request_context():
        result = app_module.next(task_list)
        assert result is None


def test_next_ignores_done_tasks():
    from datetime import datetime, timedelta

    done_task = (1, "Completed Task", "general", datetime.now(), datetime.now() + timedelta(days=1), datetime.now())
    upcoming_task = (2, "Future Task", "general", datetime.now(), datetime.now() + timedelta(days=2), None)
    task_list = [done_task, upcoming_task]

    with app_module.app.test_request_context():
        result = app_module.next(task_list)
        assert result == upcoming_task


def test_next_handles_tasks_due_today():
    from datetime import datetime, timedelta

    # one task due today, one in the future
    due_today = (1, "Today Task", "general", datetime.now(), datetime.now(), None)
    due_future = (2, "Future Task", "general", datetime.now(), datetime.now() + timedelta(days=2), None)
    task_list = [due_future, due_today]

    with app_module.app.test_request_context():
        result = app_module.next(task_list)
        assert result == due_today  # should prefer today's task

def test_delete_existing_task(tmp_path, monkeypatch):
    db_path = tmp_path / "todo_test.db"
    _create_tasks_table(db_path)

    def get_db_connection():
        conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)
    client = app_module.app.test_client()

    # Insert a task to delete
    conn = sqlite3.connect(str(db_path))
    # Use full datetime strings for started and due
    conn.execute(
        "INSERT INTO tasks (item, type, started, due, done) VALUES (?, ?, ?, ?, ?)",
        ('DeleteMe', 'test', '2024-01-01 00:00:00', '2025-01-01 00:00:00', None)
    )
    conn.commit()
    conn.close()

    # Call delete
    resp = client.post('/delete/', data={'item': 'DeleteMe'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Task deleted successfully!" in resp.data

    # Verify it's gone
    conn = sqlite3.connect(str(db_path))
    row = conn.execute("SELECT * FROM tasks WHERE item = ?", ('DeleteMe',)).fetchone()
    conn.close()
    assert row is None

def test_delete_nonexistent_task(tmp_path, monkeypatch):
    db_path = tmp_path / "todo_test.db"
    _create_tasks_table(db_path)

    def get_db_connection():
        conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)
    client = app_module.app.test_client()

    # Try to delete a task that doesn't exist
    resp = client.post('/delete/', data={'item': 'NotThere'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Task not found." in resp.data


def test_update_existing_task(tmp_path, monkeypatch):
	# create a temporary SQLite database
	db_path = tmp_path / "todo_test.db"
	_create_tasks_table(db_path)

	def get_db_connection():
		conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
		conn.row_factory = sqlite3.Row
		return conn

	monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)

	client = app_module.app.test_client()
	
	# first add a task
	client.post('/add', data={
		'task': 'Original Task',
		'type': 'general',
		'due_date': '2025-01-01'
	})

	# now update it
	resp = client.post('/update/Original Task', data={
		'type': 'urgent',
		'due_date': '2025-02-01'
	})

	assert resp.status_code == 302  # Redirect status code

	# verify the task was updated
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	row = conn.execute("SELECT item, type, due FROM tasks WHERE item = ?", ('Original Task',)).fetchone()
	conn.close()

	assert row is not None
	assert row['item'] == 'Original Task'  # item name should stay the same
	assert row['type'] == 'urgent'  # type should be updated
	assert '2025-02-01' in row['due']  # due date should be updated

def test_update_nonexistent_task_shows_error(tmp_path, monkeypatch):
	# create a temporary SQLite database
	db_path = tmp_path / "todo_test.db"
	_create_tasks_table(db_path)

	def get_db_connection():
		conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
		conn.row_factory = sqlite3.Row
		return conn

	monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)

	client = app_module.app.test_client()

	# attempt to update a task that doesn't exist
	resp = client.post('/update/Nonexistent Task', data={
		'type': 'general',
		'due_date': '2025-01-01'
	})

	# Should redirect back to / with error message
	assert resp.status_code == 302

def test_update_preserves_started_date(tmp_path, monkeypatch):
	# create a temporary SQLite database
	db_path = tmp_path / "todo_test.db"
	_create_tasks_table(db_path)

	def get_db_connection():
		conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
		conn.row_factory = sqlite3.Row
		return conn

	monkeypatch.setattr(app_module, 'get_db_connection', get_db_connection)

	client = app_module.app.test_client()
	
	# add a task
	client.post('/add', data={
		'task': 'Task With Date',
		'type': 'general',
		'due_date': '2025-01-01'
	})

	# get the original started date
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	original_row = conn.execute("SELECT started FROM tasks WHERE item = ?", ('Task With Date',)).fetchone()
	original_started = original_row['started']
	conn.close()

	# update the task
	client.post('/update/Task With Date', data={
		'type': 'updated',
		'due_date': '2025-03-01'
	})

	# verify the started date hasn't changed
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	updated_row = conn.execute("SELECT started FROM tasks WHERE item = ?", ('Task With Date',)).fetchone()
	conn.close()

	assert updated_row['started'] == original_started
