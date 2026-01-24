import { ChevronDown, ChevronRight, Trash2 } from 'lucide-react';
import React, { useMemo, useState, useEffect } from 'react';
import WeeklyCalendar from './components/WeeklyCalendar/WeeklyCalendar';
import DayCalendar from './components/WeeklyCalendar/DayCalendar';
import MonthCalendar from './components/WeeklyCalendar/MonthCalendar';
import YearCalendar from './components/WeeklyCalendar/YearCalendar';
import MiniMonthPicker from './components/WeeklyCalendar/MiniMonthPicker';
import TaskSidebar from './components/SidebarTasks/TaskSidebar';
import TaskPopover from './components/TaskPopover/TaskPopover';
import CoursePopover from './components/TaskPopover/CoursePopover';
import { HOURS_START, minutesToTimeString, timeToMinutes } from './components/WeeklyCalendar/timeUtils';
import './index.css';
import './App.css';

const WEEKDAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const DAY_KEY_BY_JS_INDEX = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const VIEW_BUTTONS = [
  { id: 'day', label: 'Day' },
  { id: 'week', label: 'Week' },
  { id: 'month', label: 'Month' },
  { id: 'year', label: 'Year' },
];
const JS_DAY_TO_KEY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Color palette for courses and groups
const GROUP_COLORS = [
  '#5B8DEF',
  '#3FB69F',
  '#E6A65C',
  '#E47EA8',
  '#8F73D6',
  '#57C0E8',
  '#F08F5A',
  '#7CCF91'
];

// Default personal groups
const DEFAULT_PERSONAL_GROUPS = [
  { id: 'grp-work', name: 'Personal', color: '#4CAF50', isCourse: false },
  { id: 'grp-study', name: 'Work', color: '#F2B705', isCourse: false },
];

// PBI-7: Helper to convert day abbreviations from backend to calendar format
const DAY_MAP = {
  'M': 'Mon',
  'T': 'Tue',
  'W': 'Wed',
  'Th': 'Thu',
  'F': 'Fri',
  'S': 'Sat',
  'Su': 'Sun',
  'TBA': 'TBA', // For TBA/online classes

  // Also handle if backend returns full names
  'Mon': 'Mon',
  'Tue': 'Tue',
  'Wed': 'Wed',
  'Thu': 'Thu',
  'Fri': 'Fri',
  'Sat': 'Sat',
  'Sun': 'Sun'
};

// Helper to map days
const mapDay = (day) => {
  if (day === 'Th' || day === 'Thu') return 'Thu';
  if (day === 'T' || day === 'Tue') return 'Tue';
  return DAY_MAP[day] || day;
};

// Convert time to 24-hour format (handles both 12-hour and 24-hour inputs)
const convertTo24Hour = (timeStr) => {
  if (!timeStr) return '00:00';
  
  // If it's already in 24-hour format (HH:MM or HH:MM:SS), just return first 5 chars
  if (!timeStr.match(/AM|PM/i)) {
    // Remove seconds if present (HH:MM:SS -> HH:MM)
    const parts = timeStr.split(':');
    return `${parts[0].padStart(2, '0')}:${parts[1] || '00'}`;
  }
  
  // Parse 12-hour format
  const match = timeStr.match(/(\d+):(\d+)(AM|PM)/i);
  if (!match) return '00:00';
  
  let [_, hours, minutes, period] = match;
  hours = parseInt(hours);
  
  if (period.toUpperCase() === 'PM' && hours !== 12) {
    hours += 12;
  } else if (period.toUpperCase() === 'AM' && hours === 12) {
    hours = 0;
  }
  
  return `${String(hours).padStart(2, '0')}:${minutes}`;
};

const getWeekStart = (baseDate) => {
  const date = new Date(baseDate);
  const diff = (date.getDay() + 6) % 7;
  date.setDate(date.getDate() - diff);
  date.setHours(0, 0, 0, 0);
  return date;
};

const shiftMonthDate = (date, direction) => {
  const next = new Date(date);
  const day = date.getDate();
  next.setDate(1);
  next.setMonth(date.getMonth() + direction);
  const maxDay = new Date(next.getFullYear(), next.getMonth() + 1, 0).getDate();
  next.setDate(Math.min(day, maxDay));
  return next;
};

const buildWeekDays = (currentDate) => {
  const start = getWeekStart(currentDate);
  return WEEKDAY_ORDER.map((key, idx) => {
    const dayDate = new Date(start);
    dayDate.setDate(start.getDate() + idx);
    return {
      key,
      label: dayDate.toLocaleDateString('en-US', { weekday: 'short' }),
      dateLabel: dayDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: dayDate,
    };
  });
};

const formatWeekRange = (weekDays) => {
  if (!weekDays.length) return '';
  const first = weekDays[0].fullDate;
  const last = weekDays[weekDays.length - 1].fullDate;
  const formatter = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' });
  return `${formatter.format(first)} – ${formatter.format(last)}`;
};

const createId = (prefix) => `${prefix}-${Math.random().toString(36).slice(2, 8)}`;
const formatDayLabel = (date) =>
  date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
