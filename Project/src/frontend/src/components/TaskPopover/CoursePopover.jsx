// CoursePopover.jsx - PBI-8: Edit course schedule events
import React, { useState, useEffect, useRef } from 'react';
import './TaskPopover.css'; // Reuse existing popover styles

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const COURSE_TYPES = ['LEC', 'LAB', 'TUT', 'SEM', 'STU'];

export default function CoursePopover({ open, position, initialData, onSave, onDelete, onClose }) {
  const [form, setForm] = useState({
    id: null,
    course: '',
    type: 'LEC',
    day: 'Mon',
    start: '08:00',
    end: '09:00',
    location: '',
    instructor: '',
  });

  const popoverRef = useRef(null);

  useEffect(() => {
    if (open && initialData) {
      setForm({
        id: initialData.id || null,
        course: initialData.course || '',
        type: initialData.type || 'LEC',
        day: initialData.day || 'Mon',
        start: initialData.start || '08:00',
        end: initialData.end || '09:00',
        location: initialData.location || '',
        instructor: initialData.instructor || '',
      });
    }
  }, [open, initialData]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        onClose();
      }
    };
    
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (!form.course.trim()) {
      alert('Please enter a course name');
      return;
    }
    
    // Validate that end time is after start time
    if (form.start >= form.end) {
      alert('End time must be after start time');
      return;
    }
    
    onSave(form);
  };

  const handleDelete = () => {
    if (form.id && window.confirm('Delete this course event?')) {
      onDelete(form.id);
    }
  };

  const isEditing = !!form.id;

  return (
    <div className="task-popover-overlay">
      <div
        ref={popoverRef}
        className="task-popover"
        style={{
          position: 'fixed',
          left: Math.min(position.x, window.innerWidth - 360),
          top: Math.min(position.y, window.innerHeight - 500),
        }}
      >
        <div className="task-popover-header">
          <h3>{isEditing ? 'Edit Course Event' : 'Add Course Event'}</h3>
          <button className="task-popover-close" onClick={onClose}>×</button>
        </div>

        <div className="task-popover-body">
          <div className="task-form-group">
            <label>Course Code</label>
            <input
              type="text"
              placeholder="e.g. CS 137"
              value={form.course}
              onChange={(e) => handleChange('course', e.target.value)}
              autoFocus
            />
          </div>

          <div className="task-form-group">
            <label>Type</label>
            <select value={form.type} onChange={(e) => handleChange('type', e.target.value)}>
              {COURSE_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="task-form-group">
            <label>Day</label>
            <select value={form.day} onChange={(e) => handleChange('day', e.target.value)}>
              {DAYS.map(day => (
                <option key={day} value={day}>{day}</option>
              ))}
            </select>
          </div>

          <div className="task-form-row">
            <div className="task-form-group">
              <label>Start Time</label>
              <input
                type="time"
                value={form.start}
                onChange={(e) => handleChange('start', e.target.value)}
              />
            </div>

            <div className="task-form-group">
              <label>End Time</label>
              <input
                type="time"
                value={form.end}
                onChange={(e) => handleChange('end', e.target.value)}
              />
            </div>
          </div>

          <div className="task-form-group">
            <label>Location (Optional)</label>
            <input
              type="text"
              placeholder="e.g. MC 4020"
              value={form.location}
              onChange={(e) => handleChange('location', e.target.value)}
            />
          </div>

          <div className="task-form-group">
            <label>Instructor (Optional)</label>
            <input
              type="text"
              placeholder="e.g. Prof. Smith"
              value={form.instructor}
              onChange={(e) => handleChange('instructor', e.target.value)}
            />
          </div>
        </div>

        <div className="task-popover-footer">
          <div>
            {isEditing && (
              <button className="task-btn task-btn-danger" onClick={handleDelete}>
                Delete
              </button>
            )}
          </div>
          <div className="task-popover-actions">
            <button className="task-btn task-btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button className="task-btn task-btn-primary" onClick={handleSave}>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}