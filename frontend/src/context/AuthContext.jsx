import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

const DEMO_FALLBACK_USERS = {
  admin: {
    id: 'usr_enterprise_admin',
    email: 'admin@enterprise.qrmaster.pro',
    role: 'owner',
    name: 'Enterprise Admin',
  },
  marketing: {
    id: 'usr_marketing_lead',
    email: 'marketing@enterprise.qrmaster.pro',
    role: 'editor',
    name: 'Marketing Lead',
  },
  auditor: {
    id: 'usr_security_auditor',
    email: 'compliance@enterprise.qrmaster.pro',
    role: 'viewer',
    name: 'Security Auditor',
  },
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [currentWorkspace, setCurrentWorkspace] = useState(() => {
    return localStorage.getItem('qrm_current_workspace') || 'ws_legacy_default'
  })
  const [workspaces, setWorkspaces] = useState([])
  const [loading, setLoading] = useState(true)

  // Initialize session from storage / backend verification
  useEffect(() => {
    let isMounted = true
    const initSession = async () => {
      try {
        const storedToken = localStorage.getItem('qrm_auth_token')
        const storedUser = localStorage.getItem('qrm_user')
        if (storedToken && storedUser) {
          setUser(JSON.parse(storedUser))
          // Refresh session details from backend
          try {
            const res = await authAPI.getMe()
            if (isMounted && res.data) {
              if (res.data.user) {
                setUser((prev) => ({ ...prev, ...res.data.user }))
                localStorage.setItem('qrm_user', JSON.stringify({ ...JSON.parse(storedUser), ...res.data.user }))
              }
              if (res.data.workspaces) {
                setWorkspaces(res.data.workspaces)
              }
              if (res.data.current_workspace?.id) {
                setCurrentWorkspace(res.data.current_workspace.id)
                localStorage.setItem('qrm_current_workspace', res.data.current_workspace.id)
              }
            }
          } catch {
            // Keep local session intact if offline or backend cold starting
          }
        } else {
          // Default guest enterprise session
          const defaultUser = DEMO_FALLBACK_USERS.admin
          setUser(defaultUser)
          localStorage.setItem('qrm_user', JSON.stringify(defaultUser))
        }
      } catch {
        setUser(DEMO_FALLBACK_USERS.admin)
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    initSession()
    return () => { isMounted = false }
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      const res = await authAPI.login({ email, password })
      const { token, user: loggedInUser, workspace } = res.data
      localStorage.setItem('qrm_auth_token', token)
      localStorage.setItem('qrm_user', JSON.stringify(loggedInUser))
      if (workspace?.id) {
        localStorage.setItem('qrm_current_workspace', workspace.id)
        setCurrentWorkspace(workspace.id)
      }
      setUser(loggedInUser)
      return { success: true, user: loggedInUser, workspace }
    } catch (err) {
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const signup = useCallback(async (email, password, name) => {
    setLoading(true)
    try {
      const res = await authAPI.register({ email, password, name })
      const { token, user: newUser, workspace } = res.data
      localStorage.setItem('qrm_auth_token', token)
      localStorage.setItem('qrm_user', JSON.stringify(newUser))
      if (workspace?.id) {
        localStorage.setItem('qrm_current_workspace', workspace.id)
        setCurrentWorkspace(workspace.id)
      }
      setUser(newUser)
      return { success: true, user: newUser, workspace }
    } catch (err) {
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const demoLogin = useCallback(async (roleKey = 'admin') => {
    setLoading(true)
    try {
      const res = await authAPI.demoLogin(roleKey)
      const { token, user: demoUser, workspace } = res.data
      localStorage.setItem('qrm_auth_token', token)
      localStorage.setItem('qrm_user', JSON.stringify(demoUser))
      if (workspace?.id) {
        localStorage.setItem('qrm_current_workspace', workspace.id)
        setCurrentWorkspace(workspace.id)
      }
      setUser(demoUser)
      return demoUser
    } catch {
      // Fallback if backend is running offline
      const fallback = DEMO_FALLBACK_USERS[roleKey] || DEMO_FALLBACK_USERS.admin
      setUser(fallback)
      localStorage.setItem('qrm_user', JSON.stringify(fallback))
      return fallback
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('qrm_auth_token')
    localStorage.removeItem('qrm_user')
    setUser(null)
  }, [])

  const switchWorkspace = useCallback((wsId) => {
    localStorage.setItem('qrm_current_workspace', wsId)
    setCurrentWorkspace(wsId)
  }, [])

  const value = {
    user,
    currentWorkspace,
    workspaces,
    setWorkspaces,
    loading,
    login,
    signup,
    demoLogin,
    logout,
    switchWorkspace,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
