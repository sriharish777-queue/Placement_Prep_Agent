import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { dashboardAPI } from '../api/client'
import { FullPageSpinner } from '../components/ui/Spinner'
import StatCard from '../components/ui/StatCard'
import { ProgressRingWithValue } from '../components/ui/ProgressRing'
import {
  Flame, CalendarDays, Mic, Code2, Target,
  ArrowRight, CheckCircle2, Clock, TrendingUp,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, ResponsiveContainer } from 'recharts'

const TOPIC_COLORS = {
  DSA: '#7c5af2', Java: '#3b82f6', Python: '#10b981', SQL: '#f59e0b',
  DBMS: '#ef4444', OS: '#8b5cf6', CN: '#06b6d4', Aptitude: '#f97316',
  OOP: '#ec4899', 'System Design': '#14b8a6',
}

export default function DashboardPage() {
  const { user, setDashboard, dashboard } = useStore()
  const [loading, setLoading] = useState(!dashboard)

  useEffect(() => {
    if (!user) return
    dashboardAPI.get(user.user_id || user.id).then(({ data }) => {
      setDashboard(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [user])

  if (loading) return <FullPageSpinner />

  const d = dashboard || {}
  const readiness = d.readiness || {}
  const plan = d.active_plan
  const stats = d.stats || {}
  const topicScores = readiness.topic_scores || []

  const radarData = topicScores.map(t => ({ topic: t.topic, score: t.score }))

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome banner */}
      <div className="relative bg-gradient-to-r from-brand-600 to-purple-600 rounded-3xl p-6 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute right-8 top-4 w-32 h-32 rounded-full bg-white blur-2xl" />
          <div className="absolute right-32 bottom-2 w-20 h-20 rounded-full bg-white blur-2xl" />
        </div>
        <div className="relative flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold">Good {getGreeting()}, {user?.name?.split(' ')[0]}! 👋</h2>
            <p className="text-purple-200 mt-1 text-sm">
              {plan
                ? `Day ${plan.current_day} of ${plan.timeline_days} • ${plan.today_focus?.join(', ') || 'No tasks today'}`
                : 'Upload your resume to get started.'}
            </p>
            {stats.practice_streak_days > 0 && (
              <div className="flex items-center gap-1.5 mt-3 bg-white/15 rounded-full px-3 py-1 w-fit text-sm">
                <Flame size={14} className="text-orange-300" />
                <span>{stats.practice_streak_days} day streak — keep it up!</span>
              </div>
            )}
          </div>
          <ProgressRingWithValue
            value={readiness.overall_score || 0}
            size={100}
            strokeWidth={8}
            color="#a78bfa"
            label="Readiness"
          />
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Readiness Score" value={`${readiness.overall_score || 0}%`}
          icon={TrendingUp} color="brand"
          subtitle="Overall placement readiness" />
        <StatCard title="Practice Streak" value={`${stats.practice_streak_days || 0} days`}
          icon={Flame} color="yellow"
          subtitle="Consecutive practice days" />
        <StatCard title="Mock Interviews" value={stats.completed_interviews || 0}
          icon={Mic} color="green"
          subtitle={`${stats.total_interviews || 0} total sessions`} />
        <StatCard title="Practice Sessions" value={stats.total_sessions || 0}
          icon={Code2} color="blue"
          subtitle="Total practice sessions" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's plan */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-5">
            <h3 className="section-title">Today's Plan</h3>
            <Link to="/plan" className="text-sm text-brand-600 font-semibold hover:text-brand-700 flex items-center gap-1">
              View full plan <ArrowRight size={14} />
            </Link>
          </div>

          {plan ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1 bg-surface-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-brand-500 to-purple-500 transition-all"
                    style={{ width: `${plan.overall_progress || 0}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-gray-600 shrink-0">
                  {plan.overall_progress}% complete
                </span>
              </div>

              {plan.today_focus?.map((topic, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-surface-50 border border-surface-200">
                  <div className="w-2 h-2 rounded-full" style={{ background: TOPIC_COLORS[topic] || '#7c5af2' }} />
                  <span className="text-sm font-medium text-gray-700">{topic}</span>
                  <span className="ml-auto badge-gray">{Math.round(60 / (plan.today_focus?.length || 1))} min</span>
                </div>
              ))}

              {(!plan.today_focus || plan.today_focus.length === 0) && (
                <div className="text-center py-8 text-gray-400">
                  <CheckCircle2 size={32} className="mx-auto mb-2 text-green-400" />
                  <p className="font-medium">All done for today!</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center py-10 gap-4">
              <CalendarDays size={40} className="text-gray-300" />
              <div className="text-center">
                <p className="font-semibold text-gray-600">No active plan yet</p>
                <p className="text-sm text-gray-400 mt-1">Upload your resume and run a skill gap analysis first</p>
              </div>
              <Link to="/resume" className="btn-primary">Get started</Link>
            </div>
          )}
        </div>

        {/* Skill radar */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="section-title">Skill Radar</h3>
            <Link to="/performance" className="text-sm text-brand-600 font-semibold hover:text-brand-700">
              Details
            </Link>
          </div>

          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e8ecf4" />
                <PolarAngleAxis dataKey="topic" tick={{ fontSize: 10, fill: '#6b7280' }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                <Radar dataKey="score" stroke="#7c5af2" fill="#7c5af2" fillOpacity={0.2} strokeWidth={2} />
                <Tooltip formatter={(v) => [`${v}%`, 'Score']} />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex flex-col items-center justify-center text-gray-400 gap-2">
              <Target size={28} className="text-gray-300" />
              <p className="text-sm">Practice to see your skill radar</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent sessions */}
      {d.recent_sessions?.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">Recent Sessions</h3>
          <div className="space-y-2">
            {d.recent_sessions.map((s, i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-xl hover:bg-surface-50 transition-colors">
                <div className="w-9 h-9 rounded-xl bg-brand-50 flex items-center justify-center shrink-0">
                  <Code2 size={16} className="text-brand-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">
                    {s.topics_covered?.join(', ') || 'Practice Session'}
                  </p>
                  <p className="text-xs text-gray-400">{s.questions_attempted} questions • {s.duration_minutes} min</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-bold text-gray-800">{s.score?.toFixed(0)}%</p>
                  <p className="text-xs text-gray-400">{formatDate(s.started_at)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { to: '/practice', icon: Code2, label: 'Practice Now', color: 'from-brand-500 to-purple-500' },
          { to: '/interview', icon: Mic, label: 'Mock Interview', color: 'from-green-500 to-teal-500' },
          { to: '/skill-gap', icon: Target, label: 'Skill Gap', color: 'from-orange-500 to-yellow-500' },
          { to: '/assistant', icon: TrendingUp, label: 'AI Assistant', color: 'from-pink-500 to-rose-500' },
        ].map(({ to, icon: Icon, label, color }) => (
          <Link
            key={to} to={to}
            className={`flex flex-col items-center gap-2 p-4 rounded-2xl bg-gradient-to-br ${color} text-white shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200`}
          >
            <Icon size={22} />
            <span className="text-sm font-semibold">{label}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}

function formatDate(iso) {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) }
  catch { return '' }
}
