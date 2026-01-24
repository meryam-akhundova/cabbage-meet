# Use Cases - CabbageMeet

## UC-1: Import Personal Schedule

**ID:** UC-1  
**Related User Story:** US-1.1  
**Priority:** High

### Actors

- Student (Primary)
- System

### Preconditions

- User has access to their class schedule

### Basic Flow

1. User navigates to the "Import Schedule" page
2. User clicks on "Upload Schedule" button
3. User pastes schedule information from Quest
4. System validates format
5. System parses schedule data (course code, days, times, location)
6. System displays success confirmation message
7. System redirects user to schedule view page

### Alternate Flows

**AF-1: Invalid Format**

- At step 5, if format is invalid:
  - System displays error message: "Invalid format. Please retry."
  - System returns to step 3

### Postconditions

- User's schedule is saved in the database
- Schedule is available for viewing and comparison

### Business Rules

- Schedule file must be in expected format

---

## UC-2: View Personal Schedule

**ID:** UC-2  
**Related User Story:** US-1.2  
**Priority:** High

### Actors

- Student (Primary)
- System

### Preconditions

- User has imported at least one schedule

### Basic Flow

1. User navigates to "My Schedules" page
2. System retrieves user's schedule from database
3. System displays schedule in weekly grid view
4. System shows each class with course code, time, and location
5. System applies color coding to distinguish different courses
6. System highlights free time blocks
7. User views their weekly schedule

### Alternate Flows

**AF-1: No Schedule Exists**

- At step 2, if user has no schedule:
  - System displays message: "You haven't imported a schedule yet."
  - System provides "Import Schedule" button
  - User can click button to go to UC-1

**AF-2: Mobile View**

- At step 3, if user is on mobile device:
  - System displays responsive, scrollable calendar view
  - System adjusts font sizes and spacing for readability

### Postconditions

- User has viewed their schedule
- User can proceed to share or compare schedules

### Business Rules

- Schedule displays Monday through Friday
- Time slots display from 8:00 AM to 10:00 PM
- Each course uses a unique color
- Free time is displayed as white/empty blocks

---

## UC-3: Compare Multiple Schedules

**ID:** UC-3  
**Related User Story:** US-2  
**Priority:** Medium

### Actors

- Student (Primary)
- System

### Preconditions

- User has imported multiple schedules

### Basic Flow

1. User navigates to "Compare Schedules" page
2. System displays user's schedules
3. User selects schedules from the list
4. System retrieves selected schedules from database
5. System overlays all schedules on a single calendar view
6. System assigns distinct colors to each person's classes
7. System analyzes and highlights common free time slots
8. User views the combined schedule comparison

### Alternate Flows

**AF-2: No Common Free Time**

- At step 7, if there are no common free time slots:
  - System displays message: "No common free time found for selected group."
  - System suggests using the "Meeting Time Suggestions" feature with flexible options

### Postconditions

- User has viewed comparison of multiple schedules
- Common free time slots are identified
- User can proceed to UC-4 for detailed meeting suggestions

### Business Rules

- Common free time requires all selected users to be available
- Minimum common free block is 30 minutes

---

## UC-4: Get Meeting Time Suggestions

**ID:** UC-4  
**Related User Story:** US-3.1  
**Priority:** High

### Actors

- Student/Study Group Member (Primary)
- System

### Preconditions

- User has selected at least two schedule for comparison (from UC-3)
- There are multiple schedules to compare

### Basic Flow

1. User clicks "Get Meeting Suggestions" button from schedule comparison view
2. System analyzes all selected users' schedules
3. System identifies all time slots where all participants are free
4. System calculates duration of each available time slot
5. System sorts suggestions by longest available duration
6. System displays list of meeting time suggestions with:
   - Day of week
   - Start and end time
   - Duration
   - List of available participants
7. User reviews meeting time suggestions

### Alternate Flows

**AF-1: Specify Minimum Duration**

- At step 1, user sets minimum meeting duration (e.g., 30 min, 1 hour, 2 hours):
  - System filters results to only show time slots meeting minimum duration

**AF-2: No Available Time Slots**

- At step 3, if no common free time exists:
  - System displays message: "No common free time found for the selected group."
  - System suggests:
    - Reducing the number of people in the group
    - Using the filter feature to search specific days/times
    - Making some participants optional

