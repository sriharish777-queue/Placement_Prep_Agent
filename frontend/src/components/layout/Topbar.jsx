import { useNavigate, useLocation } from 'react-router-dom'
import { useStore } from '../../store/useStore'
import { Bell, LogOut, Search } from 'lucide-react'
import { useState } from 'react'

const PAGE_TITLES = {
  '/dashboard':   { title: 'Dashboard',       sub: 'Your placement journey at a glance' },
  '/resume':      { title: 'Resume',           sub: 'Upload and analyze your resume' },
  '/skill-gap':   { title: 'Skill Gap',        sub: 'Find what you need to learn' },
  '/plan':        { title: 'Preparation Plan', sub: 'Your personalized study roadmap' },
  '/practice':    { title: 'Practice',         sub: 'DSA, SQL, Aptitude, CS Fundamentals' },
  '/interview':   { title: 'Mock Interview',   sub: 'Simulate real placement interviews' },
  '/performance': { title: 'Performance',      sub: 'Track your readiness and progress' },
  '/assistant':   { title: 'AI Assistant',     sub: 'RAG-powered career guidance' },
  '/profile':     { title: 'Profile',          sub: 'Manage your account settings' },
}

export default function Topbar() {
  const { user, logout } = useStore()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const page = PAGE_TITLES[pathname] || { title: 'PrepCopilot', sub: '' }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-16 shrink-0 bg-white border-b border-surface-200 flex items-center justify-between px-6 z-20">
      <div>
        <h1 className="text-lg font-bold text-gray-900 leading-tight">{page.title}</h1>
        <p className="text-xs text-gray-400">{page.sub}</p>
      </div>

      <div className="flex items-center gap-2">
        <button className="btn-ghost text-gray-400 hover:text-gray-600 p-2">
          <Bell size={18} />
        </button>
        <div className="flex items-center gap-2 pl-2 border-l border-surface-200">
          <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <button onClick={handleLogout} className="btn-ghost text-gray-400 hover:text-red-500 p-2">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
