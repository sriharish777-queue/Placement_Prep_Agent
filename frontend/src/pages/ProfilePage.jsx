import { useState } from 'react'
import { useStore } from '../store/useStore'
import { authAPI } from '../api/client'
import toast from 'react-hot-toast'
import Spinner from '../components/ui/Spinner'
import { User, Save, Mail, Briefcase, Building2, BarChart3 } from 'lucide-react'

const EXP_LEVELS = ['fresher', 'junior', 'mid', 'senior']

export default function ProfilePage() {
  const { user, setUser } = useStore()
  const [form, setForm] = useState({
    name: user?.name || '',
    target_role: user?.target_role || '',
    target_company: user?.target_company || '',
    experience_level: user?.experience_level || 'fresher',
  })
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      const { data } = await authAPI.updateProfile(user?.user_id || user?.id, form)
      setUser({ ...user, ...form })
      toast.success('Profile updated!')
    } catch {
      // handled
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">Manage your account and placement preferences</p>
      </div>

      {/* Avatar */}
      <div className="card flex items-center gap-5">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-white text-3xl font-extrabold shadow-glow">
          {user?.name?.[0]?.toUpperCase() || 'U'}
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">{user?.name}</h3>
          <p className="text-sm text-gray-500 flex items-center gap-1.5 mt-1">
            <Mail size={13} /> {user?.email}
          </p>
          <p className="text-xs text-gray-400 mt-1 capitalize">
            {user?.experience_level} • {user?.target_role || 'No target role set'}
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card space-y-5">
        <h3 className="font-semibold text-gray-900">Personal Information</h3>

        <div>
          <label className="label flex items-center gap-1.5"><User size={14} /> Full Name</label>
          <input className="input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
        </div>

        <div>
          <label className="label flex items-center gap-1.5"><Briefcase size={14} /> Target Role</label>
          <input className="input" value={form.target_role}
            onChange={e => setForm({ ...form, target_role: e.target.value })}
            placeholder="Software Developer, Data Engineer…" />
        </div>

        <div>
          <label className="label flex items-center gap-1.5"><Building2 size={14} /> Target Company</label>
          <input className="input" value={form.target_company}
            onChange={e => setForm({ ...form, target_company: e.target.value })}
            placeholder="Google, TCS, Infosys…" />
        </div>

        <div>
          <label className="label flex items-center gap-1.5"><BarChart3 size={14} /> Experience Level</label>
          <div className="flex gap-2">
            {EXP_LEVELS.map(l => (
              <button key={l} onClick={() => setForm({ ...form, experience_level: l })}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium border capitalize transition-all
                  ${form.experience_level === l
                    ? 'bg-brand-600 text-white border-brand-600'
                    : 'bg-white text-gray-600 border-surface-300 hover:border-brand-300'
                  }`}>
                {l}
              </button>
            ))}
          </div>
        </div>

        <button onClick={handleSave} disabled={saving} className="btn-primary">
          {saving ? <><Spinner size="sm" /> Saving…</> : <><Save size={15} /> Save Changes</>}
        </button>
      </div>

      {/* Account info */}
      <div className="card space-y-3">
        <h3 className="font-semibold text-gray-900">Account Info</h3>
        <div className="space-y-2">
          {[
            { label: 'User ID', value: user?.user_id || user?.id },
            { label: 'Email', value: user?.email },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between py-2 border-b border-surface-100 last:border-0">
              <span className="text-sm text-gray-500">{label}</span>
              <span className="text-sm font-medium text-gray-800 font-mono">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
