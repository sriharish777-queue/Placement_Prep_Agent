import { useState, useRef, useEffect } from 'react'
import { useStore } from '../store/useStore'
import { ragAPI } from '../api/client'
import Spinner from '../components/ui/Spinner'
import { Send, Bot, User, BookOpen, Zap, Database } from 'lucide-react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import clsx from 'clsx'
import toast from 'react-hot-toast'

const SUGGESTED_QUERIES = [
  'How do I approach DSA problems in interviews?',
  'Explain the difference between process and thread',
  'What are SOLID principles with examples?',
  'How do SQL JOINs work?',
  'What is the STAR method for behavioral interviews?',
  'Explain system design for a URL shortener',
  'Common Java 8 interview questions',
  'How to prepare for aptitude tests?',
]

export default function AssistantPage() {
  const { user, skillGap } = useStore()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm your AI placement preparation assistant powered by a RAG knowledge base. I can answer questions about DSA, system design, CS fundamentals, behavioral interviews, company-specific prep, and more.

What would you like to learn today?`,
      sources: [],
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [seeding, setSeeding] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendQuery = async (query) => {
    if (!query.trim()) return
    const q = query.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', content: q }])
    setLoading(true)
    try {
      const { data } = await ragAPI.query({
        query: q,
        user_id: user?.user_id || user?.id,
        company: skillGap?.target_company || undefined,
        user_context: skillGap ? {
          target_role: skillGap.target_role,
          weak_skills: skillGap.weak_skills,
        } : undefined,
      })
      setMessages(m => [...m, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        context_used: data.context_used,
      }])
    } catch {
      // handled
    } finally {
      setLoading(false)
    }
  }

  const handleSeed = async () => {
    setSeeding(true)
    try {
      const { data } = await ragAPI.seed()
      toast.success(`Knowledge base seeded with ${data.count} documents!`)
    } catch {
      // handled
    } finally {
      setSeeding(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendQuery(input)
    }
  }

  return (
    <div className="max-w-3xl flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      {/* Header */}
      <div className="card mb-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center shadow-glow">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">AI Career Assistant</p>
            <p className="text-xs text-gray-400">RAG-powered • Context-aware • Placement focused</p>
          </div>
        </div>
        <button onClick={handleSeed} disabled={seeding}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-brand-600 transition px-3 py-1.5 rounded-lg border border-surface-200 hover:border-brand-200">
          {seeding ? <Spinner size="sm" /> : <Database size={13} />}
          Seed Knowledge Base
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-3 pr-1">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx('flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : 'flex-row')}
          >
            <div className={clsx(
              'w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1',
              msg.role === 'assistant' ? 'bg-gradient-to-br from-brand-500 to-purple-500' : 'bg-gray-100'
            )}>
              {msg.role === 'assistant'
                ? <Bot size={15} className="text-white" />
                : <User size={15} className="text-gray-600" />
              }
            </div>

            <div className={clsx('max-w-[85%] space-y-2', msg.role === 'user' && 'items-end flex flex-col')}>
              <div className={clsx(
                'px-4 py-3 rounded-2xl text-sm leading-relaxed',
                msg.role === 'assistant'
                  ? 'bg-white border border-surface-200 rounded-tl-sm'
                  : 'bg-brand-600 text-white rounded-tr-sm'
              )}>
                {msg.role === 'assistant' ? (
                  <ReactMarkdown className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-code:bg-surface-100 prose-code:px-1 prose-code:rounded">
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>

              {/* Sources */}
              {msg.sources?.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <BookOpen size={11} className="text-gray-400" />
                  {msg.sources.slice(0, 3).map((s, si) => (
                    <span key={si} className="text-xs text-gray-400 bg-surface-100 px-2 py-0.5 rounded-full border border-surface-200">
                      {s.source || s.category || 'Knowledge Base'}
                    </span>
                  ))}
                  {msg.context_used > 0 && (
                    <span className="text-xs text-gray-300">{msg.context_used} sources used</span>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center">
              <Bot size={15} className="text-white" />
            </div>
            <div className="bg-white border border-surface-200 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1.5 items-center">
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 rounded-full bg-brand-300 animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
                <span className="text-xs text-gray-400 ml-1">Searching knowledge base…</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested queries */}
      {messages.length <= 2 && !loading && (
        <div className="shrink-0 mb-3">
          <p className="text-xs text-gray-400 mb-2 flex items-center gap-1">
            <Zap size={11} /> Suggested questions
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUERIES.slice(0, 4).map(q => (
              <button key={q} onClick={() => sendQuery(q)}
                className="text-xs px-3 py-1.5 rounded-full border border-surface-300 text-gray-600 hover:border-brand-300 hover:text-brand-700 hover:bg-brand-50 transition-all">
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="shrink-0 flex gap-2">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          className="input resize-none flex-1 text-sm"
          placeholder="Ask anything about placement prep… (Enter to send)"
          disabled={loading}
        />
        <button onClick={() => sendQuery(input)} disabled={loading || !input.trim()}
          className="btn-primary px-4 self-end">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
