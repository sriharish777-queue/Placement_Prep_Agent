import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useStore = create(
  persist(
    (set, get) => ({
      // ── Auth ──────────────────────────────────────────────────────────────
      user: null,
      setUser: (user) => set({ user }),
      logout: () => set({ user: null, activeResume: null, activePlan: null, skillGap: null }),

      // ── Resume ────────────────────────────────────────────────────────────
      activeResume: null,
      setActiveResume: (resume) => set({ activeResume: resume }),

      // ── Skill Gap ─────────────────────────────────────────────────────────
      skillGap: null,
      setSkillGap: (gap) => set({ skillGap: gap }),

      // ── Preparation Plan ──────────────────────────────────────────────────
      activePlan: null,
      setActivePlan: (plan) => set({ activePlan: plan }),

      // ── Dashboard ─────────────────────────────────────────────────────────
      dashboard: null,
      setDashboard: (data) => set({ dashboard: data }),

      // ── UI ────────────────────────────────────────────────────────────────
      sidebarOpen: true,
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
    }),
    {
      name: 'placement-prep-store',
      partialize: (state) => ({
        user: state.user,
        activeResume: state.activeResume,
        skillGap: state.skillGap,
        activePlan: state.activePlan,
      }),
    }
  )
)