const toTimeString = (date) =>
  `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
const buildStartDate = (dateISO, timeString) => {
  const base = new Date(dateISO);
  const minutes = timeToMinutes(timeString);
  if (!Number.isFinite(minutes)) return base;
  base.setHours(0, 0, 0, 0);
  base.setMinutes(minutes);
  return base;
};

function App() {
  const [view, setView] = useState('week');
  const [masterCalendarName, setMasterCalendarName] = useState("My Calendar ");
  const [isMasterCollapsed, setIsMasterCollapsed] = useState(false);
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const [schedules, setSchedules] = useState([]);
  const [expandedScheduleIds, setExpandedScheduleIds] = useState(new Set());  
  
  // Initialize with personal groups only (courses will be added from imported schedule)
  const [taskGroups, setTaskGroups] = useState(DEFAULT_PERSONAL_GROUPS);
  const [tasks, setTasks] = useState([]);
  
  // Store imported course schedule
  const [courseSchedule, setCourseSchedule] = useState([]);
  const [importedScheduleId, setImportedScheduleId] = useState(null);
  
  const [popover, setPopover] = useState({ open: false, position: { x: 0, y: 0 }, data: null });
  const [coursePopover, setCoursePopover] = useState({ open: false, position: { x: 0, y: 0 }, data: null });
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [scheduleInput, setScheduleInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [importCalendarName, setImportCalendarName] = useState('');
  const [importMethod, setImportMethod] = useState('quest');

  // Meeting suggestions state
  const [showSuggestionsDialog, setShowSuggestionsDialog] = useState(false);
  const [selectedScheduleIds, setSelectedScheduleIds] = useState([]);
  const [selectedDays, setSelectedDays] = useState(['M', 'T', 'W', 'Th', 'F', 'S', 'Su']);
  const [meetingDuration, setMeetingDuration] = useState(60);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [weekRange, setWeekRange] = useState(null);
  const [showSuggestionsOnCalendar, setShowSuggestionsOnCalendar] = useState(false);
  const [startTimeFilter, setStartTimeFilter] = useState('');
  const [endTimeFilter, setEndTimeFilter] = useState('');

  // Rename schedule state
  const [editingScheduleId, setEditingScheduleId] = useState(null);
  const [editingScheduleName, setEditingScheduleName] = useState('');

  // Visibility state for calendars
  const [calendarVisibility, setCalendarVisibility] = useState({});

  // Auto-enable visibility when calendars load
  useEffect(() => {
    const visibility = {};
    taskGroups.forEach(group => {
      visibility[group.id] = true;
    });
    setCalendarVisibility(visibility);
  }, [taskGroups]);

  // Toggle function
  const toggleCalendarVisibility = (groupId) => {
    setCalendarVisibility(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  };


 // Fetch latest schedule and personal events on mount

 useEffect(() => {
  loadTaskGroups();
  fetchAllSchedules(); 
  loadPersonalEvents();
}, []);

  // Fetch all schedules from backend and load them
  const fetchAllSchedules = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/schedules/all');
      const data = await response.json();

      if (data.success && data.schedules) {
        // Fetch full details for all schedules
        const allScheduleDetails = [];
        for (const schedule of data.schedules) {
          const detailResponse = await fetch(`http://localhost:5000/api/schedules/${schedule.schedule_id}`);
          const detailData = await detailResponse.json();

          if (detailData.success) {
            allScheduleDetails.push(detailData.schedule);
          }
        }

        // Update schedules state with full details
        setSchedules(allScheduleDetails);

        // Process all schedules at once
        if (allScheduleDetails.length > 0) {
          await processAllSchedules(allScheduleDetails);
        }
      }
    } catch (error) {
      console.log('No existing schedules found:', error);
    }
  };

  const toggleScheduleExpanded = (scheduleId) => {
    setExpandedScheduleIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(scheduleId)) {
        newSet.delete(scheduleId);
      } else {
        newSet.add(scheduleId);
      }
      return newSet;
    });
  };
  
  // Process multiple schedules at once (for initial load)
  const processAllSchedules = async (schedules) => {
    const allCourseEvents = [];
    const allCourseGroups = [];
    const colorsBySchedule = new Map();

    // Assign one color per schedule
    schedules.forEach((schedule, index) => {
      const scheduleColor = GROUP_COLORS[index % GROUP_COLORS.length];
      colorsBySchedule.set(schedule.schedule_id, scheduleColor);
    });

    // Process each schedule
    for (const schedule of schedules) {
      const courses = schedule.courses || [];
      const schedulePrefix = schedule.term || `Schedule ${schedule.schedule_id}`;
      const scheduleColor = colorsBySchedule.get(schedule.schedule_id);

      courses.forEach((course) => {
        const courseCode = course.course_code;
        const groupName = `${courseCode} (${schedulePrefix})`;

        // Create course group
        const courseGroup = {
          id: `course-grp-${schedule.schedule_id}-${courseCode.replace(/\s+/g, '-')}`,
          name: groupName,
          color: scheduleColor,
          isCourse: true,
          scheduleId: schedule.schedule_id,
          scheduleTerm: schedule.term,
        };
        allCourseGroups.push(courseGroup);

        // Process meetings
        course.meetings.forEach(meeting => {
          if (!meeting.days || meeting.days.length === 0 ||
              meeting.days.includes('TBA') ||
              !meeting.start_time || !meeting.end_time) {
            return;
          }

          meeting.days.forEach(day => {
            const mappedDay = mapDay(day);
            if (!mappedDay || mappedDay === 'TBA') return;

            const startTime = convertTo24Hour(meeting.start_time);
            const endTime = convertTo24Hour(meeting.end_time);

            allCourseEvents.push({
              id: createId('course-event'),
              courseId: course.course_id,
              course: groupName,
              originalCourse: courseCode,
              type: meeting.component || course.component || 'LEC',
              day: mappedDay,
              originalDay: day,
              start: startTime,
              end: endTime,
              location: meeting.location || '',
              instructor: meeting.instructor || '',
              startDate: meeting.start_date,
              endDate: meeting.end_date,
              scheduleId: schedule.schedule_id,
            });
          });
        });
      });
    }

    // Save all course groups to database
    for (const group of allCourseGroups) {
      await saveTaskGroupToDB(group);
    }

    // Update state with all groups and events
    setTaskGroups(prev => {
      const personalGroups = prev.filter(g => !g.isCourse);
      return [...allCourseGroups, ...personalGroups];
    });

    setCourseSchedule(allCourseEvents);
  };

  const startEditingSchedule = (scheduleId, currentName) => {
    setEditingScheduleId(scheduleId);
    setEditingScheduleName(currentName);
  };

  const cancelEditingSchedule = () => {
    setEditingScheduleId(null);
    setEditingScheduleName('');
  };

  const saveScheduleName = async (scheduleId) => {
    if (!editingScheduleName.trim()) {
      alert('Schedule name cannot be empty');
      cancelEditingSchedule();
      return;
    }

    const newName = editingScheduleName.trim();

    try {
      console.log('Renaming schedule', scheduleId, 'to:', newName);

      const response = await fetch(`http://localhost:5000/api/schedules/${scheduleId}/rename`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName })
      });

      const data = await response.json();
      console.log('Rename response:', data);

      if (data.success) {
        // Update local state
        setSchedules(prev => prev.map(s =>
          s.schedule_id === scheduleId ? { ...s, term: data.name } : s
        ));

        // Update task groups that reference this schedule
        setTaskGroups(prev => prev.map(g => {
          if (g.isCourse && g.scheduleId === scheduleId) {
            const courseCode = g.name.split(' (')[0]; // Extract just the course code
            return {
              ...g,
              name: `${courseCode} (${data.name})`,
              scheduleTerm: data.name
            };
          }
          return g;
        }));

        // Update course events
        setCourseSchedule(prev => prev.map(event => {
          if (event.scheduleId === scheduleId) {
            const courseCode = event.originalCourse || event.course.split(' (')[0];
            return {
              ...event,
              course: `${courseCode} (${data.name})`
            };
          }
          return event;
        }));

        cancelEditingSchedule();
      } else {
        alert('Error: ' + data.error);
        cancelEditingSchedule();
      }
    } catch (error) {
      console.error('Error renaming schedule:', error);
      alert('Failed to rename schedule');
      cancelEditingSchedule();
    }
  };

  const deleteEntireSchedule = async (scheduleId) => {
    const schedule = schedules.find(s => s.schedule_id === scheduleId);
    const confirmed = window.confirm(
      `Delete "${schedule.term || 'Schedule'}"? All courses will be removed from your calendar.`
    );
    if (!confirmed) return;
  
    try {
      const response = await fetch(`http://localhost:5000/api/schedules/${scheduleId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
  
      if (data.success) {
        setSchedules(prev => prev.filter(s => s.schedule_id !== scheduleId));
        setTaskGroups(prev => prev.filter(g => g.scheduleId !== scheduleId));
        setCourseSchedule(prev => prev.filter(e => e.scheduleId !== scheduleId));
        alert('Schedule deleted successfully');
      }
    } catch (error) {
      alert('Failed to delete schedule');
    }
  };

  // Process imported schedule and create course groups
 // Replace your existing processImportedSchedule function with this enhanced version

// Process imported schedule and create course groups
  // Replace your existing processImportedSchedule function with this enhanced version
  const processImportedSchedule = async (schedule, replaceExisting = true) => {
    const courses = schedule.courses || [];
    const courseEvents = [];
    const courseGroupsMap = new Map();

    // If replacing, clear existing course groups and events
    if (replaceExisting) {
      setTaskGroups(prev => prev.filter(g => !g.isCourse));
      setCourseSchedule([]);
    }

    // Create a friendly schedule prefix for group names
    const schedulePrefix = schedule.term || `Schedule ${schedule.schedule_id}`;

    // Assign ONE color for this entire schedule
    const existingSchedules = new Set(taskGroups.filter(g => g.isCourse).map(g => g.scheduleId));
    const scheduleColorIndex = existingSchedules.size % GROUP_COLORS.length;
    const scheduleColor = GROUP_COLORS[scheduleColorIndex];

    courses.forEach((course) => {
      const courseCode = course.course_code;
      // Add schedule term to course name to distinguish between multiple schedules
      const groupName = replaceExisting ? courseCode : `${courseCode} (${schedulePrefix})`;

      if (!courseGroupsMap.has(groupName)) {
        courseGroupsMap.set(groupName, {
          id: `course-grp-${schedule.schedule_id}-${courseCode.replace(/\s+/g, '-')}`,
          name: groupName,
          color: scheduleColor, // Use the same color for all courses in this schedule
          isCourse: true,
          scheduleId: schedule.schedule_id,
          scheduleTerm: schedule.term,
        });
      }

    course.meetings.forEach(meeting => {
      if (!meeting.days || meeting.days.length === 0 || 
          meeting.days.includes('TBA') || 
          !meeting.start_time || !meeting.end_time) {
        return;
      }

      meeting.days.forEach(day => {
        const mappedDay = mapDay(day);
        if (!mappedDay || mappedDay === 'TBA') return;

        const startTime = convertTo24Hour(meeting.start_time);
        const endTime = convertTo24Hour(meeting.end_time);

        courseEvents.push({
          id: createId('course-event'),
          courseId: course.course_id,
          course: groupName,
          originalCourse: courseCode,
          type: meeting.component || course.component || 'LEC',
          day: mappedDay,
          originalDay: day,
          start: startTime,
          end: endTime,
          location: meeting.location || '',
          instructor: meeting.instructor || '',
          startDate: meeting.start_date,
          endDate: meeting.end_date,
          scheduleId: schedule.schedule_id,
        });
      });
    });
  });

  const newCourseGroups = Array.from(courseGroupsMap.values());

  // Save course groups to database
  for (const group of newCourseGroups) {
    await saveTaskGroupToDB(group);
  }

  // Update task groups
  setTaskGroups(prev => {
    if (replaceExisting) {
      const personalGroups = prev.filter(g => !g.isCourse);
      return [...newCourseGroups, ...personalGroups];
    } else {
      // Add new groups without removing existing course groups
      const existingIds = new Set(prev.map(g => g.id));
      const uniqueNew = newCourseGroups.filter(g => !existingIds.has(g.id));
      return [...prev, ...uniqueNew];
    }
  });

  // Update course schedule
  setCourseSchedule(prev => 
    replaceExisting ? courseEvents : [...prev, ...courseEvents]
  );
};

// Also update your importSchedule function to not replace existing schedules:
const importSchedule = async (url, body, errorMsg) => {
  setIsLoading(true);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await response.json();

    if (data.success) {
      const finalName = importCalendarName.trim() || `My Calendar ${new Date().getFullYear()}`;
      
      alert(`Schedule imported successfully!\n\n"${finalName}"\nFound ${data.coursesCount} courses.`);

      if (data.scheduleId) {
        const scheduleResponse = await fetch(`http://localhost:5000/api/schedules/${data.scheduleId}`);
        const scheduleData = await scheduleResponse.json();
        
        if (scheduleData.success) {
          // Add to schedules list
          setSchedules(prev => [...prev, scheduleData.schedule]);
          
          // Process without replacing existing schedules (false = don't replace)
          await processImportedSchedule(scheduleData.schedule, false);
        }
      }
      handleCloseImportDialog();
    } else {
      alert(`Error: ${data.error}\n${data.details || ''}`);
    }
  } catch (error) {
    console.error('Error importing schedule:', error);
    alert(errorMsg);
  } finally {
    setIsLoading(false);
  }
};


  const weekDays = useMemo(() => buildWeekDays(currentDate), [currentDate]);
  const weekSubtitle = useMemo(() => formatWeekRange(weekDays), [weekDays]);
  const daySubtitle = useMemo(
    () => currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }),
    [currentDate]
  );
  const monthSubtitle = useMemo(
    () => currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
    [currentDate]
  );
  const yearSubtitle = useMemo(
    () => currentDate.getFullYear().toString(),
    [currentDate]
  );

  const viewSubtitle = useMemo(() => {
    switch (view) {
      case 'day':
        return daySubtitle;
      case 'week':
        return weekSubtitle;
      case 'month':
        return monthSubtitle;
      case 'year':
        return yearSubtitle;
      default:
        return '';
    }
  }, [view, daySubtitle, weekSubtitle, monthSubtitle, yearSubtitle]);

  const currentDayKey = DAY_KEY_BY_JS_INDEX[currentDate.getDay()];
  const defaultGroupId = taskGroups.find(g => !g.isCourse)?.id ?? taskGroups[0]?.id ?? null;

  // Convert suggestions to calendar events
  const convertSuggestionsToEvents = (suggestions, weekDays) => {
    if (!showSuggestionsOnCalendar || suggestions.length === 0) return [];

    // Map day abbreviations to actual dates this week
    const dayMap = {
      'M': weekDays[0]?.fullDate,   // Monday
      'T': weekDays[1]?.fullDate,   // Tuesday
      'W': weekDays[2]?.fullDate,   // Wednesday
      'Th': weekDays[3]?.fullDate,  // Thursday
      'F': weekDays[4]?.fullDate,   // Friday
      'S': weekDays[5]?.fullDate,   // Saturday
      'Su': weekDays[6]?.fullDate   // Sunday
    };

    return suggestions
      .filter(suggestion => dayMap[suggestion.day]) // Only include days in current week
      .map((suggestion, index) => ({
        course: '💡 Available Time',
        type: 'Suggestion',
        day: mapDay(suggestion.day),
        start: convertTo24Hour(suggestion.start_time),
        end: convertTo24Hour(suggestion.end_time),
        color: '#81C784',  // Light green
        metadata: {
          eventType: 'suggestion',
          suggestionId: index,
          suggestionData: suggestion
        }
      }));
  };

  // Combine course schedule and personal tasks into calendar events
  const calendarEvents = useMemo(() => {
    const weekStart = getWeekStart(currentDate);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);
    
    // Personal tasks — only if calendar is visible
    const taskEvents = tasks
      .filter(task => calendarVisibility[task.groupId] !== false)
      .map(task => {
        const start = new Date(task.startISO);
        const end = new Date(start.getTime() + task.duration * 60000);
        const group = taskGroups.find(g => g.id === task.groupId);
        return {
          course: task.title,
          type: group?.name ?? 'Task',
          day: JS_DAY_TO_KEY[start.getDay()],
          start: toTimeString(start),
          end: toTimeString(end),
          color: group?.color ?? '#CBD5F5',
          metadata: { taskId: task.id, eventType: 'task' },
        };
      });

    // Course events with color coding from their groups
    // Filter by date range - only show events that overlap with current week
    // Course events — only if their calendar is visible

    const courseEvents = courseSchedule
      .filter(event => {
        const courseGroup = taskGroups.find(g => g.name === event.course && g.isCourse);
        if (!courseGroup) return false;
        if (calendarVisibility[courseGroup.id] === false) return false;

        if (!event.startDate || !event.endDate) return true;
        
        const eventStart = new Date(event.startDate);
        const eventEnd = new Date(event.endDate);
        
        // Check if event date range overlaps with current week
        return eventStart <= weekEnd && eventEnd >= weekStart;
      })
      .map(event => {
        const courseGroup = taskGroups.find(g => g.name === event.course && g.isCourse);
        return {
          ...event,
          color: courseGroup?.color ?? '#CBD5F5',
          metadata: { courseEventId: event.id, eventType: 'course' },
        };
      });

    // Add suggestion events if enabled
    const suggestionEvents = convertSuggestionsToEvents(suggestions, weekDays);

    return [...courseEvents, ...taskEvents, ...suggestionEvents];
  }, [tasks, taskGroups, courseSchedule, currentDate, calendarVisibility, suggestions, showSuggestionsOnCalendar, weekDays]);

  // Calculate group counts
  const groupsWithCounts = useMemo(() => {
  return taskGroups.map(group => {
    const count = group.isCourse
      ? courseSchedule.filter(e => e.course === group.name).length
      : tasks.filter(t => t.groupId === group.id).length;

    return {
      ...group,
      count,
      visible: calendarVisibility[group.id] !== false,  // Critical!
    };
  });
}, [taskGroups, tasks, courseSchedule, calendarVisibility]);

  const emptyForm = useMemo(() => {
    const startOfDay = new Date(currentDate);
    startOfDay.setHours(0, 0, 0, 0);
    return {
      id: null,
      title: '',
      groupId: defaultGroupId ?? '',
      dateISO: startOfDay.toISOString(),
      dayLabel: formatDayLabel(startOfDay),
      startTime: minutesToTimeString(HOURS_START * 60),
      duration: 60,
    };
  }, [currentDate, defaultGroupId]);

  const openTaskPopover = (data, anchor) => {
    if (!data || !defaultGroupId) return;
    const baseDate = data.dateISO ? new Date(data.dateISO) : new Date(currentDate);
    baseDate.setHours(0, 0, 0, 0);
    setPopover({
      open: true,
      position: anchor ?? { x: window.innerWidth / 2, y: window.innerHeight / 2 },
      data: {
        id: data.id ?? null,
        title: data.title ?? '',
        groupId: data.groupId ?? defaultGroupId,
        dateISO: baseDate.toISOString(),
        dayLabel: data.dayLabel ?? formatDayLabel(baseDate),
        startTime: data.startTime ?? minutesToTimeString(HOURS_START * 60),
        duration: data.duration ?? 60,
      },
    });
  };

  // Open course event editor
  const openCoursePopover = (data, anchor) => {
    setCoursePopover({
      open: true,
      position: anchor ?? { x: window.innerWidth / 2, y: window.innerHeight / 2 },
      data: data,
    });
  };

  const closePopover = () => setPopover({ open: false, position: { x: 0, y: 0 }, data: null });
  const closeCoursePopover = () => setCoursePopover({ open: false, position: { x: 0, y: 0 }, data: null });

  const handleSlotSelect = ({ dayDate, minutesFromStart, clientX, clientY }) => {
    if (!dayDate || !defaultGroupId) return;
    const iso = new Date(dayDate);
    iso.setHours(0, 0, 0, 0);
    const dayLabel = formatDayLabel(iso);
    const startTime = minutesToTimeString(minutesFromStart ?? HOURS_START * 60);
    openTaskPopover(
      { dateISO: iso.toISOString(), dayLabel, startTime, title: '', groupId: defaultGroupId },
      { x: clientX, y: clientY }
    );
  };

 const handleEventSelect = (metadata, event) => {
  if (!metadata) return;

  const anchor = event
    ? { x: event.clientX, y: event.clientY }
    : { x: window.innerWidth / 2, y: window.innerHeight / 2 };

  // Handle suggestion clicks - open TaskPopover pre-filled
  if (metadata.eventType === 'suggestion') {
    const suggestion = metadata.suggestionData;

    // Map suggestion day to actual date
    const dayMap = {
      'M': weekDays[0]?.fullDate,
      'T': weekDays[1]?.fullDate,
      'W': weekDays[2]?.fullDate,
      'Th': weekDays[3]?.fullDate,
      'F': weekDays[4]?.fullDate,
      'S': weekDays[5]?.fullDate,
      'Su': weekDays[6]?.fullDate
    };

    const dateForDay = dayMap[suggestion.day];
    if (!dateForDay || !defaultGroupId) return;

    // Open TaskPopover pre-filled with suggestion
    openTaskPopover({
      title: 'Team Meeting',  // Default title, user can change
      groupId: defaultGroupId,
      dateISO: dateForDay.toISOString(),
      dayLabel: formatDayLabel(dateForDay),
      startTime: convertTo24Hour(suggestion.start_time),
      duration: suggestion.duration_minutes
    }, anchor);
    return;
  }

  // Handle personal task events
  if (metadata.taskId) {
    const task = tasks.find((t) => t.id === metadata.taskId);
    if (!task) return;
    const start = new Date(task.startISO);
    const dayDate = new Date(start);
    dayDate.setHours(0, 0, 0, 0);
    openTaskPopover(
      {
        id: task.id,
        dbId: task.dbId, // Include dbId
        title: task.title,
        groupId: task.groupId,
        dateISO: dayDate.toISOString(),
        dayLabel: formatDayLabel(start),
        startTime: toTimeString(start),
        duration: task.duration,
      },
      anchor
    );
  }
  
  // Handle course events
  else if (metadata.courseEventId) {
    const courseEvent = courseSchedule.find((e) => e.id === metadata.courseEventId);
    if (!courseEvent) return;
    openCoursePopover(
      {
        id: courseEvent.id,
        courseId: courseEvent.courseId,
        course: courseEvent.course,
        type: courseEvent.type,
        day: courseEvent.day,
        start: courseEvent.start,
        end: courseEvent.end,
        location: courseEvent.location,
        instructor: courseEvent.instructor,
      },
      anchor
    );
  }
};

