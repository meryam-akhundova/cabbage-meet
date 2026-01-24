// WeeklyCalendar.jsx
import React, { useMemo } from "react";
import "./WeeklyCalendar.css";
import EventBlock from "./EventBlock";
import {
	HOURS_START,
	HOURS_END,
	getHourLabels,
	calculateEventPosition,
	minutesToTimeString,
} from "./timeUtils";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function WeeklyCalendar({ events = [], weekDays = [], onSlotSelect, onEventSelect }) {
	const hourLabels = useMemo(() => getHourLabels(), []);
	const daysConfig = weekDays.length
		? weekDays
		: DAYS.map((day) => ({ key: day, label: day, dateLabel: "", fullDate: null }));
	const dayMap = useMemo(() => new Map(daysConfig.map((day) => [day.key, day])), [daysConfig]);

	// Group events by day for simpler rendering
	const eventsByDay = useMemo(() => {
		const grouped = {};
		for (const d of daysConfig) grouped[d.key] = [];
		for (const ev of events) {
			const dayKey = ev.day;
			if (grouped[dayKey]) {
				grouped[dayKey].push(ev);
			}
		}
		return grouped;
	}, [events, daysConfig]);

	const handleDayClick = (dayKey, event) => {
		if (!onSlotSelect) return;
		const contentEl = event.currentTarget;
		const rect = contentEl.getBoundingClientRect();
		let offsetY = event.clientY - rect.top;
		offsetY = Math.max(0, Math.min(offsetY, rect.height));
		const minutesFromStart = Math.round(offsetY);
		const absoluteMinutes = HOURS_START * 80 + minutesFromStart;
		const timeLabel = minutesToTimeString(absoluteMinutes);
		const dayInfo = dayMap.get(dayKey);
		onSlotSelect({
			day: dayKey,
			time: timeLabel,
			minutesFromStart: absoluteMinutes,
			dayDate: dayInfo?.fullDate ?? null,
			clientX: event.clientX,
			clientY: event.clientY,
		});
	};

	return (
		<div className="cm-calendar-wrapper" role="region" aria-label="Weekly calendar">
			<div className="cm-calendar-grid">
				{/* Time column */}
				<div className="cm-time-col">
					<div className="cm-day-header cm-time-header" aria-hidden>
						<span className="cm-day-title">Time</span>
						<span className="cm-day-sub">&nbsp;</span>
					</div>
					{hourLabels.map((h) => (
						<div className="cm-time-label" key={h}>
							{h}
						</div>
					))}
				</div>

				{/* Day columns */}
				{daysConfig.map((day) => {
					const dayEvents = eventsByDay[day.key] || [];
					return (
						<div className="cm-day-col" key={day.key} data-day={day.key}>
							<div className="cm-day-header">
								<span className="cm-day-title">{day.label}</span>
								{day.dateLabel && <span className="cm-day-sub">{day.dateLabel}</span>}
							</div>
							{/* hour rows background */}
							<div
								className="cm-day-content"
								style={{ height: (HOURS_END - HOURS_START) * 80 }}
								onClick={(e) => handleDayClick(day.key, e)}
							>
								{Array.from({ length: HOURS_END - HOURS_START }, (_, i) => (
									<div key={i} className="cm-hour-row" />
								))}
								{/* events absolutely positioned */}
								{dayEvents.map((ev, idx) => {
									const { top, height } = calculateEventPosition(ev.start, ev.end);
									return (
										<EventBlock
											key={`${day.key}-${idx}-${ev.course}-${ev.start}`}
											course={ev.course}
											type={ev.type}
											start={ev.start}
											end={ev.end}
											color={ev.color}
											metadata={ev.metadata}
											onSelect={onEventSelect}
											style={{
												top,
												height: Math.max(height, 28), // ensure minimum hit area
											}}
										/>
									);
								})}
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}


