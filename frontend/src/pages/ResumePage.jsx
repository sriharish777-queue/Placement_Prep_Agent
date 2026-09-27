import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useStore } from '../store/useStore'
import { resumeAPI } from '../api/client'
import toast from 'react-hot-toast'
import {
  Upload, FileText, CheckCircle2, ChevronDown, ChevronUp,
  Wrench, BookOpen, User, Zap, TrendingUp, AlertTriangle,
  Lightbulb, Target, Copy, RefreshCw, Star, Award,
} from 'lucide-react'
import Spinner from '../components/ui/Spinner'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import { ProgressRingWithValue } from '../components/ui/ProgressRing'

// ── Score colour helper ───────────────────────────────────────────────────────
const scoreColor = (s) =>
  s >= 75 ? '#10b981' : s >= 50 ? '#f59e0b' : '#ef4444'

const scoreLabel = (s) =>
  s >= 75 ? 'Strong' : s >= 50 ? 'Good' : 'Needs Work'

const scoreBadge = (s) =>
  s >= 75 ? 'badge-green' : s >= 50 ? 'badge-yellow' : 'badge-red'

export default function ResumePage() {
  const { user, activeResume, setActiveResume } = useStore()

  // Upload state
  const [uploading, setUploading]   = useState(false)
  const [expanded, setExpanded]     = useState('skills')

  // Improvement state
  const [improving, setImproving]   = useState(false)
  const [improvements, setImprovements] = useState(null)
  const [targetRole, setTargetRole] = useState(user?.target_role || '')
  const [targetCompany, setTargetCompany] = useState(user?.target_company || '')
  const [copiedSummary, setCopiedSummary] = useState(false)

  // ── Dropzone ───────────────────────────────────────────────────────────────
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return
    setUploading(true)
    setImprovements(null)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', user?.user_id || user?.id || '')
    try {
      const { data } = await resumeAPI.upload(formData)
      setActiveResume({ ...data.analysis, id: data.resume_id })
      toast.success('Resume analysed successfully!')
    } catch {
      // handled by interceptor
    } finally {
      setUploading(false)
    }
  }, [user])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  // ── Get improvements ───────────────────────────────────────────────────────
  const handleImprove = async () => {
    if (!activeResume?.id) { toast.error('Upload a resume first'); return }
    setImproving(true)
    try {
      const { data } = await resumeAPI.improve({
        resume_id: activeResume.id,
        target_role: targetRole || undefined,
        target_company: targetCompany || undefined,
      })
      setImprovements(data.improvements)
      toast.success('Improvement analysis ready!')
      // Auto scroll to improvements
      setTimeout(() => {
        document.getElementById('improvements-section')?.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    } catch {
      // handled
    } finally {
      setImproving(false)
    }
  }

  const handleCopySummary = () => {
    if (improvements?.rewrite_summary) {
      navigator.clipboard.writeText(improvements.rewrite_summary)
      setCopiedSummary(true)
      toast.success('Summary copied!')
      setTimeout(() => setCopiedSummary(false), 2000)
    }
  }

  const a = activeResume

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Page header */}
      <div className="page-header">
        <h1 className="page-title">Resume Intelligence</h1>
        <p className="page-subtitle">
          Upload your resume for AI analysis and get actionable improvement suggestions
        </p>
      </div>

      {/* ── Dropzone ─────────────────────────────────────────────────────── */}
      <div
        {...getRootProps()}
        className={clsx(
          'relative border-2 border-dashed rounded-3xl p-10 text-center cursor-pointer transition-all duration-200',
          isDragActive
            ? 'border-brand-400 bg-brand-50'
            : 'border-surface-300 bg-white hover:border-brand-300 hover:bg-brand-50/40',
          uploading && 'pointer-events-none'
        )}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3 py-4">
            <Spinner size="lg" />
            <p className="text-sm font-semibold text-gray-700">
              Analysing your resume with AI…
            </p>
            <p className="text-xs text-gray-400">
              Running parallel AI calls — typically 15–25 seconds
            </p>
            <div className="flex gap-1 mt-1">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full bg-brand-300 animate-bounce"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-2xl bg-brand-50 flex items-center justify-center">
              <Upload size={26} className="text-brand-500" />
            </div>
            <div>
              <p className="text-base font-semibold text-gray-700">
                {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
              </p>
              <p className="text-sm text-gray-400 mt-1">PDF or DOCX · Max 10 MB</p>
            </div>
            <span className="btn-secondary mt-1">Browse files</span>
          </div>
        )}
      </div>

      {/* ── Analysis results ─────────────────────────────────────────────── */}
      <AnimatePresence>
        {a && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Summary banner */}
            <div className="card bg-gradient-to-r from-brand-50 to-purple-50 border-brand-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-brand-100 flex items-center justify-center shrink-0">
                  <FileText size={22} className="text-brand-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 text-lg">Resume Analysed</h3>
                  <p className="text-gray-600 text-sm mt-1">
                    {a.summary || 'AI analysis complete. Check your skills and projects below.'}
                  </p>
                </div>
                <CheckCircle2 size={24} className="text-green-500 shrink-0" />
              </div>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Skills',     value: a.skills?.length || 0,      icon: Wrench,   bg: 'bg-brand-50',  text: 'text-brand-600' },
                { label: 'Projects',   value: a.projects?.length || 0,    icon: BookOpen, bg: 'bg-green-50',  text: 'text-green-600' },
                { label: 'Experience', value: a.experiences?.length || 0, icon: User,     bg: 'bg-blue-50',   text: 'text-blue-600'  },
              ].map(({ label, value, icon: Icon, bg, text }) => (
                <div key={label} className={clsx('card text-center border-0', bg)}>
                  <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-2', bg)}>
                    <Icon size={18} className={text} />
                  </div>
                  <p className="text-3xl font-extrabold text-gray-900">{value}</p>
                  <p className="text-sm text-gray-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Expandable sections */}
            {[
              {
                id: 'skills',
                title: 'Skills Extracted',
                count: a.skills?.length,
                icon: Wrench,
                content: (
                  <div className="flex flex-wrap gap-2 pt-1">
                    {a.skills?.map(s => (
                      <span key={s} className="badge-purple">{s}</span>
                    ))}
                  </div>
                ),
              },
              {
                id: 'projects',
                title: 'Projects',
                count: a.projects?.length,
                icon: BookOpen,
                content: (
                  <div className="space-y-3 pt-1">
                    {a.projects?.map((p, i) => (
                      <div key={i} className="bg-surface-50 rounded-xl p-4 border border-surface-200">
                        <p className="font-semibold text-gray-800">{p.title}</p>
                        <p className="text-sm text-gray-500 mt-1">{p.description}</p>
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {p.technologies?.map(t => (
                            <span key={t} className="badge-blue">{t}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                    {(!a.projects || a.projects.length === 0) && (
                      <p className="text-sm text-gray-400 pt-1">No projects found</p>
                    )}
                  </div>
                ),
              },
              {
                id: 'experience',
                title: 'Experience',
                count: a.experiences?.length,
                icon: User,
                content: (
                  <div className="space-y-3 pt-1">
                    {a.experiences?.map((e, i) => (
                      <div key={i} className="bg-surface-50 rounded-xl p-4 border border-surface-200">
                        <div className="flex items-center justify-between">
                          <p className="font-semibold text-gray-800">{e.role}</p>
                          <span className="text-xs text-gray-400">{e.duration}</span>
                        </div>
                        <p className="text-sm text-brand-600 font-medium">{e.company}</p>
                        <p className="text-sm text-gray-500 mt-1">{e.description}</p>
                      </div>
                    ))}
                    {(!a.experiences || a.experiences.length === 0) && (
                      <p className="text-sm text-gray-400 pt-1">No experience found</p>
                    )}
                  </div>
                ),
              },
              {
                id: 'insights',
                title: 'Strengths & Areas to Improve',
                icon: TrendingUp,
                content: (
                  <div className="grid grid-cols-2 gap-4 pt-1">
                    <div>
                      <p className="text-xs font-semibold text-green-700 mb-2 uppercase tracking-wide">
                        Strengths
                      </p>
                      <ul className="space-y-1.5">
                        {a.strengths?.map((s, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <CheckCircle2 size={14} className="text-green-500 mt-0.5 shrink-0" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-orange-700 mb-2 uppercase tracking-wide">
                        Improve
                      </p>
                      <ul className="space-y-1.5">
                        {a.areas_of_improvement?.map((s, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                            <AlertTriangle size={14} className="text-orange-400 mt-0.5 shrink-0" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ),
              },
            ].map(({ id, title, count, icon: Icon, content }) => (
              <div key={id} className="card">
                <button
                  onClick={() => setExpanded(expanded === id ? null : id)}
                  className="flex items-center justify-between w-full"
                >
                  <span className="flex items-center gap-2 font-semibold text-gray-900">
                    <Icon size={16} className="text-brand-500" />
                    {title}
                    {count !== undefined && (
                      <span className="text-gray-400 text-sm font-normal">({count})</span>
                    )}
                  </span>
                  {expanded === id
                    ? <ChevronUp size={18} className="text-gray-400" />
                    : <ChevronDown size={18} className="text-gray-400" />}
                </button>
                <AnimatePresence>
                  {expanded === id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden mt-3"
                    >
                      {content}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}

            {/* ── Improvement CTA ─────────────────────────────────────── */}
            <div className="card bg-gradient-to-r from-brand-600 to-purple-600 text-white">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1">
                  <h3 className="font-bold text-lg flex items-center gap-2">
                    <Zap size={18} /> Get AI Improvement Suggestions
                  </h3>
                  <p className="text-purple-200 text-sm mt-1">
                    Section scores · ATS check · Quick wins · Rewritten summary
                  </p>
                  <div className="flex gap-3 mt-3">
                    <input
                      value={targetRole}
                      onChange={e => setTargetRole(e.target.value)}
                      placeholder="Target role (e.g. SDE)"
                      className="px-3 py-2 rounded-xl bg-white/15 border border-white/25 text-white placeholder:text-purple-300/70 text-sm outline-none focus:border-white/50 flex-1"
                    />
                    <input
                      value={targetCompany}
                      onChange={e => setTargetCompany(e.target.value)}
                      placeholder="Company (optional)"
                      className="px-3 py-2 rounded-xl bg-white/15 border border-white/25 text-white placeholder:text-purple-300/70 text-sm outline-none focus:border-white/50 flex-1"
                    />
                  </div>
                </div>
                <button
                  onClick={handleImprove}
                  disabled={improving}
                  className="flex items-center gap-2 bg-white text-brand-700 font-bold text-sm px-5 py-3 rounded-xl hover:bg-purple-50 active:scale-95 transition-all disabled:opacity-60 shrink-0"
                >
                  {improving
                    ? <><Spinner size="sm" /> Analysing…</>
                    : <><TrendingUp size={16} /> Analyse Resume</>}
                </button>
              </div>
            </div>

            {/* ── Improvement Results ──────────────────────────────────── */}
            <AnimatePresence>
              {improvements && (
                <motion.div
                  id="improvements-section"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  {/* Score overview */}
                  <div className="card">
                    <h3 className="section-title mb-5">Resume Score Overview</h3>
                    <div className="flex items-center gap-8 flex-wrap">
                      <ProgressRingWithValue
                        value={improvements.overall_score || 0}
                        size={110}
                        strokeWidth={9}
                        color={scoreColor(improvements.overall_score)}
                        label="Overall Score"
                      />
                      <ProgressRingWithValue
                        value={improvements.ats_score || 0}
                        size={110}
                        strokeWidth={9}
                        color={scoreColor(improvements.ats_score)}
                        label="ATS Score"
                      />
                      <div className="flex-1 min-w-[200px]">
                        <p className="text-sm text-gray-500 mb-3">Section Breakdown</p>
                        {Object.entries(improvements.sections || {}).map(([key, val]) => (
                          <div key={key} className="mb-2">
                            <div className="flex justify-between text-sm mb-0.5">
                              <span className="font-medium text-gray-700 capitalize">{key}</span>
                              <span className={clsx('font-bold', scoreColor(val.score * 10) === '#10b981' ? 'text-green-600' : scoreColor(val.score * 10) === '#f59e0b' ? 'text-yellow-600' : 'text-red-500')}>
                                {val.score}/10
                              </span>
                            </div>
                            <div className="h-1.5 bg-surface-200 rounded-full">
                              <div
                                className="h-1.5 rounded-full transition-all duration-500"
                                style={{
                                  width: `${val.score * 10}%`,
                                  background: scoreColor(val.score * 10),
                                }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Section issues & fixes */}
                  {Object.entries(improvements.sections || {}).length > 0 && (
                    <div className="card">
                      <h3 className="section-title mb-4">Section Analysis</h3>
                      <div className="space-y-3">
                        {Object.entries(improvements.sections).map(([key, val]) => (
                          <div key={key} className="flex gap-4 p-4 rounded-xl bg-surface-50 border border-surface-200">
                            <div className="shrink-0 mt-0.5">
                              <span className={clsx('badge', scoreBadge(val.score * 10))}>
                                {val.score}/10
                              </span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-semibold text-gray-800 capitalize">{key}</p>
                              <p className="text-sm text-red-600 mt-0.5 flex items-start gap-1.5">
                                <AlertTriangle size={13} className="shrink-0 mt-0.5" />
                                {val.issue}
                              </p>
                              <p className="text-sm text-green-700 mt-1 flex items-start gap-1.5">
                                <CheckCircle2 size={13} className="shrink-0 mt-0.5" />
                                {val.fix}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Quick wins */}
                  {improvements.quick_wins?.length > 0 && (
                    <div className="card">
                      <h3 className="section-title mb-4 flex items-center gap-2">
                        <Lightbulb size={18} className="text-yellow-500" />
                        Quick Wins
                      </h3>
                      <div className="space-y-2">
                        {improvements.quick_wins.map((w, i) => (
                          <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-yellow-50 border border-yellow-100">
                            <span className="w-5 h-5 rounded-full bg-yellow-400 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                              {i + 1}
                            </span>
                            <p className="text-sm text-yellow-900">{w}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Missing keywords + strong points side by side */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {improvements.missing_keywords?.length > 0 && (
                      <div className="card">
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Target size={16} className="text-red-500" />
                          Missing Keywords
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {improvements.missing_keywords.map(k => (
                            <span key={k} className="badge-red">{k}</span>
                          ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-3">
                          Add these to pass ATS screening
                        </p>
                      </div>
                    )}

                    {improvements.strong_points?.length > 0 && (
                      <div className="card">
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Star size={16} className="text-green-500" />
                          Strong Points
                        </h3>
                        <ul className="space-y-1.5">
                          {improvements.strong_points.map((p, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                              <CheckCircle2 size={14} className="text-green-500 mt-0.5 shrink-0" />
                              {p}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Rewritten summary */}
                  {improvements.rewrite_summary && (
                    <div className="card border-brand-200 bg-brand-50/40">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                          <Award size={16} className="text-brand-600" />
                          AI-Rewritten Professional Summary
                        </h3>
                        <button
                          onClick={handleCopySummary}
                          className="flex items-center gap-1.5 text-xs text-brand-600 hover:text-brand-700 font-medium border border-brand-200 px-3 py-1.5 rounded-lg hover:bg-brand-100 transition-all"
                        >
                          {copiedSummary
                            ? <><CheckCircle2 size={12} /> Copied!</>
                            : <><Copy size={12} /> Copy</>}
                        </button>
                      </div>
                      <p className="text-sm text-gray-700 leading-relaxed bg-white rounded-xl p-4 border border-brand-100">
                        {improvements.rewrite_summary}
                      </p>
                      <p className="text-xs text-gray-400 mt-2">
                        Replace your current summary with this — it is ATS-optimised and role-specific.
                      </p>
                    </div>
                  )}

                  {/* Re-analyse button */}
                  <button
                    onClick={handleImprove}
                    disabled={improving}
                    className="btn-secondary w-full justify-center"
                  >
                    <RefreshCw size={15} className={improving ? 'animate-spin' : ''} />
                    {improving ? 'Analysing…' : 'Re-analyse Resume'}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
