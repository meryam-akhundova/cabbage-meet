import React, { useEffect, useState } from 'react';
import './TaskPopover.css';

const defaultForm = {
	id: null,
	title: '',
	groupId: '',
	dateISO: '',
	dayLabel: '',
	startTime: '10:00',
	duration: 60,
};

export default function TaskPopover({
	open,
	position,
	groups = [],
	initialData = defaultForm,
	onSave,
	onDelete,
	onClose,
}) {
	const [form, setForm] = useState(initialData);

	useEffect(() => {
		setForm(initialData);
	}, [initialData]);

	if (!open) return null;

	const handleSubmit = (e) => {
		e.preventDefault();
		if (!form.title.trim()) return;
		onSave?.(form);
	};

	const handleDelete = () => {
		if (form.id) {
			onDelete?.(form.id);
		}
	};

	const offsetStyle = {
		top: position?.y ?? 0,
		left: position?.x ?? 0,
	};

	return (
		<>
			<div className="task-popover__backdrop" onClick={onClose} />
			<form className="task-popover" style={offsetStyle} onSubmit={handleSubmit}>
				<div className="task-popover__header">
					<div>
						<p className="task-popover__day">{form.dayLabel}</p>
						<input
							type="text"
							value={form.title}
							onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
							placeholder="Task name"
						/>
					</div>
				</div>
				<div className="task-popover__row">
					<label>
						Time
						<input
							type="time"
							value={form.startTime}
							onChange={(e) => setForm((prev) => ({ ...prev, startTime: e.target.value }))}
						/>
					</label>
					<label>
						Duration (min)
						<input
							type="number"
							min="15"
							step="15"
							value={form.duration}
							onChange={(e) => setForm((prev) => ({ ...prev, duration: Number(e.target.value) }))}
						/>
					</label>
				</div>
				<label className="task-popover__select">
					Group
					<select
						value={form.groupId}
						onChange={(e) => setForm((prev) => ({ ...prev, groupId: e.target.value }))}
					>
						{groups.map((group) => (
							<option key={group.id} value={group.id}>
								{group.name}
							</option>
						))}
					</select>
				</label>

				<div className="task-popover__actions">
					<button type="button" onClick={onClose}>
						Cancel
					</button>
					{form.id && (
						<button type="button" className="danger" onClick={handleDelete}>
							Delete
						</button>
					)}
					<button type="submit" className="primary">
						{form.id ? 'Save' : 'Add'}
					</button>
				</div>
			</form>
		</>
	);
}