const handleSaveTask = async (form) => {
  if (!form.title.trim() || !form.groupId) return;
  const startDate = buildStartDate(form.dateISO, form.startTime);
  
  const payload = {
    id: form.id ?? createId('task'),
    dbId: form.dbId, // Preserve dbId if editing existing task
    title: form.title.trim(),
    groupId: form.groupId,
    startISO: startDate.toISOString(),
    duration: Number(form.duration) || 60,
  };
  
  // Save to database
  const dbId = await savePersonalEventToDB(payload);
  
  if (dbId && !payload.dbId) {
    // New event - add the DB ID
    payload.dbId = dbId;
    payload.id = `task-${dbId}`;
  }
  
  // Update local state
  setTasks((prev) => {
    const exists = prev.some((task) => task.id === payload.id);
    return exists 
      ? prev.map((task) => (task.id === payload.id ? payload : task)) 
      : [...prev, payload];
  });
  
  closePopover();
};

  const handleSaveCourse = (form) => {
    if (!form.course?.trim()) return;
    
    const payload = {
      id: form.id ?? createId('course-event'),
      course: form.course.trim(),
      type: form.type || 'LEC',
      day: form.day,
      start: form.start,
      end: form.end,
      location: form.location || '',
      instructor: form.instructor || '',
    };
    
    setCourseSchedule((prev) => {
      const exists = prev.some((event) => event.id === payload.id);
      return exists 
        ? prev.map((event) => (event.id === payload.id ? payload : event)) 
        : [...prev, payload];
    });
    
    // If this is a new course, create a group for it
    const courseExists = taskGroups.some(g => g.name === payload.course && g.isCourse);
    if (!courseExists) {
      const courseGroupCount = taskGroups.filter(g => g.isCourse).length;
      const newColor = GROUP_COLORS[courseGroupCount % GROUP_COLORS.length];
      setTaskGroups(prev => [...prev, {
        id: `course-grp-${payload.course.replace(/\s+/g, '-')}`,
        name: payload.course,
        color: newColor,
        isCourse: true,
      }]);
    }
    
    closeCoursePopover();
  };

  const handleDeleteTask = async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    
    // Delete from database if it has a dbId
    if (task?.dbId) {
      const success = await deletePersonalEventFromDB(task.dbId);
      if (!success) {
        alert('Failed to delete event from database');
        return;
      }
    }
    
    // Remove from local state
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
    closePopover();
  };
    // Delete course event
    const handleDeleteCourse = async (eventId) => {
    // Find the event to get the details
    const courseEvent = courseSchedule.find((e) => e.id === eventId);
    if (!courseEvent) {
      console.error('Course event not found');
      return;
    }

    console.log('=== DELETE DEBUG ===');
    console.log('Full event:', courseEvent);
    console.log('Original day (from DB):', courseEvent.originalDay);
    console.log('Display day:', courseEvent.day);
    console.log('==================');

    // If this event has a courseId (from backend), delete from database
    if (courseEvent.courseId && courseEvent.originalDay) {
      try {
        // Use originalDay (what's in the DB) not day (display format)
        const requestBody = {
          day_of_week: courseEvent.originalDay,  // Use original format from DB
        };
        
        console.log('Sending DELETE request with:', requestBody);
        
        const response = await fetch(
          `http://localhost:5000/api/meetings/${courseEvent.courseId}`,
          {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
          }
        );
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (!data.success) {
          console.error('Failed to delete meeting:', data.error);
          alert('Failed to delete meeting: ' + data.error);
          return;
        }
        
        console.log('Meeting deleted from database successfully');
      } catch (error) {
        console.error('Error deleting meeting:', error);
        alert('Error deleting meeting. Please try again.');
        return;
      }
  }

  // Remove ONLY this specific event from local state (by id)
  setCourseSchedule((prev) => prev.filter((event) => event.id !== eventId));
  
  // Check if this was the last event for this course
  const courseName = courseEvent.course;
  const remainingEvents = courseSchedule.filter(
    e => e.course === courseName && e.id !== eventId
  );
  
  // If no more events for this course, remove the course group
  if (remainingEvents.length === 0) {
    setTaskGroups(prev => prev.filter(g => !(g.name === courseName && g.isCourse)));
  }
  
  closeCoursePopover();
};


  const handleAddGroup = async (label) => {
  const trimmed = label.trim();
  if (!trimmed) return;
  
  const personalGroupCount = taskGroups.filter(g => !g.isCourse).length;
  const color = GROUP_COLORS[personalGroupCount % GROUP_COLORS.length];
  const newGroup = { 
    id: createId('grp'), 
    name: trimmed, 
    color, 
    isCourse: false 
  };
  
  // Save to database
  const success = await saveTaskGroupToDB(newGroup);
  
  if (success) {
    setTaskGroups((prev) => [...prev, newGroup]);
  } else {
    alert('Failed to save calendar group');
  }
};

