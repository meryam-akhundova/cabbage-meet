from flask import Flask, request, redirect, render_template, flash, url_for
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # ✅ Must be right after app = Flask(...)

def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn  # <-- fix: was 'conns'

def parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None

def format_date(value):
    dt = parse_datetime(value)
    return dt.strftime('%Y-%m-%d') if dt else None

def format_datetime(value):
    dt = parse_datetime(value)
    return dt.strftime('%Y-%m-%d %H:%M') if dt else None

@app.route('/')
def index():
    conn = get_db_connection()
    raw_tasks = conn.execute("SELECT * FROM tasks ORDER BY due IS NULL, due").fetchall()
    conn.close()

    tasks = [dict(task) for task in raw_tasks]

    def prepare_task_display(task):
        prepared = dict(task)
        prepared['due_display'] = format_date(prepared.get('due'))
        prepared['started_display'] = format_datetime(prepared.get('started'))
        return prepared

    tasks_today = [prepare_task_display(task) for task in today(tasks)]
    tasks_tomorrow = [prepare_task_display(task) for task in tomorrow(tasks)]
    all_tasks = [prepare_task_display(task) for task in tasks]

    tuple_tasks = []
    for task in tasks:
        due_dt = parse_datetime(task.get('due'))
        if due_dt is None:
            continue
        tuple_tasks.append(
            (
                task.get('id'),
                task.get('item'),
                task.get('type'),
                parse_datetime(task.get('started')),
                due_dt,
                parse_datetime(task.get('done')),
            )
        )

    next_task_entry = next(tuple_tasks) if tuple_tasks else None
    next_task_display = None
    if next_task_entry:
        keys = ['id', 'item', 'type', 'started', 'due', 'done']
        next_task_dict = dict(zip(keys, next_task_entry))
        next_task_display = prepare_task_display(next_task_dict)

    return render_template(
        'index.html',
        tasks=all_tasks,
        tasks_today=tasks_today,
        tasks_tomorrow=tasks_tomorrow,
        next_task=next_task_display,
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        item = request.form['task']
        type = request.form['type']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')

        conn = get_db_connection()

        # 🔍 Check if this item already exists
        existing = conn.execute("SELECT * FROM tasks WHERE item = ?", (item,)).fetchone()
        if existing:
            flash("That task already exists. Please use a different name.", "error")
            conn.close()
            return redirect('/add')

        # ✅ Insert the new task
        conn.execute(
            "INSERT INTO tasks (item, type, started, due, done) VALUES (?, ?, ?, ?, ?)",
            (item, type, datetime.now(), due_date, None)
        )
        conn.commit()
        conn.close()

        flash("Task added successfully!", "success")
        return redirect('/')
    else:
        return render_template('add.html')

def today(task_list):
    """Return all tasks due today."""
    today_date = datetime.now().date()  # Will be patched in test

    tasks_due_today = []
    for task in task_list:
        due_val = task['due']
        if not due_val:
            continue

        # handle both str and datetime types
        if isinstance(due_val, str):
            due_date = datetime.fromisoformat(due_val).date()
        elif isinstance(due_val, datetime):
            due_date = due_val.date()
        else:
            continue

        if due_date == today_date:
            tasks_due_today.append(task)

    return tasks_due_today


def tomorrow(task_list):
    """
    Return all tasks due tomorrow.
    Expects task_list to be a list of sqlite3.Row objects with a 'due' column.
    """
    tomorrow_date = (datetime.now() + timedelta(days=1)).date()

    tasks_due_tomorrow = []
    for task in task_list:
        due_val = task['due']
        if due_val is None:
            continue

        due_date_obj = None

        # If the value is already a datetime
        if isinstance(due_val, datetime):
            due_date_obj = due_val.date()
        # If the value is a string, prefer ISO format (from datetime.isoformat()), with a small fallback
        elif isinstance(due_val, str):
            # Handles strings produced by datetime.isoformat(), including optional microseconds and offsets
            due_date_obj = datetime.fromisoformat(due_val).date()
        if due_date_obj is not None and due_date_obj == tomorrow_date:
            tasks_due_tomorrow.append(task)

    return tasks_due_tomorrow

# Returns the next pending task based on the due date.

def next(task_list):

   # Determines today's date.

    today = datetime.now().date() 

    # Filters tasks that aren't done and are due today or in the future.

    upcoming_tasks = [ 
    task for task in task_list  
    if task[5] is None and task[4].date() >= today 
    ] 
    
    # Returns None if there are no upcoming tasks.

    if not upcoming_tasks: 
        flash("No upcoming tasks!", "error")
        return None 
    
    # Sort by due date and return the earliest one 

    upcoming_tasks.sort(key=lambda t: t[4]) 
    flash("Next task found successfully!", "success")

    return upcoming_tasks[0] 

@app.route('/delete/', methods=['POST']) 
def delete():
    """Delete a task by item name"""
    item = request.form['item']
    conn = get_db_connection()

    # Check if task exists
    existing = conn.execute("SELECT * FROM tasks WHERE item = ?", (item,)).fetchone()
    if not existing:
        flash("Task not found.", "error")
        conn.close()
        return redirect('/')

    # Delete the task
    conn.execute("DELETE FROM tasks WHERE item = ?", (item,))
    conn.commit()
    conn.close()

    flash("Task deleted successfully!", "success")
    return redirect('/')


@app.route('/update/<item>', methods=['GET', 'POST'])
def update(item):
    """Update an existing task's type and due date"""
    conn = get_db_connection()

    if request.method == 'POST':
        new_type = request.form['type']
        new_due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')

        # Check if task exists
        existing = conn.execute("SELECT * FROM tasks WHERE item = ?", (item,)).fetchone()
        if not existing:
            flash("Task not found.", "error")
            conn.close()
            return redirect('/')

        # Update the task
        conn.execute(
            "UPDATE tasks SET type = ?, due = ? WHERE item = ?",
            (new_type, new_due_date, item)
        )
        conn.commit()
        conn.close()

        flash("Task updated successfully!", "success")
        return redirect('/')
    else:
        # GET request - show the update form
        task = conn.execute("SELECT * FROM tasks WHERE item = ?", (item,)).fetchone()
        conn.close()

        if not task:
            flash("Task not found.", "error")
            return redirect('/')

        due_value = format_date(task['due'])

        return render_template('update.html', task=task, due_date_value=due_value)
    
