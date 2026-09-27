import { useEffect, useState } from 'react'
import { useStore } from '../store/useStore'
import { performanceAPI } from '../api/client'
import { FullPageSpinner } from '../components/ui/Spinner'
import { ProgressRingWithValue } from '../components/ui/ProgressRing'
import StatCard from '../components/ui/StatCard'
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts'
import { TrendingUp, AlertTriangle, CheckCircle2, Clock, Target } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const TOPIC_COLORS = [
  '#7c5af2', '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#14b8a6',
]

const LEVEL_COLOR = (score) => score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'

export default function PerformancePage() {
  const { user } = useStore()
  const [readiness, setReadiness] = useState(null)
  const [weakness, setWeakness] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    const uid = user?.user_id || user?.id
    Promise.all([
      performanceAPI.getReadiness(uid),
      performanceAPI.getWeakness(uid),
      performanceAPI.getHistory(uid),
    ]).then(([r, w, h]) => {
      setReadiness(r.data)
      setWeakness(w.data)
      setHistory(h.data.sessions || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [user])

  if (loading) return <FullPageSpinner />

  const topicScores = readiness?.topic_scores || []
  const historyChartData = history.slice(0, 14).reverse().map((s, i) => ({
    day: `S${i + 1}`,
    score: s.score || 0,
    topic: s.topics_covered?.[0] || 'Practice',
  }))

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Performance</h1>
        <p className="page-subtitle">Track your readiness and identify areas to improve</p>
      </div>

      {/* Overall readiness */}
      <div className="card bg-gradient-to-r from-brand-600 to-purple-600 text-white">
        <div className="flex items-center gap-8">
          <ProgressRingWithValue value={readiness?.overall_score || 0} size={110} strokeWidth={9} color="#a78bfa" />
          <div className="flex-1">
            <h3 className="text-2xl font-extrabold">Placement Readiness</h3>
            <p className="text-purple-200 mt-1 text-sm">{readiness?.recommendation}</p>
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="bg-white/15 rounded-xl p-3 text-center">
                <p className="text-2xl font-extrabold">{readiness?.overall_score?.toFixed(0) || 0}%</p>
                <p className="text-xs text-purple-200">Overall</p>
              </div>
              <div className="bg-white/15 rounded-xl p-3 text-center">
                <p className="text-2xl font-extrabold">{readiness?.interview_readiness?.toFixed(0) || 0}%</p>
                <p className="text-xs text-purple-200">Interview Ready</p>
              </div>
              <div className="bg-white/15 rounded-xl p-3 text-center">
                <p className="text-2xl font-extrabold">{topicScores.filter(t => t.score >= 75).length}</p>
                <p className="text-xs text-purple-200">Strong Topics</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topic score bars */}
        <div className="card">
          <h3 className="section-title mb-5">Topic Breakdown</h3>
          {topicScores.length > 0 ? (
            <div className="space-y-3">
              {topicScores.sort((a, b) => b.score - a.score).map((t, i) => (
                <motion.div key={t.topic}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="space-y-1"
                >
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-700">{t.topic}</span>
                    <div className="flex items-center gap-2">
                      <span className={clsx(
                        'text-xs font-semibold',
                        t.trend === 'improving' ? 'text-green-600' :
                        t.trend === 'declining' ? 'text-red-500' : 'text-gray-500'
                      )}>
                        {t.trend === 'improving' ? '↑' : t.trend === 'declining' ? '↓' : '→'}
                      </span>
                      <span className="font-bold text-gray-900">{t.score.toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className="h-2 bg-surface-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${t.score}%` }}
                      transition={{ duration: 0.6, delay: i * 0.05 }}
                      className="h-full rounded-full"
                      style={{ background: LEVEL_COLOR(t.score) }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center py-10 text-gray-400 gap-2">
              <Target size={32} className="text-gray-300" />
              <p className="text-sm">Practice to see your topic scores</p>
            </div>
          )}
        </div>

        {/* Score history */}
        <div className="card">
          <h3 className="section-title mb-5">Score History</h3>
          {historyChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={historyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8ecf4" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <Tooltip
                  formatter={(v) => [`${v.toFixed(0)}%`, 'Score']}
                  contentStyle={{ borderRadius: 10, border: '1px solid #e8ecf4', fontSize: 12 }}
                />
                <Line type="monotone" dataKey="score" stroke="#7c5af2" strokeWidth={2.5}
                  dot={{ fill: '#7c5af2', r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center py-10 text-gray-400 gap-2">
              <TrendingUp size={32} className="text-gray-300" />
              <p className="text-sm">Complete practice sessions to see your trend</p>
            </div>
          )}
        </div>
      </div>

      {/* Weakness report */}
      {weakness && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="section-title mb-4">
              <span className="flex items-center gap-2"><AlertTriangle size={18} className="text-orange-500" /> Areas Needing Work</span>
            </h3>
            <div className="space-y-2">
              {weakness.weak_topics?.map(t => (
                <div key={t} className="flex items-center gap-3 p-3 rounded-xl bg-orange-50 border border-orange-100">
                  <AlertTriangle size={14} className="text-orange-500 shrink-0" />
                  <span className="text-sm font-medium text-orange-800">{t}</span>
                </div>
              ))}
              {weakness.critical_gaps?.map(t => (
                <div key={t} className="flex items-center gap-3 p-3 rounded-xl bg-red-50 border border-red-100">
                  <AlertTriangle size={14} className="text-red-500 shrink-0" />
                  <span className="text-sm font-medium text-red-800">{t}</span>
                  <span className="ml-auto badge-red text-xs">Critical</span>
                </div>
              ))}
              {!weakness.weak_topics?.length && !weakness.critical_gaps?.length && (
                <div className="flex items-center gap-2 p-3 rounded-xl bg-green-50 text-green-700">
                  <CheckCircle2 size={16} /> No critical weak areas detected
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h3 className="section-title mb-4">
              <span className="flex items-center gap-2"><Target size={18} className="text-brand-600" /> Suggested Focus</span>
            </h3>
            <div className="space-y-2">
              {weakness.suggested_focus?.map((t, i) => (
                <div key={t} className="flex items-center gap-3 p-3 rounded-xl bg-brand-50 border border-brand-100">
                  <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                  <span className="text-sm font-medium text-brand-800">{t}</span>
                </div>
              ))}
            </div>
            {weakness.estimated_days_to_readiness > 0 && (
              <div className="mt-4 flex items-center gap-2 text-sm text-gray-500 bg-surface-50 rounded-xl p-3 border border-surface-200">
                <Clock size={14} />
                Estimated {weakness.estimated_days_to_readiness} days to reach 75% readiness
              </div>
            )}
          </div>
        </div>
      )}

      {/* Strengths */}
      {readiness?.strengths?.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">
            <span className="flex items-center gap-2"><CheckCircle2 size={18} className="text-green-500" /> Your Strengths</span>
          </h3>
          <div className="flex flex-wrap gap-2">
            {readiness.strengths.map(s => (
              <span key={s} className="badge-green text-sm py-1 px-3">{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