const handleDeleteGroup = async (groupId) => {
  const groupToDelete = taskGroups.find(g => g.id === groupId);
  
  // If deleting a course group (existing code)
  if (groupToDelete?.isCourse) {
    const confirmed = window.confirm(`Delete all ${groupToDelete.name} classes? This cannot be undone.`);
    if (!confirmed) return;
  }
  
  // For personal groups
  const nonCourseGroups = taskGroups.filter(g => !g.isCourse);
  if (nonCourseGroups.length <= 1) {
    alert('You must have at least one personal calendar');
    return;
  }
  
  const confirmed = window.confirm(`Delete "${groupToDelete.name}" calendar? All events will be moved to another calendar.`);
  if (!confirmed) return;
  
  // Delete from database
  const success = await deleteTaskGroupFromDB(groupId);
  
  if (!success) {
    alert('Failed to delete calendar group');
    return;
  }
  
  // Update local state
  const filtered = taskGroups.filter((group) => group.id !== groupId);
  const fallbackId = filtered.find(g => !g.isCourse)?.id ?? null;
  setTaskGroups(filtered);
  
  if (fallbackId) {
    // Move all tasks to fallback group and update in database
    const tasksToMove = tasks.filter(t => t.groupId === groupId);
    for (const task of tasksToMove) {
      task.groupId = fallbackId;
      if (task.dbId) {
        await savePersonalEventToDB(task);
      }
    }
    setTasks((prev) => prev.map((task) => 
      task.groupId === groupId ? { ...task, groupId: fallbackId } : task
    ));
  }
};


  const shiftDate = (direction) => {
    setCurrentDate((prev) => {
      let next = new Date(prev);
      switch (view) {
        case 'day':
          next.setDate(prev.getDate() + direction);
          break;
        case 'week':
          next.setDate(prev.getDate() + direction * 7);
          break;
        case 'month':
          next = shiftMonthDate(prev, direction);
          break;
        case 'year':
          next.setFullYear(prev.getFullYear() + direction);
          break;
        default:
          next.setDate(prev.getDate() + direction);
      }
      return next;
    });
  };

  const handleToday = () => {
    setCurrentDate(new Date());
  };
  
  const handleMiniMonthNavigate = (direction) => {
    setCurrentDate((prev) => shiftMonthDate(prev, direction));
  };
  
  const handleMiniSelect = (date) => {
    setCurrentDate(new Date(date.getFullYear(), date.getMonth(), date.getDate()));
  };

  const renderCalendar = () => {
    switch (view) {
      case 'day':
        return (
          <DayCalendar
            events={calendarEvents}
            dayKey={currentDayKey}
            dayLabel={daySubtitle}
            dayDate={currentDate}
            onSlotSelect={handleSlotSelect}
            onEventSelect={handleEventSelect}
          />
        );
      case 'week':
        return (
          <WeeklyCalendar
            events={calendarEvents}
            weekDays={weekDays}
            onSlotSelect={handleSlotSelect}
            onEventSelect={handleEventSelect}
          />
        );
      case 'month':
        return <MonthCalendar currentDate={currentDate} events={calendarEvents} />;
      case 'year':
        return <YearCalendar currentDate={currentDate} />;
      default:
        return null;
    }
  };

  // Update group colors (works for both courses and personal groups)
  const handleUpdateGroupColor = async (groupId, color) => {
  // Update in database
  const success = await updateTaskGroupInDB(groupId, { color });
  
  if (success) {
    setTaskGroups((prev) =>
      prev.map((group) => (group.id === groupId ? { ...group, color } : group))
    );
  } else {
    alert('Failed to update calendar color');
  }
};

 const handleCloseImportDialog = () => {
  setShowImportDialog(false);
  setScheduleInput('');
  setImportCalendarName('');  // ← NEW: reset name
  setImportMethod('quest');
};

  // Load personal events from database
