import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import { useStore } from '../../store/useStore'
import { motion, AnimatePresence } from 'framer-motion'

export default function Layout() {
  const sidebarOpen = useStore((s) => s.sidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-surface-50">
      <Sidebar />

      <div
        className="flex flex-col flex-1 min-w-0 transition-all duration-300"
        style={{ marginLeft: sidebarOpen ? '256px' : '72px' }}
      >
        <Topbar />
        <main className="flex-1 overflow-y-auto px-6 py-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={window.location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
