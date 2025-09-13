import { Routes, Route } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { Automation } from './pages/Automation'
import { Layout } from './components/Layout'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/automation" element={<Automation />} />
      </Routes>
    </Layout>
  )
}

export default App
