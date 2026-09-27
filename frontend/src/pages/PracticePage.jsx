import { useState, useEffect, useRef } from 'react'
import { useStore } from '../store/useStore'
import { questionsAPI, performanceAPI } from '../api/client'
import toast from 'react-hot-toast'
import Spinner from '../components/ui/Spinner'
import { Code2, ChevronRight, CheckCircle2, XCircle, Lightbulb, Clock, RotateCcw, Send } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import ReactMarkdown from 'react-markdown'

const CATEGORIES = ['DSA', 'SQL', 'Java', 'Python', 'OOP', 'DBMS', 'OS', 'CN', 'Aptitude', 'System Design', 'Spring Boot', 'REST API']
const DIFFICULTIES = ['easy', 'medium', 'hard']

export default function PracticePage() {
  const { user } = useStore()
  const [config, setConfig] = useState({ category: 'DSA', difficulty: 'medium', count: 3 })
  const [questions, setQuestions] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [sessionId] = useState(() => Date.now().toString())
  const [answers, setAnswers] = useState([])
  const [sessionDone, setSessionDone] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null)
  const timerRef = useRef(null)
  const startTimeRef = useRef(null)

  const current = questions[currentIdx]

  const startTimer = (seconds) => {
    setTimeLeft(seconds)
    startTimeRef.current = Date.now()
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) { clearInterval(timerRef.current); return 0 }
        return t - 1
      })
    }, 1000)
  }

  const stopTimer = () => {
    clearInterval(timerRef.current)
    return Math.floor((Date.now() - (startTimeRef.current || Date.now())) / 1000)
  }

  const generateQuestions = async () => {
    setLoading(true)
    setQuestions([])
    setCurrentIdx(0)
    setEvaluation(null)
    setUserAnswer('')
    setAnswers([])
    setSessionDone(false)
    try {
      const payload = {
        ...config,
        user_id: user?.user_id || user?.id || 'guest',
      }
      const { data } = await questionsAPI.generate(payload)
      setQuestions(data.questions || [])
      if (data.questions?.length > 0) {
        startTimer(data.questions[0].time_limit_seconds || 300)
      }
    } catch {
      // handled
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!userAnswer.trim()) { toast.error('Please write an answer'); return }
    const timeTaken = stopTimer()
    setSubmitting(true)
    try {
      const { data } = await questionsAPI.attempt({
        user_id: user?.user_id || user?.id,
        question_id: current.id || '',
        session_id: sessionId,
        user_answer: userAnswer,
        time_taken_seconds: timeTaken,
      })
      setEvaluation(data)
      setAnswers(prev => [...prev, { question: current, answer: userAnswer, evaluation: data, time: timeTaken }])
    } catch {
      // handled
    } finally {
      setSubmitting(false)
    }
  }

  const nextQuestion = async () => {
    const next = currentIdx + 1
    if (next >= questions.length) {
      // Session complete — log performance
      const ev = (a) => a.evaluation?.evaluation || a.evaluation || {}
      const correct = answers.filter(a => ev(a).is_correct).length
      const score = questions.length > 0 ? (correct / questions.length) * 100 : 0
      await performanceAPI.logSession({
        user_id: user?.user_id || user?.id || 'guest',
        session_id: sessionId,
        session_type: 'practice',
        topics_covered: [config.category],
        questions_attempted: questions.length,
        questions_correct: correct,
        score,
        duration_minutes: Math.max(1, Math.ceil(answers.reduce((s, a) => s + (a.time || 0), 0) / 60)),
      }).catch(() => {})
      setSessionDone(true)
    } else {
      setCurrentIdx(next)
      setUserAnswer('')
      setEvaluation(null)
      setShowHint(false)
      startTimer(questions[next].time_limit_seconds || 300)
    }
  }

  const score = evaluation?.evaluation?.score || 0

  return (
    <div className="max-w-3xl space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Practice</h1>
        <p className="page-subtitle">AI-generated questions with instant evaluation</p>
      </div>

      {/* Config */}
      {questions.length === 0 && !loading && !sessionDone && (
        <div className="card space-y-5">
          <h3 className="font-semibold text-gray-900">Configure Practice Session</h3>

          <div>
            <label className="label">Category</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map(c => (
                <button
                  key={c}
                  onClick={() => setConfig({ ...config, category: c })}
                  className={clsx(
                    'px-3 py-1.5 rounded-xl text-sm font-medium border transition-all',
                    config.category === c
                      ? 'bg-brand-600 text-white border-brand-600 shadow-glow'
                      : 'bg-white text-gray-600 border-surface-300 hover:border-brand-300'
                  )}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Difficulty</label>
              <div className="flex gap-2">
                {DIFFICULTIES.map(d => (
                  <button key={d} onClick={() => setConfig({ ...config, difficulty: d })}
                    className={clsx(
                      'flex-1 py-2 rounded-xl text-sm font-medium border capitalize transition-all',
                      config.difficulty === d
                        ? d === 'easy' ? 'bg-green-600 text-white border-green-600'
                          : d === 'medium' ? 'bg-yellow-500 text-white border-yellow-500'
                          : 'bg-red-500 text-white border-red-500'
                        : 'bg-white text-gray-600 border-surface-300 hover:border-brand-300'
                    )}>
                    {d}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="label">Questions</label>
              <select className="input" value={config.count} onChange={e => setConfig({ ...config, count: +e.target.value })}>
                {[3, 5, 10].map(n => <option key={n} value={n}>{n} questions</option>)}
              </select>
            </div>
          </div>

          <button onClick={generateQuestions} className="btn-primary w-full justify-center py-3">
            <Code2 size={17} /> Start Practice Session
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center gap-3 py-20">
          <Spinner size="xl" />
          <p className="text-gray-600 font-medium">Generating {config.count} {config.difficulty} {config.category} questions…</p>
          <p className="text-sm text-gray-400">This takes 20–40 seconds on the free AI tier. Please wait.</p>
          <div className="flex gap-1 mt-2">
            {[0,1,2].map(i => (
              <div key={i} className="w-2 h-2 rounded-full bg-brand-300 animate-bounce" style={{animationDelay:`${i*0.2}s`}} />
            ))}
          </div>
        </div>
      )}

      {/* Session done */}
      {sessionDone && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="card text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <CheckCircle2 size={36} className="text-green-500" />
          </div>
          <h3 className="text-xl font-bold text-gray-900">Session Complete!</h3>
          <p className="text-gray-500">
            {answers.filter(a => (a.evaluation?.evaluation || a.evaluation || {}).is_correct).length}/{questions.length} correct answers
          </p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => { setQuestions([]); setSessionDone(false) }} className="btn-secondary">
              <RotateCcw size={15} /> New Session
            </button>
            <button onClick={generateQuestions} className="btn-primary">
              <RotateCcw size={15} /> Same Config
            </button>
          </div>
        </motion.div>
      )}

      {/* Question card */}
      {current && !sessionDone && (
        <motion.div key={currentIdx} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
          {/* Progress */}
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Question {currentIdx + 1} of {questions.length}</span>
            <div className="flex items-center gap-1.5">
              <Clock size={14} />
              <span className={clsx('font-mono font-bold', timeLeft !== null && timeLeft < 30 ? 'text-red-500' : 'text-gray-700')}>
                {timeLeft !== null ? `${Math.floor(timeLeft / 60)}:${String(timeLeft % 60).padStart(2, '0')}` : '—'}
              </span>
            </div>
          </div>
          <div className="flex gap-1.5">
            {questions.map((_, i) => (
              <div key={i} className={clsx('flex-1 h-1.5 rounded-full transition-colors',
                i < currentIdx ? 'bg-green-400' : i === currentIdx ? 'bg-brand-500' : 'bg-surface-200')} />
            ))}
          </div>

          {/* Question */}
          <div className="card">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="badge-purple">{current.category}</span>
                <span className={clsx(
                  current.difficulty === 'easy' ? 'badge-green' :
                  current.difficulty === 'hard' ? 'badge-red' : 'badge-yellow'
                )}>{current.difficulty}</span>
                <span className="badge-gray capitalize">{current.question_type}</span>
              </div>
            </div>

            <div className="prose prose-sm max-w-none text-gray-800 mb-5">
              <ReactMarkdown>{current.question_text}</ReactMarkdown>
            </div>

            {/* MCQ options */}
            {current.question_type === 'mcq' && current.options && (
              <div className="space-y-2 mb-4">
                {current.options.map((opt, i) => (
                  <button key={i} onClick={() => setUserAnswer(opt)}
                    className={clsx(
                      'w-full text-left p-3 rounded-xl border text-sm transition-all',
                      userAnswer === opt
                        ? 'border-brand-400 bg-brand-50 text-brand-800 font-medium'
                        : 'border-surface-200 hover:border-brand-200 hover:bg-surface-50'
                    )}>
                    {opt}
                  </button>
                ))}
              </div>
            )}

            {/* Text answer */}
            {current.question_type !== 'mcq' && (
              <textarea
                value={userAnswer}
                onChange={e => setUserAnswer(e.target.value)}
                disabled={!!evaluation}
                rows={5}
                className="input resize-none font-mono text-sm mb-4"
                placeholder={current.question_type === 'coding' ? '// Write your solution here...' : 'Write your answer here…'}
              />
            )}

            {/* Hint */}
            {current.hints?.length > 0 && !evaluation && (
              <button onClick={() => setShowHint(!showHint)} className="flex items-center gap-1.5 text-sm text-yellow-600 mb-3 hover:text-yellow-700">
                <Lightbulb size={14} /> {showHint ? 'Hide hint' : 'Show hint'}
              </button>
            )}
            {showHint && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-sm text-yellow-800 mb-3">
                {current.hints?.[0]}
              </div>
            )}

            {!evaluation ? (
              <button onClick={submitAnswer} disabled={submitting || !userAnswer.trim()} className="btn-primary w-full justify-center">
                {submitting ? <><Spinner size="sm" /> Evaluating…</> : <><Send size={15} /> Submit Answer</>}
              </button>
            ) : (
              <EvaluationPanel evaluation={evaluation} question={current} onNext={nextQuestion}
                isLast={currentIdx === questions.length - 1} />
            )}
          </div>
        </motion.div>
      )}
    </div>
  )
}

function EvaluationPanel({ evaluation, question, onNext, isLast }) {
  // API returns evaluation at top level: { evaluation: {...}, correct_answer, explanation }
  // Support both shapes: evaluation.evaluation (old) and evaluation directly
  const ev = evaluation?.evaluation || evaluation || {}
  const isCorrect = ev.is_correct
  const score = Number(ev.score) || 0

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-2 space-y-3">
      {/* Score banner */}
      <div className={clsx(
        'flex items-center gap-3 p-4 rounded-xl border',
        isCorrect ? 'bg-green-50 border-green-200' : score >= 5 ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200'
      )}>
        {isCorrect ? <CheckCircle2 className="text-green-500 shrink-0" /> : <XCircle className="text-red-500 shrink-0" />}
        <div className="flex-1">
          <p className={clsx('font-semibold', isCorrect ? 'text-green-800' : 'text-red-800')}>
            {isCorrect ? 'Correct!' : 'Needs improvement'}
          </p>
          <p className="text-xs text-gray-500">Score: {score}/10</p>
        </div>
        <div className="text-2xl font-extrabold">{score}/10</div>
      </div>

      {/* Feedback */}
      {ev.detailed_feedback && (
        <div className="bg-surface-50 rounded-xl p-4 border border-surface-200 text-sm text-gray-700 space-y-2">
          <p className="font-medium text-gray-800">AI Feedback</p>
          <p>{ev.detailed_feedback}</p>
        </div>
      )}

      {/* Correct answer */}
      {question.correct_answer && (
        <div className="bg-green-50 rounded-xl p-4 border border-green-100 text-sm">
          <p className="font-semibold text-green-800 mb-1">Correct Answer</p>
          <p className="text-green-700">{question.correct_answer}</p>
          {question.explanation && <p className="text-green-600 mt-2 text-xs">{question.explanation}</p>}
        </div>
      )}

      {ev.missing_concepts?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <p className="w-full text-xs font-medium text-gray-500">Missing concepts:</p>
          {ev.missing_concepts.map(c => <span key={c} className="badge-red">{c}</span>)}
        </div>
      )}

      <button onClick={onNext} className="btn-primary w-full justify-center">
        {isLast ? 'Finish Session' : 'Next Question'} <ChevronRight size={16} />
      </button>
    </motion.div>
  )
}
