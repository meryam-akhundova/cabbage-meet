# User Stories - CabbageMeet

## Epic 1: Schedule Management

### US-1.1: Import Personal Schedule

**As a** student  
**I want to** import my class schedule into the application  
**So that** I can share my availability with friends and find common meeting times

**Acceptance Criteria:**

- User can upload schedule (CSV or similar format)
- Schedule is validated for correct time format
- Schedule is saved to user's profile
- User receives confirmation of successful import

**Priority:** High  
**Story Points:** 5

---

### US-1.2: View My Schedule

**As a** student  
**I want to** view my weekly schedule in a calendar format  
**So that** I can verify my schedule is correct and see my commitments at a glance

**Acceptance Criteria:**

- Schedule displays in weekly grid view
- Each class shows course code, time, and location
- Color coding distinguishes different courses
- Free time blocks are clearly visible
- Schedule is responsive and readable on different screen sizes

**Priority:** High  
**Story Points:** 3

---

## Epic 2: Schedule Sharing and Comparison

### US: Compare Multiple Schedules

**As a** student  
**I want to** compare schedules of multiple friends simultaneously  
**So that** I can find times when our entire group is available

**Acceptance Criteria:**

- User can select up to 5 friends to compare
- All selected schedules overlay on single calendar view
- Each person's classes use distinct colors
- Common free time slots across all users are highlighted
- Legend shows which color represents each person

**Priority:** Medium  
**Story Points:** 8

---

## Epic 3: Meeting Time Suggestions

### US-3.1: Get Meeting Time Suggestions

**As a** student / study group member
**I want to** receive suggestions for meeting times  
**So that** I don't have to manually search through schedules

**Acceptance Criteria:**

- System identifies all time slots where selected users are free
- Suggestions show day, time, and duration of availability
- Suggestions are sorted by longest available duration
- Minimum meeting duration can be specified (e.g., 30 min, 1 hour)
- Results update when different friends are selected

**Priority:** High  
**Story Points:** 8

---

### US-3.2: Filter Meeting Suggestions

**As a** student  
**I want to** filter meeting suggestions by day and time preferences  
**So that** I can find times that work best for my study habits

**Acceptance Criteria:**

- User can filter by specific days of week
- User can set preferred time ranges (e.g., mornings only)
- User can set minimum duration for meetings
- Filtered results update in real-time
- User can save filter preferences

**Priority:** Medium  
**Story Points:** 5

---

### US-3.3: View Meeting Suggestion Details

**As a** student  
**I want to** see detailed information about suggested meeting times  
**So that** I can make informed decisions about when to meet

**Acceptance Criteria:**

- Each suggestion shows all participants who are available
- Shows duration of available time slot
- Shows conflicts
- Provides option to view on calendar

**Priority:** Low  
**Story Points:** 3

---

## Non-Functional Requirements

### NFR-1: Performance

**As a** user  
**I want to** receive meeting suggestions within 2 seconds  
**So that** the application feels responsive and fast

---

### NFR-2: Usability

**As a** first-time user  
**I want to** understand how to use the application without extensive instructions  
**So that** I can start coordinating schedules quickly

---

### NFR-3: Data Security

**As a** user  
**I want to** know my schedule data is secure  
**So that** I can trust the application with my personal information

---

## Story Priority Matrix

### Must Have (MVP)

- US-1.1: Import Personal Schedule
- US-1.2: View My Schedule
- US-3.1: Get Meeting Time Suggestions

### Should Have

- US-2: Compare Multiple Schedules
- US-3.2: Filter Meeting Suggestions

### Could Have

- US-3.3: View Meeting Suggestion Details

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025
