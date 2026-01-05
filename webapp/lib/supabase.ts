import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type StockScore = {
  id: number
  symbol: string
  scan_date: string
  score: number
  passed_filter: boolean
  market_bias_score: number | null
  market_bias_timeframe: string | null
  fibonacci_score: number | null
  fibonacci_zone: string | null
  bx_color: string | null
  swing_high: number | null
  swing_low: number | null
  current_price: number | null
  list_name: string | null
  created_at: string
}

export function calculateRiskReward(stock: StockScore): string | null {
  if (!stock.current_price || !stock.swing_high || !stock.swing_low) {
    return null
  }

  const reward = stock.swing_high - stock.current_price
  const risk = stock.current_price - stock.swing_low

  if (risk <= 0) return null

  const ratio = reward / risk
  return ratio.toFixed(2)
}

export async function getLatestScanDate() {
  const { data, error } = await supabase
    .from('stock_scores')
    .select('scan_date')
    .order('scan_date', { ascending: false })
    .limit(1)
    .single()

  if (error) throw error
  return data?.scan_date || null
}

export async function getLatestStocks(limit = 50, offset = 0) {
  const latestDate = await getLatestScanDate()
  if (!latestDate) return []

  const { data, error } = await supabase
    .from('stock_scores')
    .select('*')
    .eq('scan_date', latestDate)
    .order('score', { ascending: false })
    .order('passed_filter', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) throw error
  return data as StockScore[]
}

export async function getTotalStocksCount() {
  const latestDate = await getLatestScanDate()
  if (!latestDate) return 0

  const { count, error } = await supabase
    .from('stock_scores')
    .select('*', { count: 'exact', head: true })
    .eq('scan_date', latestDate)

  if (error) throw error
  return count || 0
}

export async function getStocksByList(listName: string) {
  const latestDate = await getLatestScanDate()
  if (!latestDate) return []

  const { data, error } = await supabase
    .from('stock_scores')
    .select('*')
    .eq('scan_date', latestDate)
    .ilike('list_name', `%${listName}%`)
    .order('score', { ascending: false })
    .order('passed_filter', { ascending: false })

  if (error) throw error
  return data as StockScore[]
}

export async function getAllLists() {
  const latestDate = await getLatestScanDate()
  if (!latestDate) return []

  const { data, error } = await supabase
    .from('stock_scores')
    .select('list_name')
    .eq('scan_date', latestDate)
    .not('list_name', 'is', null)

  if (error) throw error

  const listsSet = new Set<string>()
  data.forEach((row) => {
    if (row.list_name) {
      row.list_name.split(',').forEach((list: string) => {
        listsSet.add(list.trim())
      })
    }
  })

  return Array.from(listsSet).sort()
}

export async function getStockDetails(symbol: string) {
  const { data, error } = await supabase
    .from('stock_scores')
    .select('*')
    .eq('symbol', symbol.toUpperCase())
    .order('scan_date', { ascending: false })
    .limit(1)
    .single()

  if (error) throw error
  return data as StockScore
}