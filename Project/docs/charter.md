# Project Charter

## Title

**CabbageMeet - Smart Schedule Coordination Application**

## Purpose

To develop a web-accessible application where users can import and compare school schedules to find optimal meeting times with friends and classmates.

## Description

Develop a schedule coordination platform inspired by UWflow that allows first-year software engineering students to import their own and others' school schedules, analyze availability, and receive intelligent suggestions for meeting times and hangout opportunities.

## Objectives and Goals

1. Implement schedule import functionality for multiple schedules
2. Create schedule comparison and analysis algorithms
3. Develop meeting time suggestion engine based on overlapping free time
4. Build user-friendly interface for viewing schedules and availability
5. Enable schedule sharing between users
6. Leverage UWflow open source codebase as reference and foundation
7. Deploy functional prototype for student use

## Scope

### In Scope

- User schedule import (manual entry or file upload)
- Schedule storage in database
- Multi-user schedule comparison
- Free time identification algorithm
- Meeting time suggestions based on common availability
- Basic user interface for schedule viewing
- Schedule sharing functionality
- Local development and testing environment

### Out of Scope

- Automated university schedule scraping
- Calendar integration (Google Calendar, Outlook)
- Mobile application
- Real-time notifications
- Event creation and RSVP system
- Location-based suggestions
- Production deployment
- Advanced analytics and insights

## Stakeholders

### Project Team

- **Name** - Responsibilities
- **Maya** - Schedule sharing features, code review
- **Kaibo** - Frontend interface, schedule display
- **Angus** - backend architecture, schedule import
- **Arulini** - Meeting suggestion engine, testing
- **Meryam** - Database design, schedule comparison algorithm

### Users

- Student groups and study teams
- Campus clubs and organizations

## Assumptions

1. Team has access to UWflow repository and can study its architecture
2. Users will manually input or upload their schedules initially
3. All users are willing to share schedule information with selected contacts
4. Web framework knowledge can be learned during development
5. Users have accesss to their class schedules

## Constraints

1. Team consists of first-year students
2. Development timeline constrained to 5 weeks
3. Must leverage open source resources (UWflow) for guidance

## High-Level Risks

| Risk                         | Probability | Impact | Mitigation Strategy                                    |
| ---------------------------- | ----------- | ------ | ------------------------------------------------------ |
| Steep learning curve         | High        | High   | Study UWflow codebase, use LLM assistance              |
| Algorithm complexity         | Medium      | High   | Start with simple time-matching, iterate with testing  |
| Scope creep                  | High        | Medium | Strict feature prioritization, defer advanced features |
| Integration with UWflow code | Medium      | Medium | Study documentation thoroughly, adapt rather than copy |
| Team coordination            | Medium      | Medium | Regular meetings, clear task assignments, Git workflow |

## Authority and Sign-Off

### Decision Authority

- **Team Members**: Feature implementation approaches, code review and approval, enforce quality standards
- **All Team**: Major scope or direction changes require consensus

### Sign-Off Criteria

- Schedule import functionality working
- Schedule comparison algorithm accurately identifies free time
- Meeting suggestions generated based on user availability
- Basic user interface functional and usable
- Core features tested and validated
- Documentation complete for setup and usage
- Code reviewed and approved by team

---

**Document Version:** 1.0  
**Created:** [Current Date]