const loadPersonalEvents = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/personal-events');
    const data = await response.json();
    
    if (data.success && data.events) {
      // Convert database format to app format
      const loadedTasks = data.events.map(event => ({
        id: `task-${event.event_id}`, // Prefix to distinguish from new tasks
        dbId: event.event_id, // Store DB ID for updates/deletes
        title: event.title,
        groupId: event.group_id,
        startISO: event.start_datetime,
        duration: event.duration,
      }));
      setTasks(loadedTasks);
    }
  } catch (error) {
    console.error('Error loading personal events:', error);
  }
};

  // Load task groups from database
  const loadTaskGroups = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/task-groups');
      const data = await response.json();
      
      if (data.success && data.groups) {
        // Separate personal groups from course groups
        const personalGroups = data.groups.filter(g => !g.isCourse);
        
        // If no personal groups exist, use defaults
        if (personalGroups.length === 0) {
          // Save default groups to database
          for (const group of DEFAULT_PERSONAL_GROUPS) {
            await saveTaskGroupToDB(group);
          }
          setTaskGroups(DEFAULT_PERSONAL_GROUPS);
        } else {
          setTaskGroups(personalGroups);
        }
      }
    } catch (error) {
      console.error('Error loading task groups:', error);
      // Fallback to default groups if error
      setTaskGroups(DEFAULT_PERSONAL_GROUPS);
    }
  };

  // Save task group to database
  const saveTaskGroupToDB = async (group) => {
    try {
      const groupData = {
        group_id: group.id,
        name: group.name,
        color: group.color,
        is_course: group.isCourse || false,
      };
      
      const response = await fetch('http://localhost:5000/api/task-groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(groupData),
      });
      
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error saving task group:', error);
      return false;
    }
  };

  // Update task group in database
  const updateTaskGroupInDB = async (groupId, updates) => {
    try {
      const response = await fetch(`http://localhost:5000/api/task-groups/${groupId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error updating task group:', error);
      return false;
    }
  };

  // Delete task group from database
  const deleteTaskGroupFromDB = async (groupId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/task-groups/${groupId}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error deleting task group:', error);
      return false;
    }
  };

  // Save personal event to database
  const savePersonalEventToDB = async (task) => {
    try {
      const eventData = {
        title: task.title,
        group_id: task.groupId,
        start_datetime: task.startISO,
        duration: task.duration,
      };
      
      // If task has dbId, update; otherwise create
      if (task.dbId) {
        const response = await fetch(`http://localhost:5000/api/personal-events/${task.dbId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(eventData),
        });
        const data = await response.json();
        return data.success;
      } else {
        const response = await fetch('http://localhost:5000/api/personal-events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(eventData),
        });
        const data = await response.json();
        
        if (data.success) {
          // Return the new DB ID so we can update the task
          return data.event_id;
        }
        return false;
      }
    } catch (error) {
      console.error('Error saving personal event:', error);
      return false;
    }
  };

  // Delete personal event from database
  const deletePersonalEventFromDB = async (dbId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/personal-events/${dbId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error deleting personal event:', error);
      return false;
    }
  };


