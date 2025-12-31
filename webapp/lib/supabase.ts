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
  list_name: string | null
  created_at: string
}

export async function getLatestStocks(limit = 50) {
  const { data, error } = await supabase
    .from('stock_scores')
    .select('*')
    .order('scan_date', { ascending: false })
    .order('score', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data as StockScore[]
}

export async function getStocksByList(listName: string) {
  const { data, error } = await supabase
    .from('stock_scores')
    .select('*')
    .ilike('list_name', `%${listName}%`)
    .order('scan_date', { ascending: false })
    .order('score', { ascending: false })

  if (error) throw error
  return data as StockScore[]
}

export async function getAllLists() {
  const { data, error } = await supabase
    .from('stock_scores')
    .select('list_name')
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