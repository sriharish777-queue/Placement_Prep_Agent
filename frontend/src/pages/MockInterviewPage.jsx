import { useState, useRef, useEffect } from 'react'
import { useStore } from '../store/useStore'
import { interviewAPI } from '../api/client'
import toast from 'react-hot-toast'
import Spinner from '../components/ui/Spinner'
import { Mic, Send, Square, User, Bot, Star, ChevronRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import ReactMarkdown from 'react-markdown'

const INTERVIEW_TYPES = [
  { value: 'technical',     label: 'Technical',      emoji: '💻', desc: 'DSA, CS fundamentals, language-specific' },
  { value: 'hr',            label: 'HR',             emoji: '🤝', desc: 'Background, motivation, culture fit' },
  { value: 'behavioral',    label: 'Behavioral',     emoji: '🧠', desc: 'STAR method, past experiences' },
  { value: 'system_design', label: 'System Design',  emoji: '🏗️', desc: 'Architecture, scalability' },
  { value: 'mixed',         label: 'Mixed',          emoji: '🎯', desc: 'Comprehensive placement round' },
]

export default function MockInterviewPage() {
  const { user } = useStore()
  const [config, setConfig] = useState({
    interview_type: 'technical',
    target_role: user?.target_role || 'Software Developer',
    target_company: user?.target_company || '',
  })
  const [interview, setInterview] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [ended, setEnded] = useState(false)
  const [evaluation, setEvaluation] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startInterview = async () => {
    setLoading(true)
    try {
      const { data } = await interviewAPI.start({
        user_id: user?.user_id || user?.id,
        ...config,
        target_company: config.target_company || undefined,
      })
      setInterview(data)
      setMessages([{ role: 'interviewer', content: data.opening_message }])
    } catch {
      // handled
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || sending) return
    const msg = input.trim()
    setInput('')
    setMessages(m => [...m, { role: 'candidate', content: msg }])
    setSending(true)
    try {
      const { data } = await interviewAPI.message({
        interview_id: interview.interview_id,
        user_id: user?.user_id || user?.id,
        message: msg,
      })
      setMessages(m => [...m, {
        role: 'interviewer',
        content: data.interviewer_message,
        evaluation: data.answer_evaluation,
      }])
    } catch {
      // handled
    } finally {
      setSending(false)
    }
  }

  const endInterview = async () => {
    setSending(true)
    try {
      const { data } = await interviewAPI.end(interview.interview_id)
      setEvaluation(data.evaluation)
      setEnded(true)
    } catch {
      // handled
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const resetInterview = () => {
    setInterview(null)
    setMessages([])
    setEnded(false)
    setEvaluation(null)
  }

  if (!interview) {
    return (
      <div className="max-w-3xl space-y-6 animate-fade-in">
        <div className="page-header">
          <h1 className="page-title">Mock Interview</h1>
          <p className="page-subtitle">Practice with an AI interviewer that adapts to your answers in real time</p>
        </div>

        <div className="card space-y-5">
          <h3 className="font-semibold text-gray-900">Configure your interview</h3>

          <div>
            <label className="label">Interview Type</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {INTERVIEW_TYPES.map(t => (
                <button
                  key={t.value}
                  onClick={() => setConfig({ ...config, interview_type: t.value })}
                  className={clsx(
                    'flex items-center gap-3 p-4 rounded-2xl border-2 text-left transition-all',
                    config.interview_type === t.value
                      ? 'border-brand-400 bg-brand-50'
                      : 'border-surface-200 hover:border-brand-200 hover:bg-surface-50'
                  )}
                >
                  <span className="text-2xl">{t.emoji}</span>
                  <div>
                    <p className="font-semibold text-gray-800 text-sm">{t.label}</p>
                    <p className="text-xs text-gray-400">{t.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Target Role</label>
              <input className="input" value={config.target_role}
                onChange={e => setConfig({ ...config, target_role: e.target.value })}
                placeholder="Software Developer" />
            </div>
            <div>
              <label className="label">Company (optional)</label>
              <input className="input" value={config.target_company}
                onChange={e => setConfig({ ...config, target_company: e.target.value })}
                placeholder="Google, TCS, Infosys…" />
            </div>
          </div>

          <button onClick={startInterview} disabled={loading} className="btn-primary w-full justify-center py-3">
            {loading ? <><Spinner size="sm" /> Starting interview…</> : <><Mic size={17} /> Start Interview</>}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      {/* Header */}
      <div className="card mb-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-100 flex items-center justify-center">
            <Bot size={18} className="text-brand-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800">
              {INTERVIEW_TYPES.find(t => t.value === config.interview_type)?.label} Interview
            </p>
            <p className="text-xs text-gray-400">{config.target_role}{config.target_company ? ` • ${config.target_company}` : ''}</p>
          </div>
        </div>
        {!ended && (
          <button onClick={endInterview} disabled={sending}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-50 text-red-600 text-sm font-medium border border-red-200 hover:bg-red-100 transition">
            <Square size={13} /> End & Evaluate
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx('flex gap-3', msg.role === 'candidate' ? 'flex-row-reverse' : 'flex-row')}
          >
            <div className={clsx(
              'w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1',
              msg.role === 'interviewer' ? 'bg-brand-100' : 'bg-gray-100'
            )}>
              {msg.role === 'interviewer' ? <Bot size={16} className="text-brand-600" /> : <User size={16} className="text-gray-600" />}
            </div>
            <div className={clsx('max-w-[80%] space-y-1', msg.role === 'candidate' && 'items-end flex flex-col')}>
              <div className={clsx(
                'px-4 py-3 rounded-2xl text-sm',
                msg.role === 'interviewer'
                  ? 'bg-white border border-surface-200 text-gray-800 rounded-tl-sm'
                  : 'bg-brand-600 text-white rounded-tr-sm'
              )}>
                <ReactMarkdown className="prose prose-sm max-w-none">{msg.content}</ReactMarkdown>
              </div>
              {msg.evaluation?.score !== undefined && (
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <Star size={11} className="text-yellow-400" />
                  Score: {msg.evaluation.score}/10
                  {msg.evaluation.feedback && <span className="ml-1 text-gray-400">— {msg.evaluation.feedback}</span>}
                </div>
              )}
            </div>
          </motion.div>
        ))}
        {sending && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center">
              <Bot size={16} className="text-brand-600" />
            </div>
            <div className="bg-white border border-surface-200 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-2 h-2 rounded-full bg-brand-300 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Evaluation results */}
      {ended && evaluation && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          className="card mb-3 shrink-0">
          <h3 className="font-bold text-gray-900 mb-4">Interview Evaluation</h3>
          <div className="grid grid-cols-5 gap-3 mb-4">
            {[
              { key: 'correctness', label: 'Accuracy' },
              { key: 'technical_depth', label: 'Depth' },
              { key: 'communication', label: 'Communication' },
              { key: 'confidence', label: 'Confidence' },
              { key: 'overall_score', label: 'Overall' },
            ].map(({ key, label }) => (
              <div key={key} className="text-center bg-surface-50 rounded-xl p-3 border border-surface-200">
                <p className="text-xl font-extrabold text-gray-900">{evaluation[key]?.toFixed(1)}</p>
                <p className="text-xs text-gray-400 mt-0.5">{label}</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-700 bg-surface-50 rounded-xl p-4 border border-surface-200">
            {evaluation.feedback}
          </p>
          {evaluation.improvements?.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-gray-500 mb-2">Areas to Improve</p>
              <div className="flex flex-wrap gap-1.5">
                {evaluation.improvements.map(i => <span key={i} className="badge-red">{i}</span>)}
              </div>
            </div>
          )}
          <button onClick={resetInterview} className="btn-secondary w-full justify-center mt-4">
            Start New Interview
          </button>
        </motion.div>
      )}

      {/* Input */}
      {!ended && (
        <div className="shrink-0 flex gap-2">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            className="input resize-none flex-1 text-sm"
            placeholder="Type your answer… (Enter to send, Shift+Enter for new line)"
            disabled={sending}
          />
          <button onClick={sendMessage} disabled={sending || !input.trim()}
            className="btn-primary px-4 self-end">
            <Send size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
