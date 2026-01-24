# Product Backlog - CabbageMeet

## Project Overview

**Project:** CabbageMeet - Smart Schedule Coordination Application  
**Duration:** 3 weeks  
**Team Size:** 5 members (Maya, Kaibo, Angus, Arulini, Meryam)

---

## Backlog Items

### Sprint 1: Foundation & Schedule Management (Week 1)

| ID    | Story                                     | Use Case | Priority    | Points | Assignee | Status    |
| ----- | ----------------------------------------- | -------- | ----------- | ------ | -------- | --------- |
| PBI-1 | Project setup and repository structure    | -        | Must Have   | 2      | Kaibo    | Completed |
| PBI-2 | Database schema design                    | -        | Must Have   | 3      | Kaibo    | Completed |
| PBI-3 | UI design system and wireframes           | -        | Must Have   | 3      | Kaibo    | Completed |
| PBI-4 | Schedule import from Quest paste (UC-1)   | UC-1     | Must Have   | 8      | Maya     | Completed |
| PBI-5 | Schedule validation and parsing           | UC-1     | Must Have   | 5      | Maya     | Completed |
| PBI-6 | Weekly calendar view component (UC-2)     | UC-2     | Must Have   | 5      | Angus    | Completed |
| PBI-7 | Display schedule with color coding (UC-2) | UC-2     | Must Have   | 3      | Meryam   | Completed |
| PBI-8 | Schedule edit functionality               | UC-2     | Should Have | 3      | Meryam   | Completed |
| PBI-9 | Unit tests for schedule import/display    | -        | Must Have   | 3      | Arulini  | Completed |

**Sprint Goal:** Users can import, view, and edit their own schedules

**Total Points:** 35

---

### Sprint 2: Sharing & Comparison (Week 2)

| ID     | Story                                            | Use Case  | Priority    | Points | Assignee | Status    |
| ------ | ------------------------------------------------ | --------- | ----------- | ------ | -------- | --------- |
| PBI-10 | Multiple Schedule management system              | -         | Should Have | 5      | Arulini  | Completed |
| PBI-11 | Multiple schedule selection interface            | UC-3      | Must Have   | 3      | Arulini  | Completed |
| PBI-12 | Schedule overlay and comparison view (UC-3)      | UC-3      | Must Have   | 8      | Angus    | Completed |
| PBI-13 | Common free time identification algorithm (UC-3) | UC-3      | Must Have   | 8      | Meryam   | Completed |
| PBI-14 | Free time highlighting on calendar               | UC-3      | Must Have   | 5      | Meryam   | Completed |
| PBI-15 | Handle no common free time scenario              | UC-3 AF-2 | Should Have | 2      | Kaibo    | Completed |
| PBI-16 | Testing for comparison algorithm                 | -         | Must Have   | 3      | Maya     | Completed |

**Sprint Goal:** Users can share schedules with friends and identify common free time

**Total Points:** 34

---

### Sprint 3: Meeting Suggestions & Polish (Week 3)

| ID     | Story                                       | Use Case | Priority    | Points | Assignee | Status    |
| ------ | ------------------------------------------- | -------- | ----------- | ------ | -------- | --------- |
| PBI-17 | Meeting time suggestion engine (UC-4)       | UC-4     | Must Have   | 8      | Arulini  | Completed |
| PBI-18 | Sort suggestions (UC-4)                     | UC-4     | Must Have   | 3      | Angus    | Completed |
| PBI-19 | Display suggestion details (UC-4)           | UC-4     | Must Have   | 3      | Angus    | Completed |
| PBI-20 | Meeting suggestion filters (UC-5)           | UC-5     | Should Have | 5      | Maya     | Completed |
| PBI-21 | Filter by day, time, duration (UC-5)        | UC-5     | Should Have | 5      | Maya     | Completed |
| PBI-22 | Detailed suggestion view (UC-6)             | UC-6     | Could Have  | 3      | Kaibo    | Completed |
| PBI-23 | Conflict detection and warnings (UC-6 AF-1) | UC-6     | Could Have  | 3      | Arulini  | Completed |
| PBI-24 | UI/UX polish and responsiveness             | -        | Should Have | 5      | Meryam   | Completed |
| PBI-25 | End-to-end testing                          | -        | Must Have   | 5      | All      | Completed |
| PBI-26 | Bug fixes and optimization                  | -        | Must Have   | 5      | All      | Completed |
| PBI-27 | Documentation and demo preparation          | -        | Must Have   | 3      | All      | Completed |

