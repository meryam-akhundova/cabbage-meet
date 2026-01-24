// DayCalendar.jsx
import React, { useMemo } from "react";
import "./WeeklyCalendar.css";
import EventBlock from "./EventBlock";
import { HOURS_START, HOURS_END, getHourLabels, calculateEventPosition, minutesToTimeString } from "./timeUtils";

export default function DayCalendar({ events = [], dayKey = "Mon", dayLabel = "Today", dayDate = null, onSlotSelect, onEventSelect }) {
	const hourLabels = useMemo(() => getHourLabels(), []);
	const filtered = useMemo(() => events.filter(e => e.day === dayKey), [events, dayKey]);

	const handleClick = (event) => {
		if (!onSlotSelect) return;
		const rect = event.currentTarget.getBoundingClientRect();
		let offsetY = event.clientY - rect.top;
		offsetY = Math.max(0, Math.min(offsetY, rect.height));
		const minutesFromStart = Math.round(offsetY);
		const absoluteMinutes = HOURS_START * 60 + minutesFromStart;
		onSlotSelect({
			day: dayKey,
			time: minutesToTimeString(absoluteMinutes),
			minutesFromStart: absoluteMinutes,
			dayDate,
			clientX: event.clientX,
			clientY: event.clientY,
		});
	};

	return (
		<div className="cm-calendar-wrapper" role="region" aria-label={`Day calendar ${dayLabel}`}>
			<div className="cm-calendar-grid" style={{ gridTemplateColumns: "90px minmax(0, 1fr)" }}>
				{/* Time column */}
				<div className="cm-time-col">
					<div className="cm-day-header" aria-hidden>Time</div>
					{hourLabels.map((h) => (
						<div className="cm-time-label" key={h}>{h}</div>
					))}
				</div>
				{/* Single day column */}
				<div className="cm-day-col">
					<div className="cm-day-header">
						<span className="cm-day-title">{dayLabel}</span>
					</div>
					<div
						className="cm-day-content"
						style={{ height: (HOURS_END - HOURS_START) * 60 }}
						onClick={handleClick}
					>
						{Array.from({ length: HOURS_END - HOURS_START }, (_, i) => (
							<div key={i} className="cm-hour-row" />
						))}
						{filtered.map((ev, idx) => {
							const { top, height } = calculateEventPosition(ev.start, ev.end);
							return (
								<EventBlock
									key={`${dayKey}-${idx}-${ev.course}-${ev.start}`}
									course={ev.course}
									type={ev.type}
									start={ev.start}
									end={ev.end}
									color={ev.color}
									metadata={ev.metadata}
									onSelect={onEventSelect}
									style={{ top, height: Math.max(height, 28) }}
								/>
							);
						})}
					</div>
				</div>
			</div>
		</div>
	);
}


