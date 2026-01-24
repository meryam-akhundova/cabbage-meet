"""
Tests for free time algorithm.
"""

# Remove sys.path manipulation - use proper imports instead
from src.backend.free_time_algorithm import (
    find_common_free_time,
    time_to_minutes,
    minutes_to_time
)


def test_time_conversion():
    """Test time conversion functions."""
    print("Testing time conversions...")
    
    assert time_to_minutes("9:00AM") == 540  # 9*60
    assert time_to_minutes("10:30AM") == 630  # 10*60 + 30
    assert time_to_minutes("12:00PM") == 720  # 12*60
    assert time_to_minutes("1:00PM") == 780  # 13*60
    assert time_to_minutes("11:59PM") == 1439  # 23*60 + 59
    
    assert minutes_to_time(540) == "9:00AM"
    assert minutes_to_time(630) == "10:30AM"
    assert minutes_to_time(780) == "1:00PM"
    
    print("Time conversion tests passed!")


def test_basic_free_time():
    """Test basic free time finding with two simple schedules."""
    print("\nTesting basic free time identification...")
    
    # Schedule 1
    schedule1 = {
        'schedule_id': 1,
        'user_id': 'maya',
        'term': 'Winter 2025',
        'courses': [{
            'course_code': 'CS 246',
            'meetings': [{
                'days': ['M'],
                'start_time': '9:00AM',
                'end_time': '10:20AM'
            }]
        }]
    }
    
    # Schedule 2
    schedule2 = {
        'schedule_id': 2,
        'user_id': 'kaibo',
        'term': 'Winter 2025',
        'courses': [{
            'course_code': 'ECE 222',
            'meetings': [{
                'days': ['M'],
                'start_time': '11:30AM',
                'end_time': '12:50PM'
            }]
        }]
    }
    
    result = find_common_free_time([schedule1, schedule2])
    
    # Should find free time on Monday: 8:00-9:00, 10:20-11:30, 12:50-22:00
    monday_free = [r for r in result if r['day'] == 'M']
    
    print(f"Found {len(monday_free)} free time blocks on Monday:")
    for block in monday_free:
        print(f"  {block['start_time']} - {block['end_time']} ({block['duration_minutes']} min)")
    
    assert len(monday_free) == 3, f"Expected 3 blocks, got {len(monday_free)}"
    print("Basic free time test passed!")


def test_overlapping_schedules():
    """Test schedules with overlapping classes."""
    print("\nTesting overlapping schedules...")
    
    schedule1 = {
        'schedule_id': 1,
        'courses': [{
            'meetings': [{
                'days': ['M'],
                'start_time': '9:00AM',
                'end_time': '12:00PM'
            }]
        }]
    }
    
    schedule2 = {
        'schedule_id': 2,
        'courses': [{
            'meetings': [{
                'days': ['M'],
                'start_time': '10:00AM',
                'end_time': '11:00AM'
            }]
        }]
    }
    
    result = find_common_free_time([schedule1, schedule2])
    monday_free = [r for r in result if r['day'] == 'M']
    
    # The 10-11 class is inside 9-12, so should merge into one big 9-12 block
    # Free time: 8-9, 12-22
    print(f"Found {len(monday_free)} free time blocks:")
    for block in monday_free:
        print(f"  {block['start_time']} - {block['end_time']}")
    
    assert len(monday_free) == 2
    print("Overlapping schedules test passed!")


def test_multiple_days():
    """Test free time across multiple days."""
    print("\nTesting multiple days...")
    
    schedule = {
        'schedule_id': 1,
        'courses': [{
            'meetings': [{
                'days': ['M', 'W', 'F'],
                'start_time': '9:00AM',
                'end_time': '10:20AM'
            }]
        }]
    }
    
    result = find_common_free_time([schedule])
    
    print(f"Found free time on {len(set(r['day'] for r in result))} days")
    for day in ['M', 'T', 'W', 'Th', 'F']:
        day_blocks = [r for r in result if r['day'] == day]
        print(f"  {day}: {len(day_blocks)} blocks")
    
    # Tuesday and Thursday should have entire day free
    tuesday_free = [r for r in result if r['day'] == 'T']
    assert len(tuesday_free) == 1  # Entire day
    assert tuesday_free[0]['duration_minutes'] == 840  # 14 hours * 60
    
    print("Multiple days test passed!")


def test_minimum_duration():
    """Test minimum duration filtering."""
    print("\nTesting minimum duration filter...")
    
    schedule = {
        'schedule_id': 1,
        'courses': [{
            'meetings': [
                {
                    'days': ['M'],
                    'start_time': '9:00AM',
                    'end_time': '9:15AM'
                },
                {
                    'days': ['M'],
                    'start_time': '9:30AM',
                    'end_time': '10:00AM'
                }
            ]
        }]
    }
    
    # With 30-minute minimum, should NOT show the 9:15-9:30 gap (only 15 min)
    result = find_common_free_time([schedule], {'min_duration': 30})
    monday_free = [r for r in result if r['day'] == 'M']
    
    print(f"Found {len(monday_free)} blocks with 30min minimum")
    for block in monday_free:
        print(f"  {block['start_time']} - {block['end_time']} ({block['duration_minutes']} min)")
        assert block['duration_minutes'] >= 30
    
    print("Minimum duration test passed!")


def test_no_common_free_time():
    """Test case where someone is always busy."""
    print("\nTesting no common free time...")
    
    schedule1 = {
        'schedule_id': 1,
        'courses': [{
            'meetings': [{
                'days': ['M'],
                'start_time': '8:00AM',
                'end_time': '10:00PM'
            }]
        }]
    }
    
    schedule2 = {
        'schedule_id': 2,
        'courses': []
    }
    
    result = find_common_free_time([schedule1, schedule2])
    monday_free = [r for r in result if r['day'] == 'M']
    
    print(f"Found {len(monday_free)} free blocks (expected 0)")
    assert len(monday_free) == 0
    
    print("No free time test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING FREE TIME ALGORITHM TESTS")
    print("=" * 60)
    
    test_time_conversion()
    test_basic_free_time()
    test_overlapping_schedules()
    test_multiple_days()
    test_minimum_duration()
    test_no_common_free_time()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)