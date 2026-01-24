"""
Free time identification algorithm for CabbageMeet.

This algorithm finds common free time across multiple schedules.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import re


def time_to_minutes(time_str: str) -> int:
    """
    Convert time string 'HH:MMAM/PM' to minutes since midnight.
    
    Parameters:
        time_str: Time in format like '10:30AM' or '2:45PM'
        
    Returns:
        Minutes since midnight (e.g., '10:30AM' -> 630)
    """
    if not time_str or time_str.strip() == "":
        return 0
    
    time_str = time_str.strip().upper()
    
    # Match format like "10:30AM" or "2:30PM"
    match = re.match(r'(\d{1,2}):(\d{2})(AM|PM)', time_str)
    if not match:
        return 0
    
    hour = int(match.group(1))
    minute = int(match.group(2))
    am_pm = match.group(3)
    
    # Convert to 24-hour format
    if am_pm == "PM" and hour != 12:
        hour += 12
    elif am_pm == "AM" and hour == 12:
        hour = 0
    
    return hour * 60 + minute


def minutes_to_time(minutes: int) -> str:
    """
    Convert minutes since midnight back to 'HH:MMAM/PM' format.

    Parameters:
        minutes: Minutes since midnight (0-1439)

    Returns:
        Time string like '10:30AM'
    """
    # Clamp to valid range (0-1439)
    minutes = max(0, min(minutes, 1439))

    hour = minutes // 60
    minute = minutes % 60

    am_pm = "AM"
    if hour >= 12:
        am_pm = "PM"
        if hour > 12:
            hour -= 12
    elif hour == 0:
        hour = 12

    return f"{hour}:{minute:02d}{am_pm}"


def merge_overlapping_blocks(blocks: List[Dict[str, int]]) -> List[Dict[str, int]]:
    """
    Merge overlapping time blocks.
    
    Parameters:
        blocks: List of dicts with 'start' and 'end' keys (in minutes)
        
    Returns:
        Merged list of non-overlapping blocks
    """
    if not blocks:
        return []
    
    # Sort by start time
    sorted_blocks = sorted(blocks, key=lambda x: x['start'])
    
    merged = [sorted_blocks[0].copy()]
    
    for current in sorted_blocks[1:]:
        last = merged[-1]
        
        # If current block overlaps or is adjacent to last block, merge them
        if current['start'] <= last['end']:
            last['end'] = max(last['end'], current['end'])
        else:
            # No overlap, add as new block
            merged.append(current.copy())
    
    return merged


def find_gaps(busy_blocks: List[Dict[str, int]], 
              day_start: int, 
              day_end: int, 
              min_duration: int) -> List[Dict[str, Any]]:
    """
    Find free time gaps between busy blocks.
    
    Parameters:
        busy_blocks: List of busy time blocks (already merged)
        day_start: Start of day in minutes (e.g., 8*60 = 480 for 8am)
        day_end: End of day in minutes (e.g., 22*60 = 1320 for 10pm)
        min_duration: Minimum gap duration in minutes
        
    Returns:
        List of free time gaps with start, end, and duration
    """
    gaps = []
    
    # If no classes, entire day is free
    if not busy_blocks:
        duration = day_end - day_start
        if duration >= min_duration:
            return [{
                'start': day_start,
                'end': day_end,
                'duration': duration
            }]
        return []
    
    # Gap before first class
    if busy_blocks[0]['start'] > day_start:
        duration = busy_blocks[0]['start'] - day_start
        if duration >= min_duration:
            gaps.append({
                'start': day_start,
                'end': busy_blocks[0]['start'],
                'duration': duration
            })
    
    # Gaps between classes
    for i in range(len(busy_blocks) - 1):
        gap_start = busy_blocks[i]['end']
        gap_end = busy_blocks[i + 1]['start']
        duration = gap_end - gap_start
        
        if duration >= min_duration:
            gaps.append({
                'start': gap_start,
                'end': gap_end,
                'duration': duration
            })
    
    # Gap after last class
    if busy_blocks[-1]['end'] < day_end:
        duration = day_end - busy_blocks[-1]['end']
        if duration >= min_duration:
            gaps.append({
                'start': busy_blocks[-1]['end'],
                'end': day_end,
                'duration': duration
            })
    
    return gaps


def find_common_free_time(schedules: List[Dict[str, Any]],
                          options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Find common free time across multiple schedules.

    This is the main algorithm for PBI-13.

    Parameters:
        schedules: List of schedule dictionaries from database (via get_schedule_from_db)
                   Each schedule has format:
                   {
                       'schedule_id': int,
                       'user_id': str,
                       'term': str,
                       'courses': [
                           {
                               'course_code': str,
                               'meetings': [
                                   {
                                       'days': ['M', 'W', 'F'],
                                       'start_time': '9:00AM',
                                       'end_time': '10:20AM',
                                       'location': str,
                                       'instructor': str,
                                       'start_date': 'YYYY-MM-DD',
                                       'end_date': 'YYYY-MM-DD'
                                   }
                               ]
                           }
                       ]
                   }
        options: Optional configuration:
                 - min_duration: Minimum free time in minutes (default: 30)
                 - start_hour: Day start hour (default: 8)
                 - end_hour: Day end hour (default: 22)
                 - days_of_week: List of days to check (default: ['M', 'T', 'W', 'Th', 'F', 'S', 'Su'])
                 - week_start_date: Start date to filter meetings (ISO format YYYY-MM-DD)
                 - week_end_date: End date to filter meetings (ISO format YYYY-MM-DD)

    Returns:
        List of free time blocks:
        [
            {
                'day': 'M',
                'start_time': '10:20AM',
                'end_time': '11:30AM',
                'duration_minutes': 70
            },
            ...
        ]
    """
    from datetime import datetime as dt

    # Default options
    if options is None:
        options = {}

    min_duration = options.get('min_duration', 30)
    start_hour = options.get('start_hour', 8)
    end_hour = options.get('end_hour', 22)
    days_of_week = options.get('days_of_week', ['M', 'T', 'W', 'Th', 'F', 'S', 'Su'])
    week_start_date = options.get('week_start_date')
    week_end_date = options.get('week_end_date')

    # Parse date range if provided
    filter_start = None
    filter_end = None
    if week_start_date:
        try:
            filter_start = dt.fromisoformat(week_start_date).date()
        except:
            pass
    if week_end_date:
        try:
            filter_end = dt.fromisoformat(week_end_date).date()
        except:
            pass
    
    day_start = start_hour * 60
    day_end = end_hour * 60
    
    free_time = []
    
    # Process each day of the week
    for day in days_of_week:
        all_busy_blocks = []
        
        # Collect all busy times for this day from ALL schedules
        for schedule in schedules:
            if not schedule or 'courses' not in schedule:
                continue

            for course in schedule['courses']:
                if not course or 'meetings' not in course:
                    continue

                for meeting in course['meetings']:
                    if not meeting or 'days' not in meeting:
                        continue

                    # Check if this meeting is on the current day
                    if day in meeting['days']:
                        # Date range filtering
                        if filter_start and filter_end:
                            meeting_start = meeting.get('start_date', '')
                            meeting_end = meeting.get('end_date', '')

                            # Skip if meeting has dates and they don't overlap with filter range
                            if meeting_start and meeting_end:
                                try:
                                    m_start = dt.strptime(meeting_start, '%Y-%m-%d').date()
                                    m_end = dt.strptime(meeting_end, '%Y-%m-%d').date()

                                    # Check if meeting date range overlaps with filter range
                                    if m_end < filter_start or m_start > filter_end:
                                        continue  # Skip this meeting
                                except:
                                    pass  # If date parsing fails, include the meeting

                        start_time_str = meeting.get('start_time', '')
                        end_time_str = meeting.get('end_time', '')

                        # Skip TBA meetings or meetings without times
                        if not start_time_str or not end_time_str:
                            continue

                        start_minutes = time_to_minutes(start_time_str)
                        end_minutes = time_to_minutes(end_time_str)

                        # Only add valid time blocks
                        if start_minutes > 0 and end_minutes > start_minutes:
                            all_busy_blocks.append({
                                'start': start_minutes,
                                'end': end_minutes
                            })
        
        # Merge overlapping busy blocks
        merged_busy = merge_overlapping_blocks(all_busy_blocks)

        # Find free time gaps
        gaps = find_gaps(merged_busy, day_start, day_end, min_duration)
        
        # Format output
        for gap in gaps:
            free_time.append({
                'day': day,
                'start_time': minutes_to_time(gap['start']),
                'end_time': minutes_to_time(gap['end']),
                'duration_minutes': gap['duration']
            })
    
    return free_time


