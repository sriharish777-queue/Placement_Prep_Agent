import { useEffect, useState } from 'react'
import { useStore } from '../store/useStore'
import { planAPI } from '../api/client'
import { FullPageSpinner } from '../components/ui/Spinner'
import EmptyState from '../components/ui/EmptyState'
import { CalendarDays, CheckCircle2, Circle, ChevronDown, ChevronUp, Clock, BookOpen, Zap, RotateCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import toast from 'react-hot-toast'

const DIFFICULTY_BADGE = {
  easy: 'badge-green', medium: 'badge-yellow', hard: 'badge-red',
}
const TOPIC_EMOJI = {
  DSA: '🧮', SQL: '🗄️', Java: '☕', Python: '🐍', OOP: '🔷',
  DBMS: '🔌', OS: '💻', CN: '🌐', Aptitude: '🧠', 'System Design': '🏗️',
  'Spring Boot': '🌱', 'REST API': '🔗', Behavioral: '🤝', Communication: '💬',
  Tableau: '📊', 'Power BI': '📈', Excel: '📗', 'A/B Testing': '🧪',
  'Business Metrics': '💼', 'Case Study': '🎯', 'Mock Interview': '🎙️',
  Revision: '📝', 'Data Warehousing': '🏢',
}

export default function PlanPage() {
  const { user, activePlan, setActivePlan } = useStore()
  const [loading, setLoading] = useState(false)
  const [expandedDay, setExpandedDay] = useState(null)
  const [completing, setCompleting] = useState(null)

  const fetchPlan = async () => {
    const userId = user?.user_id || user?.id
    if (!userId) return
    setLoading(true)
    try {
      const { data } = await planAPI.getUserPlans(userId)
      if (data.plans?.length > 0) {
        setActivePlan({ ...data.plans[0] })
      }
    } catch {
      // handled
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!user) return
    if (!activePlan || !activePlan.days || activePlan.days.length === 0) {
      fetchPlan()
    }
  }, [user, activePlan])

  const handleCompleteDay = async (day) => {
    if (!activePlan?.id) return
    setCompleting(day)
    try {
      const { data } = await planAPI.completeDay(activePlan.id, {
        user_id: user?.user_id || user?.id,
        day,
        performance: { score: 70 },
      })
      toast.success(`Day ${day} completed! Progress: ${data.overall_progress}%`)
      setActivePlan({ ...activePlan, overall_progress: data.overall_progress,
        days: activePlan.days.map(d => d.day === day ? { ...d, completed: true } : d) })
    } catch {
      // handled
    } finally {
      setCompleting(null)
    }
  }

  if (loading) return <FullPageSpinner />

  const plan = activePlan
  const completedCount = plan?.days?.filter(d => d.completed).length || 0
  const totalDays = plan?.days?.length || 0
  const currentDay = completedCount + 1

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Preparation Plan</h1>
          <p className="page-subtitle">Your personalized day-by-day study roadmap</p>
        </div>
        {plan && (
          <button
            onClick={fetchPlan}
            className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3"
            title="Reload plan from server"
          >
            <RotateCw size={13} /> Refresh Plan
          </button>
        )}
      </div>

      {!plan ? (
        <EmptyState
          icon={CalendarDays}
          title="No active plan"
          description="Complete a skill gap analysis first to generate your personalized plan"
          action={<Link to="/skill-gap" className="btn-primary">Start Skill Gap Analysis</Link>}
        />
      ) : (
        <>
          {/* Plan overview */}
          <div className="card bg-gradient-to-r from-brand-600 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-extrabold">{plan.target_role}</h3>
                {plan.target_company && <p className="text-purple-200 text-sm">{plan.target_company}</p>}
                <div className="flex items-center gap-3 mt-3">
                  <span className="flex items-center gap-1.5 text-sm bg-white/20 px-3 py-1 rounded-full">
                    <CalendarDays size={13} /> {plan.timeline_days}-day plan
                  </span>
                  <span className="flex items-center gap-1.5 text-sm bg-white/20 px-3 py-1 rounded-full">
                    <CheckCircle2 size={13} /> Day {currentDay} of {totalDays}
                  </span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold">{plan.overall_progress || 0}%</div>
                <div className="text-purple-200 text-xs mt-1">Complete</div>
              </div>
            </div>
            <div className="mt-4 bg-white/20 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-white transition-all duration-500"
                style={{ width: `${plan.overall_progress || 0}%` }}
              />
            </div>
          </div>

          {/* Day list */}
          <div className="space-y-3">
            {plan.days?.map((day) => {
              const isToday = day.day === currentDay
              const isPast = day.day < currentDay
              const isFuture = day.day > currentDay
              const isExpanded = expandedDay === day.day

              return (
                <motion.div
                  key={day.day}
                  layout
                  className={clsx(
                    'card transition-all duration-200',
                    isToday && 'border-brand-300 ring-2 ring-brand-100 shadow-glow',
                    isPast && 'opacity-70',
                    isFuture && 'opacity-60'
                  )}
                >
                  <div
                    className="flex items-center gap-4 cursor-pointer"
                    onClick={() => setExpandedDay(isExpanded ? null : day.day)}
                  >
                    {/* Day indicator */}
                    <div className={clsx(
                      'w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold shrink-0',
                      day.completed ? 'bg-green-100 text-green-700' :
                      isToday ? 'bg-brand-600 text-white shadow-glow' :
                      'bg-surface-100 text-gray-500'
                    )}>
                      {day.completed ? <CheckCircle2 size={18} /> : day.day}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-900 text-sm">
                          Day {day.day}
                          {isToday && <span className="ml-2 badge-purple">Today</span>}
                          {day.completed && <span className="ml-2 badge-green">Done</span>}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {day.focus_areas?.map(f => (
                          <span key={f} className="text-xs text-gray-500 flex items-center gap-0.5">
                            {TOPIC_EMOJI[f] || '📌'} {f}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className="flex items-center gap-1 text-xs text-gray-400">
                        <Clock size={12} /> {day.total_duration_minutes} min
                      </span>
                      {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                    </div>
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-4 pt-4 border-t border-surface-200 space-y-2">
                          {day.tasks?.map((task, ti) => (
                            <div key={ti} className="flex items-center gap-3 p-3 rounded-xl bg-surface-50">
                              <span className="text-lg">{TOPIC_EMOJI[task.topic] || '📌'}</span>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-800">{task.topic} — {task.subtopic}</p>
                                <p className="text-xs text-gray-400">{task.practice_questions} questions</p>
                              </div>
                              <span className={DIFFICULTY_BADGE[task.difficulty] || 'badge-gray'}>{task.difficulty}</span>
                              <span className="text-xs text-gray-400">{task.duration_minutes}m</span>
                            </div>
                          ))}

                          {isToday && !day.completed && (
                            <button
                              onClick={() => handleCompleteDay(day.day)}
                              disabled={completing === day.day}
                              className="btn-primary w-full justify-center mt-2"
                            >
                              <CheckCircle2 size={16} />
                              {completing === day.day ? 'Saving…' : 'Mark Day Complete'}
                            </button>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
