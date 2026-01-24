import React, { useMemo } from "react";
import "./WeeklyCalendar.css";
import { getMonthMatrix } from "./calendarUtils";

const MONTH_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function MonthCalendar({ currentDate, events = [] }) {
	const matrix = useMemo(() => getMonthMatrix(currentDate), [currentDate]);

	return (
		<div className="cm-month-wrapper">
			<div className="cm-month-grid">
				<div className="cm-month-header-row">
					{MONTH_HEADERS.map((label) => (
						<div key={label} className="cm-month-header-cell">
							{label}
						</div>
					))}
				</div>
				<div className="cm-month-body">
					{matrix.map((week, idx) => (
						<div key={idx} className="cm-month-week">
							{week.map((day) => {
								const dayEvents = events.filter((ev) => ev.day === day.dayKey);
								return (
									<div
										key={day.date.toISOString()}
										className={`cm-month-cell ${day.inCurrentMonth ? '' : 'muted'} ${day.isToday ? 'today' : ''}`}
									>
										<div className="cm-month-cell-label">{day.label}</div>
										<div className="cm-month-cell-events">
											{dayEvents.slice(0, 2).map((ev, index) => (
												<div
													key={`${ev.course}-${index}`}
													className="cm-month-chip"
													style={{ backgroundColor: ev.color || '#cbd5f5' }}
												>
													<span className="chip-title">{ev.course}</span>
													<span className="chip-type">{ev.type}</span>
												</div>
											))}
											{dayEvents.length > 2 && (
												<div className="cm-month-more">+{dayEvents.length - 2} more</div>
											)}
										</div>
									</div>
								);
							})}
						</div>
					))}
				</div>
			</div>
		</div>
	);
}