**Sprint Goal:** Implement intelligent meeting suggestions and finalize MVP

**Total Points:** 48

---

## Definition of Done (DoD)

A backlog item is considered "Done" when:

- [ ] Code is written and follows team conventions
- [ ] Code is reviewed by at least one team member
- [ ] Unit tests are written and passing
- [ ] Feature is tested manually against use case flows
- [ ] All alternate flows are handled
- [ ] Code is merged
- [ ] Documentation is updated
- [ ] No critical bugs remain
- [ ] Acceptance criteria from use case are met

---

## Sprint Capacity Planning

**Sprint 1 (Week 1):** 35 story points

- Focus on core schedule management
- Establishes foundation for Sprint 2

**Sprint 2 (Week 2):** 34 story points

- Most complex algorithms (comparison, free time detection)
- Critical for Sprint 3 functionality

**Sprint 3 (Week 3):** 48 story points

- Higher capacity due to team velocity
- Includes buffer time for polish and fixes
- Can deprioritize if needed

---

## Risk Items

| Risk                                      | Impact | Mitigation                                       | Status     |
| ----------------------------------------- | ------ | ------------------------------------------------ | ---------- |
| Quest schedule parsing complexity         | High   | Test with multiple schedule formats early        | Monitoring |
| Algorithm performance with many schedules | Medium | Start with simple implementation, optimize later | Monitoring |
| UC-3 common free time too complex         | High   | Implement basic algorithm in Sprint 2, iterate   | Monitoring |
| Sprint 3 overloaded                       | Medium | PBI-25, PBI-26 marked as "Could Have"            | Monitoring |
| Integration between components            | Medium | Daily integration testing                        | Monitoring |

---

## Sprint Schedule

**Week 1 (Nov 11-15):** Sprint 1

- **Monday:** Sprint planning, setup
- **Tuesday-Thursday:** Development
- **Friday:** Sprint review and retrospective

**Week 2 (Nov 18-22):** Sprint 2

- **Monday:** Sprint planning
- **Tuesday-Thursday:** Development
- **Friday:** Sprint review and retrospective

**Week 3 (Nov 25-29):** Sprint 3

- **Monday:** Sprint planning
- **Tuesday-Wednesday:** Development
- **Thursday:** Final testing and polish
- **Friday:** Demo preparation and presentation

---

## Key Dependencies

**Sprint 1 → Sprint 2:**

- PBI-2 (Database schema) must be complete for PBI-15 (Algorithm)
- PBI-6 (Calendar view) needed for PBI-14 (Overlay view)

**Sprint 2 → Sprint 3:**

- PBI-13 (Free time algorithm) required for PBI-20 (Suggestions)
- PBI-12 (Comparison view) needed for PBI-22 (Display suggestions)

---

## Notes

- All use cases have clear acceptance criteria from use case document
- Alternate flows are tracked as separate PBIs or handled within main PBIs
- Focus on basic flows first, alternate flows if time permits
- UC-6 (detailed view) is lower priority - can be deferred if needed
- Each sprint ends with working, demonstrable features
- Daily standups at 6 PM via team chat
- Code reviews required for all PRs before merge

---

**Document Version:** 2.0
**Last Updated:** December 17, 2024
**Status:** Project Complete - 25/27 PBIs Completed (93%)
