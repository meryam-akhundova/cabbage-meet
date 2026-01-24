// EventBlock.jsx
import React from "react";

function readableTimeRange(start, end) {
	return `${start}–${end}`;
}

export default function EventBlock({ course, type, start, end, color, style, metadata, onSelect }) {
	const bg = color || "#A3C4F3";
	const isSuggestion = metadata?.eventType === 'suggestion';

	const handleClick = (event) => {
		event.stopPropagation();
		if (onSelect) {
			onSelect(metadata, event);
		}
	};

	// Special styling for suggestion events
	const suggestionStyle = isSuggestion ? {
		opacity: 0.85,
		border: '2px dashed #66BB6A',
		background: 'linear-gradient(135deg, rgba(129, 199, 132, 0.4), rgba(129, 199, 132, 0.6))',
		cursor: 'pointer',
		transition: 'all 0.2s ease',
	} : {};

	return (
		<div
			className="cm-event-block"
			style={{
				...style,
				backgroundColor: bg,
				...suggestionStyle,
			}}
			onClick={handleClick}
			title={isSuggestion ? `💡 ${course} - Click to create event` : `${course} ${type} ${readableTimeRange(start, end)}`}
			onMouseEnter={(e) => {
				if (isSuggestion) {
					e.currentTarget.style.opacity = '1';
					e.currentTarget.style.transform = 'scale(1.02)';
					e.currentTarget.style.boxShadow = '0 4px 8px rgba(129, 199, 132, 0.4)';
				}
			}}
			onMouseLeave={(e) => {
				if (isSuggestion) {
					e.currentTarget.style.opacity = '0.85';
					e.currentTarget.style.transform = 'scale(1)';
					e.currentTarget.style.boxShadow = 'none';
				}
			}}
		>
			<div className="cm-event-title">{course}</div>
			<div className="cm-event-sub">{type}</div>
			<div className="cm-event-time">{readableTimeRange(start, end)}</div>
		</div>
	);
}