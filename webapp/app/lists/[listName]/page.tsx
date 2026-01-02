import { getStocksByList, getAllLists } from '@/lib/supabase'
import StockTable from '@/components/StockTable'
import LocalTime from '@/components/LocalTime'
import Link from 'next/link'
import { notFound } from 'next/navigation'

export const revalidate = 300

export async function generateStaticParams() {
  const lists = await getAllLists()
  return lists.map((list) => ({
    listName: list,
  }))
}

export default async function ListDetailPage({
  params,
}: {
  params: { listName: string }
}) {
  const { listName } = params
  const stocks = await getStocksByList(listName)

  if (stocks.length === 0) {
    notFound()
  }

  return (
    <div>
      {/* Back Button */}
      <div className="mb-4">
        <Link
          href="/lists"
          className="text-blue-400 hover:text-blue-300 transition-colors inline-flex items-center"
        >
          ← Back to All Lists
        </Link>
      </div>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          {listName} Stocks
        </h1>
        <p className="text-gray-400">
          {stocks.length} stocks • Last scan: {stocks[0]?.created_at ? <LocalTime date={stocks[0].created_at} /> : 'N/A'}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Total in {listName}</div>
          <div className="text-3xl font-bold text-white mt-2">{stocks.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Passed Filter</div>
          <div className="text-3xl font-bold text-green-400 mt-2">
            {stocks.filter((s) => s.passed_filter).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="text-gray-400 text-sm">Avg Score</div>
          <div className="text-3xl font-bold text-blue-400 mt-2">
            {(stocks.reduce((acc, s) => acc + s.score, 0) / stocks.length).toFixed(1)}
          </div>
        </div>
      </div>

      {/* Stock Table */}
      <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <StockTable stocks={stocks} />
      </div>
    </div>
  )
}
