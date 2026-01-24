import React, { useMemo, useState } from 'react';
import './TaskSidebar.css';

const COLOR_POOL = ['#4CAF50', '#F2B705', '#29B6F6', '#AB47BC', '#FF7043', '#8D6E63', '#00ACC1'];

export default function TaskSidebar({
  groups = [],
  tasks = [],
  onAddGroup,
  onDeleteGroup,
  onUpdateGroupColor,
  onToggleVisibility,
}) {
  const [newGroup, setNewGroup] = useState('');

  const counts = useMemo(() => {
    const map = new Map(groups.map(g => [g.id, 0]));
    tasks.forEach(task => {
      if (map.has(task.groupId)) {
        map.set(task.groupId, map.get(task.groupId) + 1);
      }
    });
    return map;
  }, [groups, tasks]);

  const disableDelete = groups.length <= 1;
  const canAddGroup = newGroup.trim().length > 0;

  const handleSubmit = e => {
    e.preventDefault();
    const trimmed = newGroup.trim();
    if (!trimmed) return;
    onAddGroup(trimmed);
    setNewGroup('');
  };

  return (
    <div className="group-panel">
      <p className="group-panel__title">Calendars</p>

      <ul className="group-list">
        {groups.map((group, idx) => {
          const isVisible = group.visible !== false;
          const color = group.color || COLOR_POOL[idx % COLOR_POOL.length];

          return (
            <li
              key={group.id}
              className="group-item"
              style={{ opacity: isVisible ? 1 : 0.55 }}
            >
              <div className="group-pill">
                <label className="group-color-trigger">
                  <input
                    type="color"
                    value={color}
                    onChange={e => onUpdateGroupColor?.(group.id, e.target.value)}
                    className="group-color-input"
                  />
                  <span className="group-dot" style={{ backgroundColor: color }} />
                </label>

                <span className="group-name">{group.name}</span>
              </div>

              <div className="group-actions">
                <span className="group-count">{counts.get(group.id) ?? 0}</span>

                {/* YOUR EYE ICON — Open Eye for visible, Closed for hidden */}
                <button
                  type="button"
                  onClick={() => onToggleVisibility(group.id)}
                  className="visibility-toggle"
                  aria-label={isVisible ? 'Hide calendar' : 'Show calendar'}
                  title={isVisible ? 'Hide' : 'Show'}
                >
                  {isVisible ? (
                    // Open Eye SVG (from your screenshot)
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <circle cx="12" cy="12" r="3" fill="#333"/>
                    </svg>
                  ) : (
                    // Closed Eye SVG
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.31-4.31" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>

                <button
                  type="button"
                  className="group-delete"
                  onClick={() => onDeleteGroup?.(group.id)}
                  disabled={disableDelete}
                  aria-label={`Delete ${group.name}`}
                >
                  X
                </button>
              </div>
            </li>
          );
        })}
      </ul>

      <form className="group-form" onSubmit={handleSubmit}>
        <button type="submit" className="plus-pill" disabled={!canAddGroup}>
          +
        </button>
        <input
          type="text"
          placeholder="Add calendar"
          value={newGroup}
          onChange={e => setNewGroup(e.target.value)}
        />
      </form>
    </div>
  );
}
