'use client'

import { useEffect, useState, useRef } from 'react'
import StockTable from './StockTable'
import type { StockScore } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'

type Props = {
  initialStocks: StockScore[]
}

export default function InfiniteStockList({ initialStocks }: Props) {
  const [stocks, setStocks] = useState<StockScore[]>(initialStocks)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const observerTarget = useRef<HTMLDivElement>(null)

  const loadMore = async () => {
    if (loading || !hasMore) return

    setLoading(true)
    try {
      const latestDateRes = await supabase
        .from('stock_scores')
        .select('scan_date')
        .order('scan_date', { ascending: false })
        .limit(1)
        .single()

      if (latestDateRes.error) throw latestDateRes.error

      const { data, error } = await supabase
        .from('stock_scores')
        .select('*')
        .eq('scan_date', latestDateRes.data.scan_date)
        .order('score', { ascending: false })
        .order('passed_filter', { ascending: false })
        .range(stocks.length, stocks.length + 99)

      if (error) throw error

      if (data && data.length > 0) {
        setStocks((prev) => [...prev, ...data])
        setHasMore(data.length === 100)
      } else {
        setHasMore(false)
      }
    } catch (error) {
      console.error('Error loading more stocks:', error)
      setHasMore(false)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          loadMore()
        }
      },
      { threshold: 0.1 }
    )

    const currentTarget = observerTarget.current
    if (currentTarget) {
      observer.observe(currentTarget)
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget)
      }
    }
  }, [hasMore, loading, stocks.length])

  return (
    <div>
      <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <StockTable stocks={stocks} />
      </div>
      
      <div ref={observerTarget} className="h-20 flex items-center justify-center">
        {loading && (
          <div className="text-gray-400">Loading more stocks...</div>
        )}
        {!hasMore && stocks.length > 0 && (
          <div className="text-gray-500 text-sm">No more stocks to load</div>
        )}
      </div>
    </div>
  )
}