import { NavLink } from 'react-router-dom'
import { useStore } from '../../store/useStore'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, FileText, Target, CalendarDays,
  Code2, Mic, BarChart3, MessageSquare, User, ChevronLeft,
  Zap,
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/resume',     icon: FileText,        label: 'Resume' },
  { to: '/skill-gap',  icon: Target,          label: 'Skill Gap' },
  { to: '/plan',       icon: CalendarDays,    label: 'My Plan' },
  { to: '/practice',   icon: Code2,           label: 'Practice' },
  { to: '/interview',  icon: Mic,             label: 'Mock Interview' },
  { to: '/performance',icon: BarChart3,       label: 'Performance' },
  { to: '/assistant',  icon: MessageSquare,   label: 'AI Assistant' },
  { to: '/profile',    icon: User,            label: 'Profile' },
]

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar, user } = useStore()

  return (
    <motion.aside
      animate={{ width: sidebarOpen ? 256 : 72 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen bg-white border-r border-surface-200 shadow-sm z-30 flex flex-col overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-surface-200 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center shrink-0 shadow-glow">
            <Zap size={18} className="text-white" />
          </div>
          {sidebarOpen && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="min-w-0"
            >
              <p className="text-sm font-bold text-gray-900 truncate leading-tight">PrepCopilot</p>
              <p className="text-xs text-gray-400 truncate">AI Placement Prep</p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-brand-50 text-brand-700 shadow-sm'
                  : 'text-gray-500 hover:bg-surface-100 hover:text-gray-800'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={18}
                  className={clsx(
                    'shrink-0 transition-colors',
                    isActive ? 'text-brand-600' : 'text-gray-400 group-hover:text-gray-600'
                  )}
                />
                {sidebarOpen && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="truncate"
                  >
                    {label}
                  </motion.span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User chip */}
      {user && sidebarOpen && (
        <div className="px-3 pb-4 pt-2 border-t border-surface-200 shrink-0">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-surface-50">
            <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold shrink-0">
              {user.name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-gray-800 truncate">{user.name}</p>
              <p className="text-xs text-gray-400 truncate">{user.target_role || 'Set a target role'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="absolute top-5 -right-3.5 w-7 h-7 bg-white border border-surface-300 rounded-full flex items-center justify-center shadow-sm hover:bg-surface-100 transition-colors z-10"
        aria-label="Toggle sidebar"
      >
        <motion.div animate={{ rotate: sidebarOpen ? 0 : 180 }} transition={{ duration: 0.25 }}>
          <ChevronLeft size={14} className="text-gray-500" />
        </motion.div>
      </button>
    </motion.aside>
  )
}
