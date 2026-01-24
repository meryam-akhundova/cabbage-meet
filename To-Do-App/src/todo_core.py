# todo_core.py
from datetime import datetime, timedelta

def add(task_list, item, type, due):
    # Check uniqueness
    for t in task_list:
        if t[0] == item:
            raise ValueError("Item already exists")
    started = datetime.now()
    done = None
    task_list.append((item, type, started, due, done))
    return task_list

def delete(task_list, item):
    """Remove a task from the task list by item name."""
    for i, task in enumerate(task_list):
        if task[0] == item:
            task_list.pop(i)
            return task_list
    raise ValueError("Item not found")
