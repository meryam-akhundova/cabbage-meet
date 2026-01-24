# Requirements

## Title: Web-Accessible To-Do App

### Add Function

Purpose: To add a non existing task to the To-Do list

Acceptance Criteria:

* The function must include the following parameters:
    * item: Task Name (String)
    * type: Category of the task (String)
    * started: The date and time the task is created (datetime value)
    * due: The date and time the task is due (datetime value)
    * done: The date and time the task is completed (datetime value)
* If a task already exists, it should not be added again. (The task added should not already exist)
* When a task is added, it is stored in a MySQL database.
* The data is reloaded when the application is restarted.
* The user should be informed if the task was added or not.

### Update Function

Purpose: To update an existing task in the To-Do list

Acceptance Criteria:

* The function must include the following parameters:
    * item: Task Name (String)
    * type: Category of the task (String)
    * started: The date and time the task is created (datetime value)
    * due: The date and time the task is due (datetime value)
    * done: The date and time the task is completed (datetime value)
* If a task does not exist, it should not be updated. (Task must exist to be updated)
* When a task is updated, it is updated in the MySQL database.
* The data is reloaded when the application is restarted.
* The user should be informed if the task was updated or not.

### Delete Function

Purpose: To delete an existing task from the To-Do list

Acceptance Criteria:

* The function must include the following parameters:
    * item: Task Name (String)
    * type: Category of the task (String)
    * started: The date and time the task is created (datetime value)
    * due: The date and time the task is due (datetime value)
    * done: The date and time the task is completed (datetime value)
* If a task does not exist, it should not be deleted. (Task must exist to be deleted)
* When a task is deleted, it is deleted from the MySQL database.
* The data is reloaded when the application is restarted.
* The user should be informed if the task was deleted or not.

### Next Function

Purpose: To find the next task in the To-Do list based off of the due date.

Acceptance Criteria:

* The function has no parameters.
* The function must find the next task that has not already been completed based on the due date.
* The function uses the data from the MySQL database.
* If there are no upcoming tasks, user should be informed that no tasks are pending.
* The user should be informed of the next task based off of the due date.

### Today Function

Purpose: To determine the tasks due today.

Acceptance Criteria:

* The function takes in no parameters.
* The function uses the data from the MySQL database.
* If there are no tasks due today, user should be informed that no tasks are due today.
* The user should be informed of all the tasks due today that have not yet been completed.
* If there are tasks due today, returns an array of tasks due today.

### Tommorow Function

Purpose: To determine the tasks due tommorow.

Acceptance Criteria:

* The function takes in no parameters.
* The function uses the data from the MySQL database.
* If there are no tasks due tommorow, the user should be informed that no tasks are due tommorow.
* The user should be informed of all the tasks due tommorow that have not yet been completed.
* If there are tasks due tommorow, returns an array of tasks due tommorow.
