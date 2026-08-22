import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Generator from './pages/Generator'
import Scanner from './pages/Scanner'
import History from './pages/History'
import Categories from './pages/Categories'
import BulkGenerator from './pages/BulkGenerator'
import Analytics from './pages/Analytics'
import Export from './pages/Export'
import Backup from './pages/Backup'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/generator" element={<Generator />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/history" element={<History />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/bulk" element={<BulkGenerator />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/export" element={<Export />} />
        <Route path="/backup" element={<Backup />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}