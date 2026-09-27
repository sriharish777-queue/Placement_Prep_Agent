import clsx from 'clsx'

export default function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-9 h-9', xl: 'w-12 h-12' }
  return (
    <div
      className={clsx(
        'rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin',
        sizes[size],
        className
      )}
    />
  )
}

export function FullPageSpinner() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-3 text-gray-400 py-24">
      <Spinner size="lg" />
      <p className="text-sm">Loading…</p>
    </div>
  )
}
