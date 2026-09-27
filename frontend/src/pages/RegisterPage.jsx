import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'
import { Zap, ArrowRight, Eye, EyeOff } from 'lucide-react'
import { motion } from 'framer-motion'

const EXPERIENCE_LEVELS = ['fresher', 'junior', 'mid', 'senior']

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '', email: '', password: '',
    target_role: '', target_company: '', experience_level: 'fresher',
  })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const setUser = useStore((s) => s.setUser)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authAPI.register({
        name: form.name,
        email: form.email,
        password: form.password,
      })
      const { data } = await authAPI.login({ email: form.email, password: form.password })
      // Update profile with extra fields
      await authAPI.updateProfile(data.user_id, {
        target_role: form.target_role || undefined,
        target_company: form.target_company || undefined,
        experience_level: form.experience_level,
      })
      setUser({ ...data, target_role: form.target_role, target_company: form.target_company })
      toast.success('Account created! Let\'s get started.')
      navigate('/resume')
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false)
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
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
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center shadow-glow mb-4">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">PrepCopilot</h1>
          <p className="text-purple-300 text-sm mt-1">Start your placement journey</p>
        </div>

        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-6">Create your account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { key: 'name', label: 'Full Name', type: 'text', placeholder: 'Arjun Sharma' },
              { key: 'email', label: 'Email', type: 'email', placeholder: 'arjun@example.com' },
            ].map(({ key, label, type, placeholder }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-purple-200 mb-1.5">{label}</label>
                <input
                  type={type} value={form[key]} onChange={set(key)} required
                  placeholder={placeholder}
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/30 text-sm transition"
                />
              </div>
            ))}

            <div>
              <label className="block text-sm font-medium text-purple-200 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'} value={form.password} onChange={set('password')} required
                  placeholder="Min 8 characters"
                  className="w-full px-4 py-3 pr-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-400/30 text-sm transition"
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-300 hover:text-white transition">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-purple-200 mb-1.5">Target Role</label>
                <input type="text" value={form.target_role} onChange={set('target_role')}
                  placeholder="Software Developer"
                  className="w-full px-3 py-2.5 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 text-sm transition" />
              </div>
              <div>
                <label className="block text-sm font-medium text-purple-200 mb-1.5">Target Company</label>
                <input type="text" value={form.target_company} onChange={set('target_company')}
                  placeholder="Optional"
                  className="w-full px-3 py-2.5 rounded-xl bg-white/10 border border-white/20 text-white placeholder:text-purple-300/60 outline-none focus:border-brand-400 text-sm transition" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-purple-200 mb-1.5">Experience Level</label>
              <select value={form.experience_level} onChange={set('experience_level')}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white outline-none focus:border-brand-400 text-sm transition">
                {EXPERIENCE_LEVELS.map(l => (
                  <option key={l} value={l} className="bg-brand-900 capitalize">{l.charAt(0).toUpperCase() + l.slice(1)}</option>
                ))}
              </select>
            </div>

            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-brand-500 to-purple-500 hover:from-brand-400 hover:to-purple-400 text-white font-bold text-sm transition-all duration-200 active:scale-95 disabled:opacity-60 mt-2 shadow-glow">
              {loading ? 'Creating account…' : 'Get Started'}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <p className="text-center text-sm text-purple-300 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-white font-semibold hover:text-brand-300 transition">Sign in</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
