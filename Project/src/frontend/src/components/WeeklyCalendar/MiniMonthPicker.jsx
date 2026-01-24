import React, { useMemo } from "react";
import "./WeeklyCalendar.css";
import { getMonthMatrix, isSameDay } from "./calendarUtils";

const WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function MiniMonthPicker({ currentDate, onSelectDate, onNavigateMonth }) {
	const matrix = useMemo(() => getMonthMatrix(currentDate), [currentDate]);
	const monthLabel = useMemo(
		() => currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" }),
		[currentDate]
	);

	return (
		<div className="cm-mini-picker">
			<div className="cm-mini-picker-header">
				<span>{monthLabel}</span>
				<div className="cm-mini-picker-nav">
					<button type="button" aria-label="Previous month" onClick={() => onNavigateMonth(-1)}>
						‹
					</button>
					<button type="button" aria-label="Next month" onClick={() => onNavigateMonth(1)}>
						›
					</button>
				</div>
			</div>
			<div className="cm-mini-picker-grid">
				{WEEKDAY_LABELS.map((label) => (
					<span key={label} className="cm-mini-picker-label">
						{label[0]}
					</span>
				))}
				{matrix.map((week) =>
					week.map((day) => {
						const classes = [
							"cm-mini-picker-day",
							day.inCurrentMonth ? "" : "muted",
							day.isToday ? "today" : "",
							isSameDay(day.date, currentDate) ? "selected" : "",
						]
							.filter(Boolean)
							.join(" ");
						return (
							<button
								type="button"
								key={day.date.toISOString()}
								className={classes}
								onClick={() => onSelectDate(day.date)}
							>
								{day.label}
							</button>
						);
					})
				)}
			</div>
		</div>
	);
}