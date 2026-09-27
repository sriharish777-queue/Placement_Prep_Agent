import clsx from 'clsx'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function StatCard({ title, value, subtitle, icon: Icon, trend, color = 'brand', className = '' }) {
  const colorMap = {
    brand:  { bg: 'bg-brand-50',  icon: 'text-brand-600',  iconBg: 'bg-brand-100' },
    green:  { bg: 'bg-green-50',  icon: 'text-green-600',  iconBg: 'bg-green-100' },
    yellow: { bg: 'bg-yellow-50', icon: 'text-yellow-600', iconBg: 'bg-yellow-100' },
    blue:   { bg: 'bg-blue-50',   icon: 'text-blue-600',   iconBg: 'bg-blue-100' },
    red:    { bg: 'bg-red-50',    icon: 'text-red-600',    iconBg: 'bg-red-100' },
  }
  const c = colorMap[color] || colorMap.brand

  return (
    <div className={clsx('card flex items-start gap-4', className)}>
      {Icon && (
        <div className={clsx('w-11 h-11 rounded-xl flex items-center justify-center shrink-0', c.iconBg)}>
          <Icon size={20} className={c.icon} />
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-2xl font-extrabold text-gray-900 mt-0.5 leading-none">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      {trend !== undefined && (
        <div className={clsx(
          'flex items-center gap-0.5 text-xs font-semibold rounded-full px-2 py-0.5 shrink-0',
          trend > 0 ? 'text-green-600 bg-green-50' :
          trend < 0 ? 'text-red-500 bg-red-50' :
                      'text-gray-500 bg-gray-100'
        )}>
          {trend > 0 ? <TrendingUp size={12} /> : trend < 0 ? <TrendingDown size={12} /> : <Minus size={12} />}
          {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}
