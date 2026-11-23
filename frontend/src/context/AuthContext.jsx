import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

const DEMO_USERS = {
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

  // Initialize session from storage
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem('qrm_auth_token')
      const storedUser = localStorage.getItem('qrm_user')
      if (storedToken && storedUser) {
        setUser(JSON.parse(storedUser))
      } else {
        // Default guest / enterprise session
        const defaultUser = DEMO_USERS.admin
        setUser(defaultUser)
        localStorage.setItem('qrm_user', JSON.stringify(defaultUser))
      }
    } catch {
      setUser(DEMO_USERS.admin)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      // Create authenticated demo session token
      const sessionUser = {
        id: `usr_${btoa(email).replace(/[^a-zA-Z0-9]/g, '').slice(0, 10)}`,
        email,
        role: 'admin',
        name: email.split('@')[0],
      }
      const fakeJwt = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${btoa(JSON.stringify({ sub: sessionUser.id, email, role: 'authenticated' }))}.demoSig`
      
      localStorage.setItem('qrm_auth_token', fakeJwt)
      localStorage.setItem('qrm_user', JSON.stringify(sessionUser))
      setUser(sessionUser)
      return { success: true, user: sessionUser }
    } finally {
      setLoading(false)
    }
  }, [])

  const signup = useCallback(async (email, password) => {
    return login(email, password)
  }, [login])

  const demoLogin = useCallback((roleKey = 'admin') => {
    const demoUser = DEMO_USERS[roleKey] || DEMO_USERS.admin
    const fakeJwt = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${btoa(JSON.stringify({ sub: demoUser.id, email: demoUser.email, role: 'authenticated' }))}.demoSig`
    
    localStorage.setItem('qrm_auth_token', fakeJwt)
    localStorage.setItem('qrm_user', JSON.stringify(demoUser))
    setUser(demoUser)
    return demoUser
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
