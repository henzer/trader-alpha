import { getStockDetails } from '@/lib/supabase'
import LocalTime from '@/components/LocalTime'
import Link from 'next/link'
import { notFound } from 'next/navigation'

export const revalidate = 300

export default async function StockDetailPage({
  params,
}: {
  params: { symbol: string }
}) {
  const { symbol } = params

  let stock
  try {
    stock = await getStockDetails(symbol)
  } catch (error) {
    notFound()
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const chartUrl = `${apiUrl}/chart/${symbol.toUpperCase()}`

  const lists = stock.list_name?.split(',').map((l) => l.trim()) || []

  return (
    <div>
      {/* Back Button */}
      <div className="mb-4">
        <Link
          href="/lists"
          className="text-blue-400 hover:text-blue-300 transition-colors inline-flex items-center"
        >
          ← Back to Lists
        </Link>
      </div>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          {stock.symbol}
        </h1>
        <div className="flex items-center gap-4">
          <div className="text-2xl font-semibold">
            Score: {stock.score}/11
          </div>
          {stock.passed_filter ? (
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-green-900 text-green-200">
              ✓ PASS
            </span>
          ) : (
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-red-900 text-red-200">
              ✗ FAIL
            </span>
          )}
        </div>
        <div className="mt-2 flex gap-2">
          {lists.map((list) => (
            <Link
              key={list}
              href={`/lists/${list}`}
              className="px-2 py-1 text-xs rounded bg-gray-700 text-gray-200 hover:bg-gray-600"
            >
              {list}
            </Link>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden mb-8">
        <iframe
          src={chartUrl}
          className="w-full h-[600px] border-0"
          title={`${stock.symbol} Chart`}
        />
      </div>

      {/* Analysis Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">📊 Market Bias</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Score:</span>
              <span className="text-white font-semibold">{stock.market_bias_score || 0} pts</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Timeframe:</span>
              <span className="text-white">{stock.market_bias_timeframe || 'N/A'}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">🎯 Fibonacci Retracement</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Score:</span>
              <span className="text-white font-semibold">{stock.fibonacci_score || 0} pts</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Zone:</span>
              <span className="text-white">{stock.fibonacci_zone || 'N/A'}</span>
            </div>
            {stock.swing_high && stock.swing_low && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-400">Swing High:</span>
                  <span className="text-white">${stock.swing_high.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Swing Low:</span>
                  <span className="text-white">${stock.swing_low.toFixed(2)}</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* BX-Trender */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">📈 BX-Trender</h2>
        <div className="flex items-center gap-4">
          <span className="text-gray-400">Monthly Trend:</span>
          <span className={`px-3 py-1 rounded-full font-semibold ${
            stock.bx_color === 'LIME' ? 'bg-green-900 text-green-200' :
            stock.bx_color === 'DARK_GREEN' ? 'bg-green-800 text-green-300' :
            stock.bx_color === 'RED' ? 'bg-red-800 text-red-300' :
            stock.bx_color === 'DARK_RED' ? 'bg-red-900 text-red-200' :
            'bg-gray-700 text-gray-300'
          }`}>
            {stock.bx_color || 'N/A'}
          </span>
        </div>
      </div>

      {/* Metadata */}
      <div className="mt-8 text-sm text-gray-500">
        Last updated: <LocalTime date={stock.created_at} />
      </div>
    </div>
  )
}
