import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BsCodeSlash,
  BsKey,
  BsPlusLg,
  BsTrash,
  BsCopy,
  BsBoxArrowUpRight,
  BsShieldCheck,
  BsTerminal,
} from 'react-icons/bs'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiKeyAPI } from '../services/api'

const CODE_EXAMPLES = {
  curl: `curl -X POST "https://qr-generator-2-8sv7.onrender.com/api/v1/qr/generate" \\
  -H "X-API-Key: qrm_live_YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "qr_type": "url",
    "content": "https://brand.com/promo",
    "title": "Summer Campaign",
    "size": 400
  }'`,
  python: `import httpx

client = httpx.Client(
    base_url="https://qr-generator-2-8sv7.onrender.com/api/v1",
    headers={"X-API-Key": "qrm_live_YOUR_API_KEY"}
)

response = client.post("/dynamic", json={
    "title": "Spring Festival QR",
    "target_url": "https://brand.com/event",
    "ios_target_url": "https://apps.apple.com/app/id123",
    "android_target_url": "https://play.google.com/store/apps/details?id=com.brand"
})

print("Dynamic Redirect URL:", response.json()["redirect_url"])`,
  javascript: `const axios = require('axios');

const qrmaster = axios.create({
  baseURL: 'https://qr-generator-2-8sv7.onrender.com/api/v1',
  headers: { 'X-API-Key': 'qrm_live_YOUR_API_KEY' }
});

async function createDynamicQR() {
  const { data } = await qrmaster.post('/dynamic', {
    title: 'Store Window Display',
    target_url: 'https://brand.com/sale',
    max_scans: 1000
  });
  console.log('Short Link:', data.redirect_url);
}

createDynamicQR();`,
}

