# Test Plan

## Purpose

This test plan ensures that the CabbageMeet application will function correctly and meet the requirements specified in the project charter.

## Scope

### In Scope

- Free time identification algorithm (find_common_free_time, time_to_minutes, minutes_to_time)
- Schedule import functionality (QUEST format and iCalendar format)
- Database operations (insert, retrieve, delete schedules)
- Flask API endpoints (/api/schedules, /api/schedules/icalendar, /api/schedules/{id})
- Schedule comparison and analysis across multiple users
- Edge case handling (overlapping schedules, empty inputs, no free time)
- Input validation and error handling

### Out of Scope

- Frontend user interface automated testing (manual testing only)
- Performance and load testing with many users
- Cross-browser compatibility testing
- Security testing
- Mobile responsiveness testing

## Test Strategy

### Testing Types

- **Static Testing**: Code reviews and syntax checks before execution
- **Dynamic Testing**: Execution of the application with Flask test client

- **Black-box Testing**: Validate external input/output behaviour of API endpoints
- **White-box Testing**: Examine internal algorithm logic and data structures

- **Manual Testing**: Test web interface and user workflows
- **Automated Testing**: Unit and integration tests using pytest

### Test Design Techniques

- **Equivalence Partitioning**: Group similar schedule inputs (valid schedules, empty schedules, invalid formats)
- **Boundary Value Analysis**: Test time boundaries (8:00AM-10:00PM), edge times, minimum durations
- **Decision Table Testing**: Map schedule combinations to expected free time outputs
- **State Transition Testing**: Verify database state changes during CRUD operations
- **Use-Case Testing**: Derive test cases from real student scheduling scenarios
- **Error Guessing**: Anticipate common errors (overlapping classes, invalid times, missing data)

### Test Levels

| Level               | Purpose                                                | When                                      |
| ------------------- | ------------------------------------------------------ | ----------------------------------------- |
| Unit Testing        | Test individual functions (algorithm, time conversion) | During feature development in subbranches |
| Integration Testing | Test API endpoints with database and Flask test client | After backend components completed        |
| System Testing      | Test complete user workflows through web interface     | Throughout development                    |
| Regression Testing  | Re-run tests after bug fixes or code changes           | After each new feature is added           |

### Test Schedule

| Phase               | Dates    |
| ------------------- | -------- |
| Unit Testing        | Week 2-4 |
| Integration Testing | Week 4   |
| System Testing      | Week 4   |
| Regression Testing  | Week 3-5 |

## Test Cases

### Unit Testing - Free Time Algorithm

| Test Case ID | Function                | Test Scenario                   | Input                                    | Expected Output                    |
| ------------ | ----------------------- | ------------------------------- | ---------------------------------------- | ---------------------------------- |
| TC-001       | time_to_minutes()       | Convert AM/PM times to minutes  | "9:00AM", "1:00PM", "11:59PM"            | 540, 780, 1439                     |
| TC-002       | minutes_to_time()       | Convert minutes back to time    | 540, 630, 780                            | "9:00AM", "10:30AM", "1:00PM"      |
| TC-003       | find_common_free_time() | Basic non-overlapping schedules | Two schedules with different class times | Three free time blocks identified  |
| TC-004       | find_common_free_time() | Overlapping class times         | Schedule with nested class times         | Overlaps merged, correct free time |
| TC-005       | find_common_free_time() | Multiple days (M/W/F pattern)   | Schedule across weekdays                 | Correct free time per day          |
| TC-006       | find_common_free_time() | Minimum duration filter         | Schedule with short gaps, 30min minimum  | Only blocks ≥30min returned        |
| TC-007       | find_common_free_time() | No common free time             | One schedule fully busy all day          | Zero free blocks returned          |

### Integration Testing - API Endpoints

| Test Case ID | Endpoint                      | Test Scenario                  | Input                     | Expected Output               |
| ------------ | ----------------------------- | ------------------------------ | ------------------------- | ----------------------------- |
| TC-008       | POST /api/schedules           | Empty schedule text            | `{"scheduleText": "   "}` | 400 Bad Request               |
| TC-009       | POST /api/schedules/icalendar | Empty iCalendar content        | `{"icalContent": ""}`     | 400 Bad Request               |
| TC-010       | GET /api/schedules/{id}       | Retrieve existing schedule     | Valid schedule ID         | 200 OK, correct JSON response |
| TC-011       | GET /api/schedules/{id}       | Retrieve non-existent schedule | Invalid ID (999999)       | 404 Not Found                 |

### System Testing - User Interface

| Test Case ID | Action            | Test Scenario                    | Expected Result                              |
| ------------ | ----------------- | -------------------------------- | -------------------------------------------- |
| TC-012       | Import schedule   | Upload QUEST format schedule     | Schedule successfully imported and displayed |
| TC-013       | Compare schedules | Select multiple users' schedules | Common free time displayed correctly         |
| TC-014       | View schedule     | Display imported schedule        | Classes shown with correct times and days    |

## Pass/Fail Criteria

- **Pass**: Result matches the expected output with no errors, correct free time identified, proper error codes returned
- **Fail**: Incorrect free time calculated, application crashes, wrong HTTP status codes, or data loss occurs

## Entry/Exit Criteria

| Phase               | Entry Criteria                           | Exit Criteria                                   |
| ------------------- | ---------------------------------------- | ----------------------------------------------- |
| Unit Testing        | Algorithm and core functions implemented | All unit tests passed (TC-001 to TC-007)        |
| Integration Testing | API endpoints implemented                | All integration tests passed (TC-008 to TC-011) |
| System Testing      | App is ready to be locally deployed      | User workflows verified (TC-012 to TC-014)      |
| Regression Testing  | Any code change or bug fix completed     | All previous tests still passing                |

## Test Environment

- **Python Version**: 3.12.11
- **Testing Framework**: pytest

## Metrics

- **Test case coverage**: 100% (all planned test cases executed)
- **Code coverage**: ≥80% for core algorithm and backend functions
- **Critical defects remaining**: 0
- **Pass rate target**: ≥95%

---

**Document Version**: 1.0