const handleImportClick = async () => {
  setShowImportDialog(true);

  // Generate default name based on current schedule count
  const nextNumber = schedules.length + 1;
  setImportCalendarName(`Schedule ${nextNumber}`);

  setScheduleInput('');
  setImportMethod('quest');
};

  const handleIcalFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const fileContent = await file.text();
    await importSchedule(
      'http://localhost:5000/api/schedules/icalendar',
      {
        icalContent: fileContent,
        scheduleName: importCalendarName.trim()
      },
      'Failed to import iCalendar file. Please check that the backend is running and try again.'
    );
    event.target.value = '';
  };

  const handleQuestSubmit = async () => {
    const scheduleName = importCalendarName.trim();
    console.log('DEBUG: Importing with name:', scheduleName);
    console.log('DEBUG: importCalendarName state:', importCalendarName);

    await importSchedule(
      'http://localhost:5000/api/schedules',
      {
        scheduleText: scheduleInput,
        scheduleName: scheduleName
      },
      'Failed to import schedule. Please check that the backend is running and try again.'
    );
  };

  // Handle opening suggestions dialog
  const handleOpenSuggestionsDialog = () => {
    if (schedules.length < 2) {
      alert('Please import at least 2 schedules to find common meeting times.');
      return;
    }
    // Pre-select all schedules by default
    setSelectedScheduleIds(schedules.map(s => s.schedule_id));
    setShowSuggestionsDialog(true);
  };

  // Fetch meeting suggestions from API
  const handleFetchSuggestions = async () => {
    if (selectedScheduleIds.length === 0) {
      alert('Please select at least one schedule.');
      return;
    }

    setLoadingSuggestions(true);
    try {
      const requestBody = {
        schedule_ids: selectedScheduleIds,
        preferred_days: selectedDays,
        duration_minutes: meetingDuration,
        max_suggestions: 100,  // Show lots of suggestions
        start_time: startTimeFilter || null,
        end_time: endTimeFilter || null
      };

      const response = await fetch('http://localhost:5000/api/meeting-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.success) {
        setSuggestions(data.suggestions);
        setWeekRange(data.week_range);
        if (data.suggestions.length === 0) {
          alert('No common free time found with the current preferences. Try different days or shorter duration.');
        }
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      alert('Failed to fetch meeting suggestions. Please check that the backend is running.');
    } finally {
      setLoadingSuggestions(false);
    }
  };

  // Toggle schedule selection
  const toggleScheduleSelection = (scheduleId) => {
    setSelectedScheduleIds(prev =>
      prev.includes(scheduleId)
        ? prev.filter(id => id !== scheduleId)
        : [...prev, scheduleId]
    );
  };

  // Toggle day selection
  const toggleDaySelection = (day) => {
    setSelectedDays(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day]
    );
  };

  return (
    <div className="cm-page">
      <header className="cm-toolbar">
        <div>
          <h1>CabbageMeet — Calendar</h1>
          <p className="cm-toolbar-subtitle">{viewSubtitle}</p>
        </div>
        <div className="cm-toolbar-actions">
          <button className="cm-btn" onClick={handleToday}>Today</button>
          <div className="cm-nav-group">
            <button className="cm-btn icon" onClick={() => shiftDate(-1)}>‹</button>
            <button className="cm-btn icon" onClick={() => shiftDate(1)}>›</button>
          </div>
          <div className="cm-view-toggle">
            {VIEW_BUTTONS.map((option) => (
              <button
                key={option.id}
                className={`cm-btn toggle ${view === option.id ? 'active' : ''}`}
                onClick={() => setView(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>
          <button className="cm-btn primary" onClick={handleImportClick}>
            Import Calendar
          </button>
          {schedules.length >= 2 && (
            <button className="cm-btn primary" onClick={handleOpenSuggestionsDialog}>
              Meeting Suggestions
            </button>
          )}
        </div>
      </header>

      <main className="cm-calendar-area">
        <div className="cm-layout">
          <aside className="cm-sidebar">
            <MiniMonthPicker
    currentDate={currentDate}
    onNavigateMonth={handleMiniMonthNavigate}
    onSelectDate={handleMiniSelect}
  />

  {/* Removed "My Schedule" section - using only Imported Schedules */}

  {schedules.length > 0 && (
  <div className="schedule-manager">
    <p className="schedule-manager__title">Imported Schedules</p>
    
    <ul className="schedule-list">
      {schedules.map((schedule) => {
        const isExpanded = expandedScheduleIds.has(schedule.schedule_id);
        const courseCount = schedule.course_count || schedule.courses?.length || 0;

        return (
          <li key={schedule.schedule_id} className="schedule-item">
            <div className="schedule-header">
              {/* Expand/collapse button */}
              <button
                className="schedule-expand"
                onClick={() => toggleScheduleExpanded(schedule.schedule_id)}
                aria-label={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>

              {/* Schedule name and course count */}
              <div
                className="schedule-info"
                onClick={() => toggleScheduleExpanded(schedule.schedule_id)}
              >
                {editingScheduleId === schedule.schedule_id ? (
                  <input
                    type="text"
                    value={editingScheduleName}
                    onChange={(e) => setEditingScheduleName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        e.target.blur(); // This will trigger onBlur which saves
                      } else if (e.key === 'Escape') {
                        e.preventDefault();
                        cancelEditingSchedule();
                      }
                    }}
                    onBlur={() => {
                      // Only save if we're still in editing mode
                      if (editingScheduleId === schedule.schedule_id) {
                        saveScheduleName(schedule.schedule_id);
                      }
                    }}
                    onClick={(e) => e.stopPropagation()}
                    autoFocus
                    style={{
                      padding: '4px 8px',
                      fontSize: '14px',
                      border: '1px solid #5B8DEF',
                      borderRadius: '4px',
                      flex: 1,
                      marginRight: '8px'
                    }}
                  />
                ) : (
                  <span
                    className="schedule-name"
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEditingSchedule(schedule.schedule_id, schedule.term || 'Untitled Schedule');
                    }}
                    style={{ cursor: 'text' }}
                    title="Double-click to rename"
                  >
                    {schedule.term || 'Untitled Schedule'}
                  </span>
                )}
                <span className="schedule-count">
                  {courseCount} course{courseCount !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Delete button */}
              <button
                className="schedule-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteEntireSchedule(schedule.schedule_id);
                }}
                aria-label={`Delete ${schedule.term || 'schedule'}`}
                title="Delete entire schedule"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {/* Expanded course list */}
            {isExpanded && schedule.courses && schedule.courses.length > 0 && (
              <ul className="course-list">
                {schedule.courses.map((course, idx) => (
                  <li key={idx} className="course-item">
                    <span className="course-code">{course.course_code}</span>
                    <span className="course-name-small">{course.course_name}</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        );
      })}
    </ul>
  </div>
)}

</aside>

          <section className="cm-main-panel">
            {renderCalendar()}
          </section>
        </div>
      </main>
      
      {/* Task/Personal event popover */}
      <TaskPopover
        open={popover.open}
        position={popover.position}
        groups={taskGroups.filter(g => !g.isCourse)}
        initialData={popover.data ?? emptyForm}
        onSave={handleSaveTask}
        onDelete={handleDeleteTask}
        onClose={closePopover}
      />
      
      {/* Course event popover */}
      <CoursePopover
        open={coursePopover.open}
        position={coursePopover.position}
        initialData={coursePopover.data}
        onSave={handleSaveCourse}
        onDelete={handleDeleteCourse}
        onClose={closeCoursePopover}
      />
      
      {showImportDialog && (
  <div className="modal-overlay" onClick={handleCloseImportDialog}>
    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
      <div className="modal-header">
        <h2>Import Schedule</h2>
        <button className="close-button" onClick={handleCloseImportDialog}>×</button>
      </div>

      {/* NEW: Calendar Name Input */}
      <div className="calendar-name-input">
        <label>Calendar Name</label>
        <input
          type="text"
          placeholder="e.g. Fall 2025, Winter 2026, My Co-op Term..."
          value={importCalendarName}
          onChange={(e) => setImportCalendarName(e.target.value)}
          autoFocus
        />
      </div>

      <div className="import-method-tabs">
        <button
          className={`method-tab ${importMethod === 'quest' ? 'active' : ''}`}
          onClick={() => setImportMethod('quest')}
          disabled={isLoading}
        >
          Quest Paste
        </button>
        <button
          className={`method-tab ${importMethod === 'icalendar' ? 'active' : ''}`}
          onClick={() => setImportMethod('icalendar')}
          disabled={isLoading}
        >
          iCalendar File
        </button>
      </div>

      <div className="modal-body">
        {importMethod === 'quest' ? (
          <>
            <p className="instructions">Paste your schedule information from Quest below:</p>
            <textarea
              className="schedule-input"
              value={scheduleInput}
              onChange={(e) => setScheduleInput(e.target.value)}
              placeholder="Paste your schedule here..."
              rows={10}
              disabled={isLoading}
            />
          </>
        ) : (
          <>
            <p className="instructions">Upload an iCalendar (.ics) file:</p>
            <div className="file-upload-area">
              <input
                type="file"
                id="ical-file-input"
                accept=".ics"
                onChange={handleIcalFileChange}
                disabled={isLoading}
                style={{ display: 'none' }}
              />
              <label htmlFor="ical-file-input" className="file-upload-button">
                {isLoading ? 'Importing...' : 'Choose iCalendar File'}
              </label>
              <p className="file-hint">Select a .ics file from your calendar application</p>
            </div>
          </>
        )}
      </div>

      <div className="modal-footer">
        <button className="cancel-button" onClick={handleCloseImportDialog} disabled={isLoading}>
          Cancel
        </button>
        <button
          className="submit-button"
          onClick={importMethod === 'quest' ? handleQuestSubmit : handleIcalFileChange}
          disabled={
            isLoading ||
            (importMethod === 'quest' && !scheduleInput.trim()) ||
            !importCalendarName.trim()
          }
        >
          {isLoading ? 'Importing...' : 'Import Schedule'}
        </button>
      </div>
    </div>
  </div>
)}

{/* Meeting Suggestions Dialog */}
{showSuggestionsDialog && (
  <div className="modal-overlay" onClick={() => setShowSuggestionsDialog(false)}>
    <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
      <div className="modal-header">
        <h2>Find Common Meeting Times</h2>
        <button className="close-button" onClick={() => setShowSuggestionsDialog(false)}>×</button>
      </div>

      <div className="modal-body">
        {/* Schedule Selection */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#f0f0f0' }}>
            Select Schedules to Compare:
          </label>
          {schedules.map(schedule => (
            <div key={schedule.schedule_id} style={{ marginBottom: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: '#f0f0f0' }}>
                <input
                  type="checkbox"
                  checked={selectedScheduleIds.includes(schedule.schedule_id)}
                  onChange={() => toggleScheduleSelection(schedule.schedule_id)}
                  style={{ marginRight: '8px' }}
                />
                {schedule.term || `Schedule ${schedule.schedule_id}`}
              </label>
            </div>
          ))}
        </div>

        {/* Day Selection */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#f0f0f0' }}>
            Preferred Days:
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {[
              { key: 'M', label: 'Mon' },
              { key: 'T', label: 'Tue' },
              { key: 'W', label: 'Wed' },
              { key: 'Th', label: 'Thu' },
              { key: 'F', label: 'Fri' },
              { key: 'S', label: 'Sat' },
              { key: 'Su', label: 'Sun' }
            ].map(day => (
              <button
                key={day.key}
                onClick={() => toggleDaySelection(day.key)}
                style={{
                  padding: '8px 12px',
                  border: selectedDays.includes(day.key) ? '2px solid #5B8DEF' : '1px solid #ccc',
                  borderRadius: '4px',
                  background: selectedDays.includes(day.key) ? '#5B8DEF' : 'white',
                  color: selectedDays.includes(day.key) ? 'white' : '#333',
                  cursor: 'pointer',
                  fontWeight: selectedDays.includes(day.key) ? 'bold' : 'normal'
                }}
              >
                {day.label}
              </button>
            ))}
          </div>
        </div>

        {/* Duration Selection */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#f0f0f0' }}>
            Meeting Duration (minutes):
          </label>
          <input
            type="number"
            value={meetingDuration}
            onChange={(e) => setMeetingDuration(Number(e.target.value))}
            min="15"
            step="15"
            style={{ padding: '8px', width: '100%', border: '1px solid #ccc', borderRadius: '4px' }}
          />
        </div>

        {/* Time Range Filters */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#f0f0f0' }}>
            Time Range (optional):
          </label>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '13px', color: '#d0d0d0' }}>
                Earliest Start
              </label>
              <input
                type="time"
                value={startTimeFilter}
                onChange={(e) => setStartTimeFilter(e.target.value)}
                style={{ padding: '8px', width: '100%', border: '1px solid #ccc', borderRadius: '4px' }}
                placeholder="e.g., 09:00"
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '13px', color: '#d0d0d0' }}>
                Latest End
              </label>
              <input
                type="time"
                value={endTimeFilter}
                onChange={(e) => setEndTimeFilter(e.target.value)}
                style={{ padding: '8px', width: '100%', border: '1px solid #ccc', borderRadius: '4px' }}
                placeholder="e.g., 17:00"
              />
            </div>
          </div>
          <p style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
            Leave blank for no time restrictions
          </p>
        </div>

        {/* Fetch Button */}
        <button
          onClick={handleFetchSuggestions}
          disabled={loadingSuggestions || selectedScheduleIds.length === 0}
          style={{
            width: '100%',
            padding: '12px',
            background: '#5B8DEF',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loadingSuggestions ? 'wait' : 'pointer',
            marginBottom: '20px'
          }}
        >
          {loadingSuggestions ? 'Finding times...' : 'Find Meeting Times'}
        </button>

        {/* Results */}
        {suggestions.length > 0 && (
          <div>
            <h3 style={{ marginBottom: '8px', color: '#f0f0f0' }}>Suggested Times:</h3>
            {weekRange && (
              <p style={{ fontSize: '14px', color: '#d0d0d0', marginBottom: '12px' }}>
                For the week of {new Date(weekRange.start).toLocaleDateString()} - {new Date(weekRange.end).toLocaleDateString()}
              </p>
            )}

            {/* Toggle to show suggestions on calendar */}
            <div style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid #555' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: '#f0f0f0' }}>
                <input
                  type="checkbox"
                  checked={showSuggestionsOnCalendar}
                  onChange={(e) => setShowSuggestionsOnCalendar(e.target.checked)}
                  style={{ marginRight: '8px', width: '16px', height: '16px', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '15px' }}>Show suggestions on calendar</span>
              </label>
              <p style={{ fontSize: '12px', color: '#999', marginTop: '4px', marginLeft: '24px' }}>
                Click any suggestion block on the calendar to create an event
              </p>
            </div>

            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  style={{
                    padding: '12px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '4px',
                    marginBottom: '8px',
                    background: '#f9f9f9'
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                    {mapDay(suggestion.day)} - {suggestion.start_time} to {suggestion.end_time}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    Duration: {suggestion.duration_minutes} minutes
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="modal-footer">
        <button className="cancel-button" onClick={() => setShowSuggestionsDialog(false)}>
          Close
        </button>
      </div>
    </div>
  </div>
)}
    </div>
  );
}

export default App;
