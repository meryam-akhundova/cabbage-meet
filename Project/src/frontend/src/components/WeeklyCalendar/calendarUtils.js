export const JS_DAY_TO_KEY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function isSameDay(dateA, dateB) {
	if (!dateA || !dateB) return false;
	return (
		dateA.getFullYear() === dateB.getFullYear() &&
		dateA.getMonth() === dateB.getMonth() &&
		dateA.getDate() === dateB.getDate()
	);
}

export function getMonthMatrix(baseDate) {
	const viewDate = new Date(baseDate);
	const year = viewDate.getFullYear();
	const month = viewDate.getMonth();
	const firstOfMonth = new Date(year, month, 1);
	const startOffset = firstOfMonth.getDay(); // Sunday=0
	const gridStart = new Date(firstOfMonth);
	gridStart.setDate(firstOfMonth.getDate() - startOffset);

	const today = new Date();
	const weeks = [];

	for (let week = 0; week < 6; week++) {
		const days = [];
		for (let day = 0; day < 7; day++) {
			const cellDate = new Date(gridStart);
			cellDate.setDate(gridStart.getDate() + week * 7 + day);
			days.push({
				date: cellDate,
				label: cellDate.getDate(),
				inCurrentMonth: cellDate.getMonth() === month,
				isToday: isSameDay(cellDate, today),
				dayKey: JS_DAY_TO_KEY[cellDate.getDay()],
			});
		}
		weeks.push(days);
	}
	return weeks;
}

export function getYearMonths(baseDate) {
	const yearDate = new Date(baseDate);
	const year = yearDate.getFullYear();
	const months = [];
	for (let m = 0; m < 12; m++) {
		const monthDate = new Date(year, m, 1);
		months.push({
			label: monthDate.toLocaleDateString('en-US', { month: 'long' }),
			matrix: getMonthMatrix(monthDate),
		});
	}
	return months;
}


