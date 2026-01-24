# Test Plan

## Purpose

This test plan ensures that the To-Do application will function correctly and meet the requirements.

## Scope

### In Scope

- Six core functions: add(), update(), delete(), next(), today(), tomorrow()
- Database operations (insert, update, delete, select) with userid filtering ('WHERE userid = CURRENT_USER)
- Flask web routes of the core functions
- HTML forms and page rendering
- Error handling and input validation

### Out of Scope

- Performance and load testing
- Cross-browser compatibility testing

## Test Strategy

### Testing Types

- Static Testing: Code reviews and syntax checks before running
- Dynamic Testing: Execution of the application in Flask

- Black-box Testing: Focus on validating external input/output behaviour of web routes
- White-box Testing: Focus on examining internal code

- Manual Testing: Test form submissions
- Automated Testing: Unit tests using pytest

### Test Design Techniques

- Equivalence Partitioning: Group inputs into valid and invalid classes and test one representative from each
- Boundary Value Analysis: Test edge cases at the boundaries of valid and invalid input ranges
- Decision Table Testing: Map conditions to expected outcomes
- State Transition Testing: Verify correct behavior when transitioning between application states
- Use-Case Testing: Derive test cases directly from user actions
- Error Guessing: Anticipate and test for common user or system errors

### Test Levels

| Level              | Purpose                                               | When                                      |
| ------------------ | ----------------------------------------------------- | ----------------------------------------- |
| Unit testing       | Test individual functions and web routes in isolation | During feature development in subbranches |
| System Testing     | Test overall application flow through web interface   | Throughout development                    |
| Regression Testing | Re-run tests after bug fixes or code changes          | After each new feature is added           |

### Test Schedule

| Phase              | Dates          |
| ------------------ | -------------- |
| Unit Testing       | November 3 - 7 |
| System Testing     | November 10    |
| Regression Testing | November 3-10  |

## Pass/Fail Criteria

- Pass: Result matches the expected output with no errors
- Fail: Incorrect data is displayed, application crashes, or userid filtering is incorrect

## Entry/Exit Criteria

| Phase              | Entry Criteria                      | Exit Criteria                |
| ------------------ | ----------------------------------- | ---------------------------- |
| Unit Testing       | All functions implemented           | All unit tests passed        |
| System Testing     | App is ready to be locally deployed | Application flow is verified |
| Regression Testing | Testing phase has begun             | Testing phase has ended      |

## Resources

- Tools: Pytest, Flask, SQL
- Testers: Project team members

## Metrics

- Test case coverage (Percentage of test cases executed): 100%
- Code coverage (Percentage of code executed by tests): ≥ 80%

**Document Version:** 1.1  
**Created:** 11/02/2025
