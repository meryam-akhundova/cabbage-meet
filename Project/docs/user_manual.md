# CabbageMeet User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Importing Schedules](#importing-schedules)
4. [Managing Your Schedules](#managing-your-schedules)
5. [Creating Personal Events](#creating-personal-events)
6. [Finding Meeting Times](#finding-meeting-times)
7. [Calendar Views](#calendar-views)
8. [Tips and Tricks](#tips-and-tricks)

---

## Introduction

**CabbageMeet** is a calendar and scheduling application designed to help students and teams:
- Import course schedules from Quest or iCalendar files
- Manage multiple schedules (e.g., different terms, co-op schedules)
- Create personal events and tasks
- Find common free time across multiple schedules for team meetings
- View schedules in Day, Week, Month, and Year views

---

## Getting Started

### Launching the Application

1. **Start the Backend**

   macOS / Linux:
   ```bash
   .venv/bin/python src/backend/main.py
   ```

   Windows:
   ```powershell
   .\.venv\Scripts\python.exe src\backend\main.py
   ```

2. **Start the Frontend**

   ```bash
   npm run dev
   ```

3. **Open in Browser**

   Navigate to: `http://localhost:5173`

The backend runs on port 5000, and the frontend on port 5173.

---

## Importing Schedules

CabbageMeet supports two import methods:

### Method 1: Quest Paste Import

1. Click **"Import Calendar"** in the top toolbar
2. Enter a name for your schedule (e.g., "Winter 2024", "Fall 2025 Co-op")
3. Select the **"Quest Paste"** tab
4. Copy your entire course schedule from Quest (select all and copy)
5. Paste it into the text area
6. Click **"Import Schedule"**

The app will parse your courses and add them to your calendar.

### Method 2: iCalendar File Import

1. Click **"Import Calendar"**
2. Enter a name for your schedule
3. Select the **"iCalendar File"** tab
4. Click **"Choose iCalendar File"** and select your `.ics` file
5. The schedule will be imported automatically

### What Gets Imported

- Course codes and names
- Lecture, lab, and tutorial times
- Days of the week
- Start and end dates
- Locations and instructors

---

## Managing Your Schedules

### Viewing Imported Schedules

All imported schedules appear in the **"Imported Schedules"** section in the left sidebar. Each schedule shows:
- Schedule name
- Number of courses
- List of courses (click the arrow to expand/collapse)

### Renaming a Schedule

1. **Double-click** on the schedule name in the sidebar
2. Type the new name
3. Press **Enter** to save, or **Esc** to cancel

### Deleting a Schedule

1. Click the **trash icon** next to the schedule name
2. Confirm the deletion

**Note:** Deleting a schedule removes all its courses from your calendar.

### Show/Hide Schedules on Calendar

- Each schedule has its own color assigned automatically
- Toggle visibility using the checkboxes in the calendar groups section
- Hidden schedules won't appear on the calendar but remain in your database

---

## Creating Personal Events

### Adding a New Event

**Method 1: Click on the Calendar**
1. Click on any empty time slot in the calendar
2. A popup will appear

**Method 2: Use the New Event Button**
1. Look for the add event option in your calendar view

### Filling in Event Details

In the event popup, enter:
- **Title**: Name of your event (e.g., "Team Meeting", "Study Session")
- **Calendar Group**: Choose which personal calendar group it belongs to (e.g., "Personal", "Work")
- **Date**: The date of the event
- **Start Time**: When it begins
- **Duration**: How long it lasts (in minutes)

Click **"Save"** to add the event.

### Editing an Event

1. Click on an existing event in the calendar
2. The popup will show the current details
3. Make your changes
4. Click **"Save"**

### Deleting an Event

1. Click on the event
2. Click the **"Delete"** button in the popup
3. Confirm the deletion

---

## Finding Meeting Times

This is one of CabbageMeet's most powerful features - finding common free time across multiple schedules.

### Prerequisites

- You need at least **2 imported schedules** to find meeting times
- The **"Meeting Suggestions"** button appears when you have 2+ schedules

### How to Find Meeting Times

1. Click **"Meeting Suggestions"** in the top toolbar

2. **Select Schedules to Compare**
   - Check the schedules you want to compare
   - For example: Your Fall 2025 schedule + your teammate's Fall 2025 schedule

3. **Choose Preferred Days**
   - Select which days of the week work for your meeting
   - Options: Mon, Tue, Wed, Thu, Fri, Sat, Sun
   - You can select multiple days

4. **Set Meeting Duration**
   - Enter how long your meeting needs to be (in minutes)
   - Example: 60 for a 1-hour meeting

5. **Optional: Set Time Range Filters**
   - **Earliest Start**: Don't suggest meetings before this time (e.g., 9:00 AM)
   - **Latest End**: Don't suggest meetings after this time (e.g., 6:00 PM)
   - Leave blank for no restriction

6. Click **"Find Meeting Times"**

### Understanding the Results

The app will show you:
- Available time slots that work for all selected schedules
- Day, start time, and end time for each suggestion
- Duration of each slot

**Example Result:**
- Monday - 1:00 PM to 2:00 PM (60 minutes)
- Wednesday - 3:00 PM to 4:00 PM (60 minutes)
- Friday - 10:00 AM to 11:00 AM (60 minutes)

### Viewing Suggestions on the Calendar

1. After getting suggestions, check the box: **"Show suggestions on calendar"**
2. Green dashed blocks will appear on your calendar showing available times
3. These are interactive - you can click on them to create an event

### Creating an Event from a Suggestion

1. Make sure "Show suggestions on calendar" is checked
2. Click on any green suggestion block on the calendar
3. The event popup will open pre-filled with:
   - Default title: "Team Meeting" (you can change this)
   - The suggested day and time
   - The duration you specified
4. Customize the title and details
5. Click **"Save"** to add it to your calendar

---

## Calendar Views

CabbageMeet offers four different calendar views:

### Week View (Default)

- Shows Monday through Sunday
- Displays all events for the current week
- Time slots from morning to night
- Best for day-to-day planning

**Navigation:**
- Use **< >** arrows to move between weeks
- Click **"Today"** to jump to the current week

### Day View

- Shows a single day in detail
- All time slots visible
- Best for focusing on today's schedule

**Navigation:**
- Use **< >** arrows to move between days
- Click **"Today"** to jump to today

### Month View

- Shows the entire month in a grid
- Events appear as colored blocks on each day
- Best for long-term planning

**Navigation:**
- Use **< >** arrows to move between months
- Click on any day to jump to that date in Day view

### Year View

- Shows all 12 months at a glance
- Overview of the entire year
- Best for semester planning

**Navigation:**
- Use **< >** arrows to move between years
- Click on any month to jump to that month

### Mini Calendar

The mini calendar in the sidebar allows you to:
- Quickly navigate to any date
- See today highlighted
- Click on any date to jump to it

---

## Tips and Tricks

### 1. Color Coding

- Each imported schedule gets a unique color automatically
- All courses from the same schedule share the same color
- This helps you visually distinguish between different terms or people's schedules

### 2. Managing Multiple Schedules

- Use descriptive names like "Winter 2024", "Fall 2025 Co-op", "Bob's Schedule"
- You can import the same person's schedule multiple times if needed
- Toggle visibility to focus on specific schedules

### 3. Meeting Suggestions Best Practices

- **Start broad, then narrow**:
  - First search all days with no time filter
  - Then add time restrictions if needed

- **Use time filters for realistic meetings**:
  - Example: Set 9:00 AM - 5:00 PM for business hours
  - Set 3:00 PM - 6:00 PM for after-class meetings

- **Adjust duration based on meeting type**:
  - Quick check-ins: 15-30 minutes
  - Working sessions: 60-120 minutes
  - Full team meetings: 60-90 minutes

### 4. Personal Event Organization

- Create multiple calendar groups for different types of events:
  - "Personal" for personal commitments
  - "Work" for job-related tasks
  - "Study" for exam prep and assignments

- Use consistent naming for recurring events
- Set realistic durations to avoid over-scheduling

### 5. Keyboard Shortcuts and Quick Actions

- **Double-click** a schedule name to rename it
- **Click** on empty calendar slots to quickly add events
- **Click** on existing events to edit them

### 6. Handling Edge Cases

**TBA Classes:**
- Classes with "TBA" (To Be Announced) times won't appear on the calendar
- They're still imported but hidden until times are assigned

**Overlapping Events:**
- The calendar will show overlapping events side-by-side
- Check for conflicts when planning

**No Common Free Time:**
- If the meeting suggestion finds nothing, try:
  - Reducing the meeting duration
  - Adding more days to the search
  - Removing time filters
  - Checking if schedules were imported correctly

### 7. Data Persistence

- All schedules are saved to a local SQLite database
- Personal events persist across sessions
- You don't need to re-import schedules each time you open the app

---

## Troubleshooting

### The calendar is empty after importing

- Check the "Imported Schedules" section - is your schedule listed?
- Try expanding the schedule to see if courses were imported
- Make sure the visibility toggle is enabled for that schedule

### Meeting suggestions aren't showing

- Verify you have at least 2 schedules imported
- Check that the schedules actually have conflicting times (i.e., there IS free time)
- Try broadening your search criteria (more days, longer time range)

### Events aren't saving

- Make sure the backend server is running on port 5000
- Check the browser console for errors
- Verify all required fields (title, date, time, duration) are filled

### Import failed

- For Quest import: Make sure you copied the entire schedule text
- For iCalendar: Verify the file is a valid .ics file
- Check that the backend is running and accessible

---

## Frequently Asked Questions

**Q: Can I import schedules from sources other than Quest or iCalendar?**
A: Currently, only Quest paste format and .ics files are supported.

**Q: How many schedules can I import?**
A: There's no hard limit, but the UI is optimized for 2-5 schedules.

**Q: Can I export my calendar?**
A: Export functionality is not currently available.

**Q: Can multiple people use the same CabbageMeet instance?**
A: The current version is designed for single-user local use. Each person should run their own instance.

**Q: What happens if I import the same schedule twice?**
A: It will create a duplicate. Use descriptive names and delete duplicates manually.

**Q: Can I share my availability with others?**
A: Not directly. You can take screenshots or manually coordinate based on the suggested meeting times.

---

## Support

For technical issues, bug reports, or feature requests:
- Check the project's GitHub repository
- Review the `build/README.md` for setup issues
- Contact your development team

---

**Version:** 1.0
**Last Updated:** December 2024
**Application:** CabbageMeet Calendar & Scheduling