# Helper function for easier testing
def get_free_time_for_schedule_ids(schedule_ids: List[int], 
                                   options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to get free time directly from schedule IDs.
    
    Parameters:
        schedule_ids: List of schedule IDs from database
        options: Optional configuration (see find_common_free_time)
        
    Returns:
        List of free time blocks
    """
    from src.backend.database import get_schedule_from_db
    
    schedules = []
    for schedule_id in schedule_ids:
        schedule = get_schedule_from_db(schedule_id)
        if schedule:
            schedules.append(schedule)
    
    if not schedules:
        return []

    return find_common_free_time(schedules, options)


def suggest_meeting_times(free_time_blocks: List[Dict[str, Any]],
                         preferred_days: List[str],
                         duration_needed: int,
                         max_suggestions: int = 3,
                         start_time_filter: str = None,
                         end_time_filter: str = None) -> List[Dict[str, Any]]:
    """
    Filter free time blocks and suggest specific meeting time slots.

    Parameters:
        free_time_blocks: Output from find_common_free_time()
        preferred_days: List of preferred days like ['M', 'W', 'F']
        duration_needed: Meeting duration in minutes (e.g., 60)
        max_suggestions: Maximum number of suggestions to return (default: 3)
        start_time_filter: Optional earliest start time in 24-hour format (e.g., "09:00")
        end_time_filter: Optional latest end time in 24-hour format (e.g., "17:00")

    Returns:
        List of suggested meeting time slots (up to max_suggestions)
    """
    suggestions = []

    # Convert time filters to minutes if provided
    start_time_minutes = None
    end_time_minutes = None

    if start_time_filter:
        try:
            # Parse HH:MM format
            hours, minutes = map(int, start_time_filter.split(':'))
            start_time_minutes = hours * 60 + minutes
        except Exception:
            pass  # Ignore invalid format

    if end_time_filter:
        try:
            # Parse HH:MM format
            hours, minutes = map(int, end_time_filter.split(':'))
            end_time_minutes = hours * 60 + minutes
        except Exception:
            pass  # Ignore invalid format

    # Process each free time block
    for block in free_time_blocks:
        # Must be on a preferred day
        if block['day'] not in preferred_days:
            continue

        # Must have enough duration
        if block['duration_minutes'] < duration_needed:
            continue

        # Break the free block into specific meeting slots
        start_minutes = time_to_minutes(block['start_time'])
        end_minutes = time_to_minutes(block['end_time'])

        # Apply time filters to the free block bounds
        if start_time_minutes is not None:
            start_minutes = max(start_minutes, start_time_minutes)

        if end_time_minutes is not None:
            end_minutes = min(end_minutes, end_time_minutes)

        # Ensure times are within a single day (0-1439 minutes)
        start_minutes = max(0, min(start_minutes, 1439))
        end_minutes = max(0, min(end_minutes, 1439))

        # Check if there's still enough time after applying filters
        if end_minutes - start_minutes < duration_needed:
            continue

        # Generate meeting slots within this free block
        current_start = start_minutes
        while current_start + duration_needed <= end_minutes:
            meeting_end = current_start + duration_needed

            suggestions.append({
                'day': block['day'],
                'start_time': minutes_to_time(current_start),
                'end_time': minutes_to_time(meeting_end),
                'duration_minutes': duration_needed
            })

            # Move to next potential slot (30-minute intervals)
            current_start += 30

            # Stop if we have enough suggestions
            if len(suggestions) >= max_suggestions:
                break

        if len(suggestions) >= max_suggestions:
            break

    # Sort by day order and time
    day_order = {day: i for i, day in enumerate(['M', 'T', 'W', 'Th', 'F', 'S', 'Su'])}
    suggestions.sort(key=lambda x: (
        day_order.get(x['day'], 99),
        time_to_minutes(x['start_time'])
    ))

    return suggestions[:max_suggestions]