import { Routes, Route, Navigate } from 'react-router-dom'
import { useStore } from './store/useStore'
import Layout from './components/layout/Layout'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ResumePage from './pages/ResumePage'
import SkillGapPage from './pages/SkillGapPage'
import PlanPage from './pages/PlanPage'
import PracticePage from './pages/PracticePage'
import MockInterviewPage from './pages/MockInterviewPage'
import PerformancePage from './pages/PerformancePage'
import AssistantPage from './pages/AssistantPage'
import ProfilePage from './pages/ProfilePage'

function PrivateRoute({ children }) {
  const user = useStore((s) => s.user)
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="skill-gap" element={<SkillGapPage />} />
        <Route path="plan" element={<PlanPage />} />
        <Route path="practice" element={<PracticePage />} />
        <Route path="interview" element={<MockInterviewPage />} />
        <Route path="performance" element={<PerformancePage />} />
        <Route path="assistant" element={<AssistantPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
