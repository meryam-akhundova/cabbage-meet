// src/stores/useCalendars.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useCalendars = create(
  persist(
    (set) => ({
      calendars: [
        { id: 1, name: "School", color: "#8B5CF6", visible: true },
        { id: 2, name: "Personal", color: "#10B981", visible: true },
        { id: 3, name: "Work", color: "#F59E0B", visible: true },
      ],

      addCalendar: (name, color = "#3B82F6") =>
        set((state) => ({
          calendars: [...state.calendars, { id: Date.now(), name, color, visible: true }],
        })),

      toggleCalendar: (id) =>
        set((state) => ({
          calendars: state.calendars.map((c) =>
            c.id === id ? { ...c, visible: !c.visible } : c
          ),
        })),

      deleteCalendar: (id) =>
        set((state) => ({
          calendars: state.calendars.filter((c) => c.id !== id),
        })),
    }),
    { name: "cabbagemeet-calendars" } // saves to localStorage automatically
  )
)
