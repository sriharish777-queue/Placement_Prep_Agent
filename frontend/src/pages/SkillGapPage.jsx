import { useState } from 'react'
import { useStore } from '../store/useStore'
import { skillGapAPI, planAPI } from '../api/client'
import toast from 'react-hot-toast'
import Spinner from '../components/ui/Spinner'
import { ProgressRingWithValue } from '../components/ui/ProgressRing'
import { Target, ChevronRight, Zap, AlertCircle, CheckCircle2, MinusCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

const LEVEL_CONFIG = {
  strong:   { label: 'Strong',   color: 'badge-green',  icon: CheckCircle2,  iconColor: 'text-green-500'  },
  moderate: { label: 'Moderate', color: 'badge-yellow', icon: MinusCircle,   iconColor: 'text-yellow-500' },
  weak:     { label: 'Weak',     color: 'badge-red',    icon: AlertCircle,   iconColor: 'text-orange-500' },
  missing:  { label: 'Missing',  color: 'badge-gray',   icon: AlertCircle,   iconColor: 'text-red-500'    },
}

export default function SkillGapPage() {
  const { user, activeResume, skillGap, setSkillGap, setActivePlan } = useStore()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    job_description: '',
    target_role: user?.target_role || '',
    target_company: user?.target_company || '',
    timeline_days: '30',
  })
  const [loading, setLoading] = useState(false)
  const [genPlan, setGenPlan] = useState(false)

  const handleAnalyze = async () => {
    if (!activeResume?.id) {
      toast.error('Please upload your resume first')
      return
    }
    if (!form.job_description.trim()) {
      toast.error('Paste a job description to analyze')
      return
    }
    setLoading(true)
    try {
      const { data } = await skillGapAPI.analyze({
        user_id: user?.user_id || user?.id,
        resume_id: activeResume.id,
        job_description: form.job_description,
        target_role: form.target_role,
        target_company: form.target_company || undefined,
      })
      setSkillGap({ ...data.analysis, id: data.skill_gap_id })
      toast.success('Skill gap analysis complete!')
    } catch {
      // handled
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePlan = async () => {
    setGenPlan(true)
    try {
      const { data } = await planAPI.generate({
        user_id: user?.user_id || user?.id,
        skill_gap_id: skillGap.id,
        timeline_days: parseInt(form.timeline_days),
        hours_per_day: 3,
      })
      setActivePlan({ ...data.plan, id: data.plan_id })
      toast.success('Preparation plan generated!')
      navigate('/plan')
    } catch {
      // handled
    } finally {
      setGenPlan(false)
    }
  }

  const sg = skillGap

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Skill Gap Analysis</h1>
        <p className="page-subtitle">Paste a job description and let AI identify exactly what you need to work on</p>
      </div>

      {/* Input form */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-gray-900">Job Description Analysis</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Target Role *</label>
            <input className="input" value={form.target_role} onChange={e => setForm({ ...form, target_role: e.target.value })}
              placeholder="Software Developer" />
          </div>
          <div>
            <label className="label">Target Company</label>
            <input className="input" value={form.target_company} onChange={e => setForm({ ...form, target_company: e.target.value })}
              placeholder="Optional" />
          </div>
        </div>

        <div>
          <label className="label">Job Description *</label>
          <textarea
            className="input min-h-[160px] resize-none"
            value={form.job_description}
            onChange={e => setForm({ ...form, job_description: e.target.value })}
            placeholder="Paste the full job description here…"
          />
        </div>

        <div className="flex items-center gap-4">
          <div>
            <label className="label">Prep Timeline</label>
            <select className="input w-40" value={form.timeline_days} onChange={e => setForm({ ...form, timeline_days: e.target.value })}>
              <option value="7">7 days</option>
              <option value="14">14 days</option>
              <option value="30">30 days</option>
            </select>
          </div>
          <div className="flex-1" />
          <button onClick={handleAnalyze} disabled={loading} className="btn-primary mt-5">
            {loading ? <><Spinner size="sm" /> Analyzing…</> : <><Target size={16} /> Analyze Gap</>}
          </button>
        </div>

        {!activeResume && (
          <div className="flex items-center gap-2 text-sm text-orange-600 bg-orange-50 rounded-xl px-4 py-3 border border-orange-100">
            <AlertCircle size={16} />
            Upload your resume first for a personalized analysis
          </div>
        )}
      </div>

      {/* Results */}
      <AnimatePresence>
        {sg && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Match banner */}
            <div className="card bg-gradient-to-r from-brand-50 to-purple-50 border-brand-100 flex items-center gap-6">
              <ProgressRingWithValue
                value={sg.match_percentage || 0}
                size={100}
                color={
                  sg.match_percentage >= 70 ? '#10b981' :
                  sg.match_percentage >= 50 ? '#f59e0b' : '#ef4444'
                }
                label="Match %"
              />
              <div className="flex-1">
                <h3 className="text-xl font-extrabold text-gray-900">
                  {sg.match_percentage >= 70 ? 'Strong Match' :
                   sg.match_percentage >= 50 ? 'Moderate Match' : 'Needs Work'}
                </h3>
                <p className="text-gray-600 text-sm mt-1">{sg.analysis_summary}</p>
                <div className="flex flex-wrap gap-2 mt-3">
                  <span className="badge-green">{sg.strong_skills?.length || 0} Strong</span>
                  <span className="badge-yellow">{sg.moderate_skills?.length || 0} Moderate</span>
                  <span className="badge-red">{sg.weak_skills?.length || 0} Weak</span>
                  <span className="badge-gray">{sg.missing_skills?.length || 0} Missing</span>
                </div>
              </div>
            </div>

            {/* Skill breakdown */}
            <div className="grid grid-cols-2 gap-4">
              {[
                { key: 'strong_skills',   label: '✓ Strong',   cls: 'badge-green'  },
                { key: 'moderate_skills', label: '△ Moderate', cls: 'badge-yellow' },
                { key: 'weak_skills',     label: '✗ Weak',     cls: 'badge-red'    },
                { key: 'missing_skills',  label: '○ Missing',  cls: 'badge-gray'   },
              ].map(({ key, label, cls }) => (
                sg[key]?.length > 0 && (
                  <div key={key} className="card">
                    <p className="text-sm font-semibold text-gray-700 mb-3">{label}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {sg[key].map(s => <span key={s} className={cls}>{s}</span>)}
                    </div>
                  </div>
                )
              ))}
            </div>

            {/* Priority order */}
            {sg.priority_order?.length > 0 && (
              <div className="card">
                <h3 className="font-semibold text-gray-900 mb-4">Learning Priority</h3>
                <div className="space-y-2">
                  {sg.priority_order.slice(0, 8).map((skill, i) => {
                    const gap = sg.skill_gaps?.find(g => g.skill === skill)
                    const cfg = LEVEL_CONFIG[gap?.level || 'missing']
                    const Icon = cfg.icon
                    return (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-surface-50 border border-surface-200">
                        <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center shrink-0">
                          {i + 1}
                        </span>
                        <Icon size={16} className={`shrink-0 ${cfg.iconColor}`} />
                        <span className="text-sm font-medium text-gray-800 flex-1">{skill}</span>
                        <span className={`${cfg.color} shrink-0`}>{cfg.label}</span>
                        {gap?.importance === 'high' && <Zap size={13} className="text-yellow-500" />}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Generate plan CTA */}
            <div className="card bg-gradient-to-r from-brand-600 to-purple-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-lg">Ready to start preparing?</h3>
                  <p className="text-purple-200 text-sm mt-1">
                    Generate a personalized {form.timeline_days}-day plan based on this analysis
                  </p>
                </div>
                <button onClick={handleGeneratePlan} disabled={genPlan}
                  className="flex items-center gap-2 bg-white text-brand-700 font-bold text-sm px-5 py-3 rounded-xl hover:bg-purple-50 active:scale-95 transition-all disabled:opacity-60 shrink-0">
                  {genPlan ? <Spinner size="sm" /> : <ChevronRight size={18} />}
                  {genPlan ? 'Generating…' : 'Generate Plan'}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
