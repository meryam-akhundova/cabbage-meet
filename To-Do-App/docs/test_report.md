# Test Report

## Purpose

This test report summarizes the testing outcomes for the To-Do Application.

## Test Summary

| Level              | Purpose                                               | Result |
| ------------------ | ----------------------------------------------------- | ------ |
| Unit testing       | Test individual functions and web routes in isolation | Passed |
| System Testing     | Test overall application flow through web interface   | Passed |
| Regression Testing | Re-run tests after bug fixes or code changes          | Passed |

## Test Coverage

- Core functions (add(), update(), delete(), next(), today(), tomorrow())
- Core UI components (add task interaction, update task interaction, delete task interaction)
- Data validation tested: duplicate tasks, deletion and updating of nonexistent tasks

## Test Environment

- Python Version: 3.12.11
- Testing tool: Pytest

## Test Result Summary

| Level              | Total                                                 | Result |
| ------------------ | ----------------------------------------------------- | ------ |
| Unit Testing       | Test individual functions and web routes in isolation | Passed |
| System Testing     | Test overall application flow through web interface   | Passed |
| Regression Testing | Re-run tests after bug fixes or code changes          | Passed |

## Detailed Test Case Results

### Unit Testing

| Function   | Test Case                                     | Description                     | Result |
| ---------- | --------------------------------------------- | ------------------------------- | ------ |
| add()      | test_add_new_task                             | Adds a new task with valid data | Passed |
| add()      | test_add_duplicate_task_shows_error           | Attempts to add duplicate task  | Passed |
| delete()   | test_delete_existing_task                     | Deletes a valid task            | Passed |
| delete()   | test_delete_nonexistent_task                  | Tries deleting missing task     | Passed |
| update()   | test_update_existing_task                     | Modifies title & description    | Passed |
| update()   | test_update_nonexistent_task_shows_error      | Updates invalid ID              | Passed |
| update()   | test_update_preserves_started_date            | Checks timestamp not changed    | Passed |
| today()    | test_today_returns_only_tasks_due_today       | Filters today’s tasks           | Passed |
| today()    | test_today_with_empty_list                    | Handles no tasks case           | Passed |
| tomorrow() | test_tomorrow_returns_only_tasks_due_tomorrow | Filters by tomorrow’s date      | Passed |
| tomorrow() | test_tomorrow_skips_tasks_with_no_due_date    | Ignores missing due date tasks  | Passed |
| next()     | test_next_returns_earliest_upcoming_task      | Ignores missing due date tasks  | Passed |
| next()     | test_next_returns_none_if_no_upcoming_tasks   | Handles no upcoming tasks       | Passed |
| next()     | test_next_ignores_done_tasks                  | Skips completed tasks           | Passed |
| next()     | test_next_handles_tasks_due_today             | Includes today’s earliest task  | Passed |

### System Testing (GUI Tests)

| Action                       | Expected Result          | Actual Result           | Result |
| ---------------------------- | ------------------------ | ----------------------- | ------ |
| Click "Add New Task"         | Corresponding page opens | Matches expected result | Passed |
| Click "Add Task"             | Success message appears  | Matches expected result | Passed |
| Click "Update"               | Update Task page opens   | Matches expected result | Passed |
| Click "Update Task"          | Success message appears  | Matches expected result | Passed |
| Click "Delete"               | Success message appears  | Matches expected result | Passed |
| Try to create duplicate task | Error message appears    | Matches expected result | Passed |

## Metrics

- Total Test Cases: 14
- Passed: 14
- Failed: 0
- Success Rate: 100%
- Critical Defects Remaining: 0

## Recommendations

- Implement integration testing
- Implement cross-browser testing

## Conclusion

- All test cases passed successfully
- The application demonstrates stable performance, strong test coverage, and no critical defects

**Document Version:** 1.0
**Created:** 11/10/2025
