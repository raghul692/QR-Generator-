import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BsBuilding,
  BsPlusLg,
  BsPeople,
  BsShieldCheck,
  BsCheck2Circle,
  BsTrash,
  BsPencilSquare,
  BsX,
} from 'react-icons/bs'
import { workspaceAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const ROLE_COLORS = {
  owner: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800',
  admin: 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300 border-blue-200 dark:border-blue-800',
  editor: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
  viewer: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600',
}

export default function Workspaces() {
  const { currentWorkspace, switchWorkspace } = useAuth()
  const [workspaces, setWorkspaces] = useState([])
  const [selectedWs, setSelectedWs] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newWsName, setNewWsName] = useState('')
  const [newWsPlan, setNewWsPlan] = useState('enterprise')

  const [showAddMemberModal, setShowAddMemberModal] = useState(false)
  const [memberUserId, setMemberUserId] = useState('')
  const [memberEmail, setMemberEmail] = useState('')
  const [memberRole, setMemberRole] = useState('editor')

  const fetchWorkspaces = async () => {
    try {
      setLoading(true)
      const res = await workspaceAPI.list()
      const list = res.data.workspaces || []
      setWorkspaces(list)
      const active = list.find((w) => w.id === currentWorkspace) || list[0]
      if (active) {
        setSelectedWs(active)
        loadMembers(active.id)
      }
    } catch (err) {
      setError(err.message || 'Failed to load workspaces')
    } finally {
      setLoading(false)
    }
  }

  const loadMembers = async (wsId) => {
    try {
      const res = await workspaceAPI.listMembers(wsId)
      setMembers(res.data.members || [])
    } catch (err) {
      console.error('Failed to load members:', err)
    }
  }

  useEffect(() => {
    fetchWorkspaces()
  }, [])

  const handleSelectWorkspace = (ws) => {
    setSelectedWs(ws)
    switchWorkspace(ws.id)
    loadMembers(ws.id)
  }

  const handleCreateWorkspace = async (e) => {
    e.preventDefault()
    if (!newWsName.trim()) return
    try {
      await workspaceAPI.create({ name: newWsName.trim(), plan: newWsPlan })
      setNewWsName('')
      setShowCreateModal(false)
      fetchWorkspaces()
    } catch (err) {
      alert(err.message || 'Failed to create workspace')
    }
  }

  const handleAddMember = async (e) => {
    e.preventDefault()
    if (!memberUserId.trim()) return
    try {
      await workspaceAPI.addMember(selectedWs.id, {
        user_id: memberUserId.trim(),
        email: memberEmail.trim() || undefined,
        role: memberRole,
      })
      setMemberUserId('')
      setMemberEmail('')
      setShowAddMemberModal(false)
      loadMembers(selectedWs.id)
    } catch (err) {
      alert(err.message || 'Failed to add member')
    }
  }

  const handleRemoveMember = async (userId) => {
    if (!confirm(`Are you sure you want to remove member ${userId}?`)) return
    try {
      await workspaceAPI.removeMember(selectedWs.id, userId)
      loadMembers(selectedWs.id)
    } catch (err) {
      alert(err.message || 'Failed to remove member')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsBuilding className="text-indigo-600 dark:text-indigo-400" />
            Team Workspaces & RBAC
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Manage multi-tenant enterprise organizations, membership rosters, and role permissions.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2 text-sm self-start sm:self-auto"
        >
          <BsPlusLg />
          <span>New Workspace</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Main Grid: Workspaces list on left, Details on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workspace Selector List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 space-y-3">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2">
            Available Workspaces ({workspaces.length})
          </h2>
          <div className="space-y-2">
            {workspaces.map((ws) => {
              const isSelected = selectedWs?.id === ws.id
              const isDefault = ws.id === 'ws_legacy_default'
              return (
                <button
                  key={ws.id}
                  onClick={() => handleSelectWorkspace(ws)}
                  className={`w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 dark:border-indigo-500'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
                  }`}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-sm text-gray-900 dark:text-white truncate">
                        {ws.name}
                      </p>
                      {isDefault && (
                        <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                          Legacy
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5 font-mono">
                      {ws.id}
                    </p>
                  </div>
                  {isSelected && (
                    <BsCheck2Circle className="text-indigo-600 dark:text-indigo-400 text-lg flex-shrink-0" />
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Selected Workspace Overview & Members */}
        <div className="lg:col-span-2 space-y-6">
          {selectedWs && (
            <>
              {/* Workspace Details Card */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      {selectedWs.name}
                    </h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Tenant Slug: <span className="font-mono text-indigo-600 dark:text-indigo-400">/{selectedWs.slug}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300">
                      {selectedWs.plan.toUpperCase()} PLAN
                    </span>
                    <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/60 dark:text-indigo-300">
                      Role: {selectedWs.role?.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4">
                  <div>
                    <p className="text-xs text-gray-400">Tenant ID</p>
                    <p className="text-xs font-mono font-medium text-gray-900 dark:text-gray-200 mt-0.5 truncate">
                      {selectedWs.id}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Owner User</p>
                    <p className="text-xs font-mono font-medium text-gray-900 dark:text-gray-200 mt-0.5 truncate">
                      {selectedWs.owner_id}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Team Size</p>
                    <p className="text-xs font-medium text-gray-900 dark:text-gray-200 mt-0.5">
                      {members.length} member{members.length === 1 ? '' : 's'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Isolation Status</p>
                    <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400 mt-0.5 flex items-center gap-1">
                      <BsShieldCheck /> RLS Protected
                    </p>
                  </div>
                </div>
              </div>

              {/* Members Roster Card */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <BsPeople className="text-indigo-600 dark:text-indigo-400" />
                    Member Roster & Roles
                  </h3>
                  <button
                    onClick={() => setShowAddMemberModal(true)}
                    className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-indigo-600 text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 transition-colors"
                  >
                    + Add Member
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700 text-xs text-gray-400 uppercase">
                        <th className="py-2.5 px-3">Member ID</th>
                        <th className="py-2.5 px-3">Email</th>
                        <th className="py-2.5 px-3">Role</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60">
                      {members.map((m) => (
                        <tr key={m.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/30">
                          <td className="py-3 px-3 font-mono text-xs text-gray-900 dark:text-white">
                            {m.user_id}
                          </td>
                          <td className="py-3 px-3 text-xs text-gray-600 dark:text-gray-300">
                            {m.email || '—'}
                          </td>
                          <td className="py-3 px-3">
                            <span
                              className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                                ROLE_COLORS[m.role?.toLowerCase()] || ROLE_COLORS.viewer
                              }`}
                            >
                              {m.role.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right">
                            {m.role !== 'owner' && (
                              <button
                                onClick={() => handleRemoveMember(m.user_id)}
                                className="text-red-500 hover:text-red-700 dark:hover:text-red-400 p-1 rounded"
                                title="Remove member"
                              >
                                <BsTrash className="text-sm" />
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modal: Create Workspace */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-700 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create New Workspace</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">
                <BsX className="text-2xl" />
              </button>
            </div>
            <form onSubmit={handleCreateWorkspace} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Workspace Name
                </label>
                <input
                  type="text"
                  value={newWsName}
                  onChange={(e) => setNewWsName(e.target.value)}
                  placeholder="e.g. Acme Marketing, APAC Division"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Subscription Tier
                </label>
                <select
                  value={newWsPlan}
                  onChange={(e) => setNewWsPlan(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="enterprise">Enterprise (Unlimited Dynamic QRs & RLS)</option>
                  <option value="pro">Pro (1,000 QRs & Team Members)</option>
                  <option value="standard">Standard</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-sm px-4 py-2">
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Member */}
      {showAddMemberModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-700 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Add Team Member</h3>
              <button onClick={() => setShowAddMemberModal(false)} className="text-gray-400 hover:text-gray-600">
                <BsX className="text-2xl" />
              </button>
            </div>
            <form onSubmit={handleAddMember} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  User ID
                </label>
                <input
                  type="text"
                  value={memberUserId}
                  onChange={(e) => setMemberUserId(e.target.value)}
                  placeholder="e.g. usr_user123 or Supabase Auth UID"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email (Optional)
                </label>
                <input
                  type="email"
                  value={memberEmail}
                  onChange={(e) => setMemberEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Role
                </label>
                <select
                  value={memberRole}
                  onChange={(e) => setMemberRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="admin">Admin (Manage settings, members & all QRs)</option>
                  <option value="editor">Editor (Create and edit QR codes & templates)</option>
                  <option value="viewer">Viewer (Read-only access to analytics & logs)</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddMemberModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-sm px-4 py-2">
                  Add Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
