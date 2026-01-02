import { getAllLists, getLatestStocks } from '@/lib/supabase'
import StockTable from '@/components/StockTable'
import LocalTime from '@/components/LocalTime'
import Link from 'next/link'

export const revalidate = 300 // Revalidate every 5 minutes

export default async function ListsPage() {
  const [lists, stocks] = await Promise.all([
    getAllLists(),
    getLatestStocks(100)
  ])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Stock Lists</h1>
        <p className="text-gray-400">
          Last scan: {stocks[0]?.created_at ? <LocalTime date={stocks[0].created_at} /> : 'N/A'}
        </p>
      </div>

      {/* List Tags */}
      <div className="mb-6 flex flex-wrap gap-2">
        <Link
          href="/lists"
          className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          All Lists ({stocks.length})
        </Link>
        {lists.map((list) => {
          const count = stocks.filter((s) => s.list_name?.includes(list)).length
          return (
            <Link
              key={list}
              href={`/lists/${list}`}
              className="px-4 py-2 rounded-lg bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
            >
              {list} ({count})
            </Link>
          )
        })}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Total Stocks</div>
          <div className="text-3xl font-bold text-white mt-2">{stocks.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Passed Filter</div>
          <div className="text-3xl font-bold text-green-400 mt-2">
            {stocks.filter((s) => s.passed_filter).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">High Score (&gt;8)</div>
          <div className="text-3xl font-bold text-yellow-400 mt-2">
            {stocks.filter((s) => s.score >= 8).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Total Lists</div>
          <div className="text-3xl font-bold text-blue-400 mt-2">{lists.length}</div>
        </div>
      </div>

      {/* Stock Table */}
      <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <StockTable stocks={stocks} />
      </div>
    </div>
  )
}
