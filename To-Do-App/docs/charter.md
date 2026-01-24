# Project Charter

# Title: Web-Accessible To-Do App

## Title

# Purpose

**Web-Accessible To-Do Application Project**

To develop a web-accessible application where users can organize
their tasks efficiently.

## Description

# Objectives

Develop a Flask-based web interface for the existing To-Do application to enable browser-based task management with database persistence and user isolation.

Implement features that allows users to add, update, delete, and view upcoming tasks
that are filtered by day.
Ensure that tasks are stored in a secure database.
Prepare the application for future multi-user support by adding user IDs.

## Objectives and Goals

# Scope

1. Implement Flask web framework with local web server
2. Create web routes and interfaces for six core functions: add(), update(), delete(), next(), today(), tomorrow()
3. Modify database schema to add userid field for user isolation
4. Ensure all database operations filter by userid using `WHERE userid = CURRENT_USER`
5. Develop comprehensive test plan and test cases
6. Execute parallel development with Git branching and peer review workflow

Basic features such as adding, updating, deleting, and viewing tasks.
Database integration.
Local login support.
Local-only web setup using Flask.

## Scope

# Stakeholders

#### In Scope

Developers
Users

- Flask installation and configuration
- Six web-accessible functions with HTML forms
- Database schema modification (add userid column)
- SQL queries with userid filtering
- HTML templates for user interactions
- Local web server deployment
- Test plan and test cases
- Git branching strategy with subbranches per function
- Peer review process

#### Out of Scope

- User authentication/login system
- Production deployment
- Mobile-responsive design
- JavaScript frameworks
- Performance optimization
- Task sharing features

## Project Organization

### Project Team

- **Name** - Responsibilities
- **Maya** - Setup, coordination, delete() function
- **Kaibo** - update() function
- **Angus** - add() function, approving MR for functions
- **Arulini** - next() function, test cases for functions
- **Meryam** - today(), tomorrow() functions

### Users

- Development team members

## Assumptions

1. Python 3.8+ and pip are installed on all machines
2. Database can be modified (ALTER TABLE permissions)
3. CURRENT_USER function available in database
4. Port 5000 available for Flask development server
5. Database-level user isolation acceptable for Phase 1

## Constraints

1. Must use Flask framework
2. Local-only deployment (no production hosting)
3. Team size fixed at 5 people
4. Must follow prescribed Git branching workflow
5. All code requires peer review before merge
6. Separate developer and tester for each function
7. Final approval required from d3feng

## High-Level Risks

| Risk                    | Probability | Impact | Mitigation Strategy                            |
| ----------------------- | ----------- | ------ | ---------------------------------------------- |
| Flask learning curve    | High        | Medium | Use LLM assistance, start with simple examples |
| Merge conflicts         | Medium      | Medium | Frequent communication, regular pulls          |
| User isolation failures | Low         | High   | Mandatory SQL query review, security testing   |
| Incomplete testing      | Medium      | High   | Dedicated tester, test-driven development      |
| Timeline delays         | Medium      | Medium | Parallel development, clear assignments        |

## Authority and Sign-Off

### Decision Authority

- **Reviewers**: Approve/reject merge requests, enforce quality standards
- **d3feng**: Accept/reject final merge request, approve completion

### Sign-Off Criteria

- All six functions implemented with web routes
- All database operations include userid filtering
- Code reviewed and approved
- Tests passed
- All subbranches merged to `feature/web-todo-app`
- Merge request submitted to d3feng

---

**Document Version:** 1.0  
**Created:** 10/28/2025