export default function DeveloperDocs() {
  const queryClient = useQueryClient()
  const [activeLang, setActiveLang] = useState('curl')
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyScopes, setNewKeyScopes] = useState('qr:read,qr:write,analytics:read')
  const [generatedKey, setGeneratedKey] = useState(null)
  const [copiedKey, setCopiedKey] = useState(false)

  const { data: apiKeys } = useQuery({
    queryKey: ['developer-api-keys'],
    queryFn: () => apiKeyAPI.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data) => apiKeyAPI.create(data),
    onSuccess: (res) => {
      setGeneratedKey(res.data)
      setNewKeyName('')
      queryClient.invalidateQueries({ queryKey: ['developer-api-keys'] })
    },
    onError: (err) => alert(err.message || 'Failed to create API key'),
  })

  const revokeMutation = useMutation({
    mutationFn: (id) => apiKeyAPI.revoke(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['developer-api-keys'] }),
    onError: (err) => alert(err.message || 'Failed to revoke API key'),
  })

  const handleCreate = (e) => {
    e.preventDefault()
    if (!newKeyName.trim()) return
    createMutation.mutate({
      name: newKeyName.trim(),
      rate_limit: 1000,
      scopes: newKeyScopes,
    })
  }

  const copyCode = (text) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 2000)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsCodeSlash className="text-indigo-600 dark:text-indigo-400" />
            Developer Platform & REST APIs
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Build with QRMaster Pro programmatically via OpenAPI 3.1 REST APIs, scoped authentication keys, and webhooks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary text-xs flex items-center gap-1.5 px-3 py-2"
          >
            <BsTerminal />
            <span>Interactive Swagger UI</span>
            <BsBoxArrowUpRight className="text-[10px]" />
          </a>
          <a
            href="http://127.0.0.1:8000/redoc"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary text-xs flex items-center gap-1.5 px-3 py-2"
          >
            <span>ReDoc Specs</span>
            <BsBoxArrowUpRight className="text-[10px]" />
          </a>
        </div>
      </div>

      {/* Code Snippets & Quickstart */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 text-white space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveLang('curl')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                activeLang === 'curl' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              cURL
            </button>
            <button
              onClick={() => setActiveLang('python')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                activeLang === 'python' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Python
            </button>
            <button
              onClick={() => setActiveLang('javascript')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                activeLang === 'javascript' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Node.js
            </button>
          </div>

          <button
            onClick={() => copyCode(CODE_EXAMPLES[activeLang])}
            className="text-xs text-slate-400 hover:text-indigo-400 flex items-center gap-1.5 transition-colors"
          >
            <BsCopy />
            <span>{copiedKey ? 'Copied!' : 'Copy Code'}</span>
          </button>
        </div>

        <pre className="overflow-x-auto text-xs font-mono text-slate-300 py-2 leading-relaxed select-all">
          <code>{CODE_EXAMPLES[activeLang]}</code>
        </pre>
      </div>

      {/* Scopes & Permission Matrix */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <BsShieldCheck className="text-indigo-600 dark:text-indigo-400" />
          API Permission Scopes
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">qr:read</span>
            <p className="text-gray-500 mt-1">Read-only access to QR history, templates, and categories.</p>
          </div>
          <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">qr:write</span>
            <p className="text-gray-500 mt-1">Generate static & dynamic QR codes and update target destinations.</p>
          </div>
          <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">analytics:read</span>
            <p className="text-gray-500 mt-1">Access real-time scan event logs, hourly metrics, and visitor devices.</p>
          </div>
          <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">admin</span>
            <p className="text-gray-500 mt-1">Full root access to all tenant workspaces, webhooks, and domains.</p>
          </div>
        </div>
      </div>

      {/* API Keys Management */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 space-y-6">
        <div>
          <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsKey className="text-indigo-600 dark:text-indigo-400" />
            Developer API Keys
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Authenticate requests by passing the secret key in the <code className="font-mono">X-API-Key</code> request header.
          </p>
        </div>

        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Key Name (e.g. Backend Microservice, POS Gateway)"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            className="input-field text-sm"
            required
          />
          <select
            value={newKeyScopes}
            onChange={(e) => setNewKeyScopes(e.target.value)}
            className="input-field text-sm"
          >
            <option value="qr:read,qr:write,analytics:read">Standard (qr:read, qr:write, analytics:read)</option>
            <option value="qr:read,analytics:read">Read-Only (qr:read, analytics:read)</option>
            <option value="qr:write">Write-Only (qr:write)</option>
            <option value="admin">Admin (Full Permissions)</option>
          </select>
          <button type="submit" disabled={createMutation.isPending} className="btn-primary flex items-center justify-center gap-2 text-sm">
            <BsPlusLg />
            <span>Generate New Key</span>
          </button>
        </form>

        {generatedKey && (
          <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200 text-xs space-y-2">
            <p className="font-bold">🔑 New API Key Generated:</p>
            <div className="flex items-center gap-2 bg-white dark:bg-gray-900 p-2.5 rounded-lg border border-amber-200 dark:border-amber-800 font-mono">
              <span className="flex-1 select-all">{generatedKey.api_key}</span>
              <button
                onClick={() => copyCode(generatedKey.api_key)}
                className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
              >
                Copy
              </button>
            </div>
            <p className="text-[11px] text-amber-700 dark:text-amber-400 font-medium">
              {generatedKey.warning}
            </p>
          </div>
        )}

        <div className="space-y-2">
          {apiKeys?.map((k) => (
            <div
              key={k.id}
              className="flex items-center justify-between p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-750"
            >
              <div>
                <p className="font-semibold text-sm text-gray-900 dark:text-white">{k.name}</p>
                <p className="text-xs text-gray-400 font-mono mt-0.5">
                  Prefix: <code className="text-indigo-600 dark:text-indigo-400">{k.key_prefix}...</code> • Scopes: [{k.scopes || 'all'}]
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400">
                  Created {k.created_at ? k.created_at.split('T')[0] : ''}
                </span>
                <button
                  onClick={() => {
                    if (confirm(`Revoke API key '${k.name}'?`)) revokeMutation.mutate(k.id)
                  }}
                  className="text-red-500 hover:text-red-700 p-1.5 rounded"
                  title="Revoke Key"
                >
                  <BsTrash />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
