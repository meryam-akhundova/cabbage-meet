import React, { useMemo } from "react";
import "./WeeklyCalendar.css";
import { getYearMonths } from "./calendarUtils";

export default function YearCalendar({ currentDate }) {
        const months = useMemo(() => getYearMonths(currentDate), [currentDate]);
        return (
                <div className="cm-year-wrapper">
                        {months.map((month) => (
                                <div key={month.label} className="cm-year-month">
                                        <div className="cm-year-month-title">{month.label}</div>
                                        <div className="cm-mini-month">
                                                <div className="cm-mini-month-header">
                                                        {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map((label) => (
                                                                <span key={label}>{label[0]}</span>
                                                        ))}
                                                </div>
                                                <div className="cm-mini-month-body">
                                                        {month.matrix.map((week, idx) => (
                                                                <div key={idx} className="cm-mini-week">
                                                                        {week.map((day) => (
                                                                                <span
                                                                                        key={day.date.toISOString()}
                                                                                        className={`cm-mini-day ${day.inCurrentMonth ? '' : 'muted'} ${day.isToday ? 'today' : ''}`}
                                                                                >
                                                                                        {day.label}
                                                                                </span>
                                                                        ))}
                                                                </div>
                                                        ))}
                                                </div>
                                        </div>
                                </div>
                        ))}
                </div>
        );
}