### Postconditions

- User has received list of suggested meeting times
- Suggestions are sorted by duration
- User can apply filters (UC-5) or view details (UC-6)

### Business Rules

- Minimum time slot duration is 30 minutes
- Only time slots where ALL selected users are free are suggested
- Time slots must be between 8:00 AM and 10:00 PM
- Suggestions are sorted longest to shortest duration

---

## UC-5: Filter Meeting Suggestions

**ID:** UC-5  
**Related User Story:** US-3.2  
**Priority:** Medium

### Actors

- Student (Primary)
- System

### Preconditions

- User has generated meeting time suggestions (UC-4)
- Suggestions list is displayed

### Basic Flow

1. User clicks "Filter Options" button
2. System displays filter panel with options:
   - Days of week checkboxes (Mon-Fri)
   - Time range sliders (start time, end time)
   - Minimum duration dropdown (30 min, 1 hour, 2 hours, 3+ hours)
3. User selects desired filter criteria
4. System applies filters in real-time
5. System updates suggestions list to show only matching results
6. System displays count of filtered results
7. User reviews filtered suggestions

### Alternate Flows

**AF-1: No Results Match Filters**

- At step 5, if no suggestions match the filter criteria:
  - System displays message: "No meeting times match your filters."
  - System suggests relaxing filter criteria
  - System provides "Reset Filters" button

**AF-2: Save Filter Preferences**

- At step 7, user clicks "Save Preferences":
  - System saves filter settings to user profile
  - System applies these filters by default in future sessions
  - System displays confirmation: "Filter preferences saved."

**AF-3: Reset Filters**

- At any step, user clicks "Reset Filters":
  - System clears all filter selections
  - System displays all available meeting times
  - System reverts to default sorting (longest duration first)

### Postconditions

- Meeting suggestions are filtered based on user preferences
- Filter settings are applied to current view
- User can save preferences for future use

### Business Rules

- Multiple days can be selected simultaneously
- Time range must have start time before end time
- Minimum duration cannot exceed longest available slot
- Saved preferences persist across sessions
- Filters apply to all participants' availability

---

## UC-6: View Meeting Suggestion Details

**ID:** UC-6  
**Related User Story:** US-3.3  
**Priority:** Low

### Actors

- Student (Primary)
- System

### Preconditions

- User has generated meeting time suggestions (UC-4)
- Suggestions list is displayed

### Basic Flow

1. User clicks on a specific meeting time suggestion from the list
2. System retrieves detailed information for that time slot
3. System displays expanded view showing:
   - Day and full date
   - Start and end time
   - Total duration
   - List of all available participants
   - Conflicts (if any participant has back-to-back classes)
4. User clicks "View on Calendar" button
5. System highlights the selected time slot on calendar view
6. System shows all participants' schedules during that time
7. User reviews the detailed information

### Alternate Flows

**AF-1: Participant Has Conflict**

- At step 3, if any participant has class immediately before or after:
  - System displays warning icon next to participant's name
  - System shows message: "[Name] has a class ending at [time] / starting at [time]"
  - System indicates potential tight timing

**AF-2: Close Details View**

- At any step, user clicks "Back" or "Close":
  - System returns to suggestions list view
  - System maintains current filter settings

**AF-3: Select Different Time Slot**

- At step 7, user clicks on different suggestion:
  - System updates details view with new time slot information
  - System does not require returning to list view

### Postconditions

- User has reviewed detailed information about meeting time
- User can make informed decision about scheduling
- User can return to suggestions list or calendar view

### Business Rules

- Conflicts are defined as classes within 15 minutes before/after time slot
- Calendar view highlights selected time slot in neutral color
- All participants shown in details must be available during entire slot
- Duration displayed in both hours and minutes (e.g., "2h 30min")

---

## Use Case Relationships

### Dependencies

- UC-3 depends on UC-1 (users must import schedules before comparing)
- UC-4 depends on UC-3 (meeting suggestions require schedule comparison)
- UC-5 depends on UC-4 (filtering requires existing suggestions)
- UC-6 depends on UC-4 (viewing details requires existing suggestions)

### Optional Flows

- UC-2 can be performed independently to view own schedule
- UC-5 and UC-6 enhance UC-4 but are not required

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025
