'use client'

import Link from 'next/link'
import type { StockScore } from '@/lib/supabase'

export default function StockTable({ stocks }: { stocks: StockScore[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-700">
        <thead className="bg-gray-800">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Symbol
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Score
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Filter
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Lists
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Market Bias
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
              Fibonacci
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="bg-gray-900 divide-y divide-gray-700">
          {stocks.map((stock) => (
            <tr key={stock.id} className="hover:bg-gray-800 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-white">{stock.symbol}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-white">{stock.score}/11</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {stock.passed_filter ? (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-900 text-green-200">
                    PASS
                  </span>
                ) : (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-900 text-red-200">
                    FAIL
                  </span>
                )}
              </td>
              <td className="px-6 py-4">
                <div className="text-sm text-gray-300 max-w-xs truncate">{stock.list_name || 'N/A'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-300">
                  {stock.market_bias_score || 0} pts
                  {stock.market_bias_timeframe && (
                    <span className="text-xs text-gray-500 ml-1">({stock.market_bias_timeframe})</span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-300">
                  {stock.fibonacci_score || 0} pts
                  {stock.fibonacci_zone && (
                    <span className="text-xs text-gray-500 ml-1">({stock.fibonacci_zone})</span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link
                  href={`/stock/${stock.symbol}`}
                  className="text-blue-400 hover:text-blue-300 transition-colors"
                >
                  View Chart →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {stocks.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No stocks found
        </div>
      )}
    </div>
  )
}