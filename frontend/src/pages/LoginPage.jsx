import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'
import { Eye, EyeOff, Zap, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const setUser = useStore((s) => s.setUser)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authAPI.login(form)
      setUser(data)
      toast.success(`Welcome back, ${data.name}!`)
      navigate('/dashboard')
    } catch {
      // error shown by interceptor
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
      {/* Decorative blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-brand-500/20 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-purple-500/20 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center shadow-glow mb-4">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">PrepCopilot</h1>
          <p className="text-purple-300 text-sm mt-1">AI-powered placement preparation</p>
        </div>

        {/* Card */}
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-purple-200 mb-1.5">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/30 text-sm transition"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-purple-200 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-4 py-3 pr-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/30 text-sm transition"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-300 hover:text-white transition"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-brand-500 to-purple-500 hover:from-brand-400 hover:to-purple-400 text-white font-bold text-sm transition-all duration-200 active:scale-95 disabled:opacity-60 mt-2 shadow-glow"
            >
              {loading ? 'Signing in…' : 'Sign in'}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <p className="text-center text-sm text-purple-300 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-white font-semibold hover:text-brand-300 transition">
              Create one
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
