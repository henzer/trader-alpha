'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function AnalyzePage() {
  const [symbol, setSymbol] = useState('')
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault()
    if (!symbol.trim()) return
    
    setLoading(true)
    setSelectedSymbol(symbol.toUpperCase().trim())
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const chartUrl = selectedSymbol ? `${apiUrl}/chart/${selectedSymbol}` : ''

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <Link
          href="/"
          className="text-blue-400 hover:text-blue-300 transition-colors inline-flex items-center"
        >
          ← Back to Home
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">
          Analyze Stock On-Demand
        </h1>
        <p className="text-gray-400">
          Enter any stock symbol to generate a technical analysis chart in real-time
        </p>
      </div>

      <form onSubmit={handleAnalyze} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol (e.g., AAPL, TSLA, GOOGL)"
            className="flex-1 px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
            maxLength={10}
          />
          <button
            type="submit"
            disabled={!symbol.trim() || loading}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
          >
            Analyze
          </button>
        </div>
      </form>

      {selectedSymbol && (
        <div>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-white">
              {selectedSymbol}
            </h2>
            <p className="text-gray-400 text-sm">
              Loading chart from API...
            </p>
          </div>

          <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
            <iframe
              src={chartUrl}
              className="w-full h-[700px] border-0"
              title={`${selectedSymbol} Chart`}
              onLoad={() => setLoading(false)}
            />
          </div>

          <div className="mt-4 text-sm text-gray-500">
            Chart URL: <code className="text-blue-400">{chartUrl}</code>
          </div>
        </div>
      )}

      {!selectedSymbol && (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-white mb-2">
            No stock selected
          </h3>
          <p className="text-gray-400">
            Enter a stock symbol above to generate a technical analysis chart
          </p>
        </div>
      )}
    </div>
  )
}