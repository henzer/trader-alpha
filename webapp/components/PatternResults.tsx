'use client';

import Link from 'next/link';

interface StockMatch {
  symbol: string;
  distance: number;
  similarity_score: number;
  correlation: number | null;
  start_date: string;
  end_date: string;
  matched_prices: number[];
}

interface PatternResultsProps {
  matches: StockMatch[];
  isLoading?: boolean;
}

export default function PatternResults({ matches, isLoading = false }: PatternResultsProps) {
  if (isLoading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <span className="ml-4 text-gray-400">Searching for matching patterns...</span>
        </div>
      </div>
    );
  }

  if (matches.length === 0) {
    return null;
  }

  // Calculate price change percentage and date info for each match
  const getMatchStats = (match: StockMatch) => {
    const startPrice = match.matched_prices[0];
    const endPrice = match.matched_prices[match.matched_prices.length - 1];
    const priceChange = endPrice - startPrice;
    const priceChangePercent = (priceChange / startPrice) * 100;
    const minPrice = Math.min(...match.matched_prices);
    const maxPrice = Math.max(...match.matched_prices);

    // Calculate pattern duration and recency
    const endDate = new Date(match.end_date);
    const startDate = new Date(match.start_date);
    const today = new Date();

    const calendarDays = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    const tradingDays = match.matched_prices.length;  // Window size (trading days)
    const daysAgo = Math.round((today.getTime() - endDate.getTime()) / (1000 * 60 * 60 * 24));

    // Weekly timeframe: only patterns ending in last week are "recent"
    // Daily timeframe: patterns ending in last 3 days are "recent"
    const isRecent = daysAgo <= 7;  // ~1 week for weekly data

    return {
      startPrice,
      endPrice,
      priceChange,
      priceChangePercent,
      minPrice,
      maxPrice,
      calendarDays,
      tradingDays,
      daysAgo,
      isRecent,
    };
  };

  // Calculate overall stats
  const allStats = matches.map(match => getMatchStats(match));
  const recentCount = allStats.filter(s => s.isRecent).length;
  const avgDaysAgo = allStats.reduce((sum, s) => sum + s.daysAgo, 0) / allStats.length;
  const avgWindowSize = allStats.reduce((sum, s) => sum + s.tradingDays, 0) / allStats.length;

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Pattern Matches</h2>
        <p className="text-gray-400 mb-4">
          Found {matches.length} stocks with similar patterns
        </p>

        {/* Verification Summary */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-500 mb-1">Recent Patterns (≤3 days old)</div>
              <div className="text-xl font-bold">
                <span className={recentCount === matches.length ? 'text-green-400' : 'text-orange-400'}>
                  {recentCount} / {matches.length}
                </span>
                {recentCount === matches.length && (
                  <span className="ml-2 text-sm text-green-400">✓ All recent!</span>
                )}
              </div>
            </div>
            <div>
              <div className="text-gray-500 mb-1">Avg Pattern Age</div>
              <div className="text-xl font-bold text-white">
                {avgDaysAgo.toFixed(1)} days ago
              </div>
            </div>
            <div>
              <div className="text-gray-500 mb-1">Avg Window Size</div>
              <div className="text-xl font-bold text-white">
                {avgWindowSize.toFixed(0)} trading days
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {matches.map((match, index) => {
          const stats = getMatchStats(match);
          const isPositive = stats.priceChangePercent >= 0;

          return (
            <div
              key={`${match.symbol}-${index}`}
              className="bg-gray-800 rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg text-white font-bold">
                    #{index + 1}
                  </div>
                  <div>
                    <Link
                      href={`/stock/${match.symbol}`}
                      className="text-2xl font-bold text-white hover:text-blue-400 transition-colors"
                    >
                      {match.symbol}
                    </Link>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="text-sm text-gray-400">
                        {match.start_date} to {match.end_date}
                      </div>
                      {stats.isRecent ? (
                        <span className="px-2 py-0.5 bg-green-600 text-white text-xs font-semibold rounded">
                          RECENT ({stats.daysAgo === 0 ? 'Today' : `${stats.daysAgo}d ago`})
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-orange-600 text-white text-xs font-semibold rounded">
                          {stats.daysAgo}d ago
                        </span>
                      )}
                      <span className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs font-semibold rounded">
                        {stats.calendarDays} days
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm text-gray-400 mb-1">Similarity</div>
                  <div className="text-2xl font-bold text-blue-400">
                    {(match.similarity_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-900 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Window Size</div>
                  <div className="text-lg font-semibold text-blue-400">
                    {stats.tradingDays} trading days
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Calendar Duration</div>
                  <div className="text-lg font-semibold text-white">
                    {stats.calendarDays} days
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">DTW Distance</div>
                  <div className="text-lg font-semibold text-white">
                    {match.distance.toFixed(2)}
                  </div>
                </div>

                {match.correlation !== null && (
                  <div className="bg-gray-900 rounded-lg p-3">
                    <div className="text-xs text-gray-500 mb-1">Correlation</div>
                    <div className="text-lg font-semibold text-white">
                      {match.correlation.toFixed(3)}
                    </div>
                  </div>
                )}
              </div>

              {/* Secondary Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-900 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Price Range</div>
                  <div className="text-lg font-semibold text-white">
                    ${stats.minPrice.toFixed(2)} - ${stats.maxPrice.toFixed(2)}
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Pattern Move</div>
                  <div
                    className={`text-lg font-semibold ${
                      isPositive ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {isPositive ? '+' : ''}
                    {stats.priceChangePercent.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Mini Price Chart */}
              <div className="bg-gray-950 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-2">Matched Price Pattern</div>
                <div className="relative h-20">
                  <svg
                    className="w-full h-full"
                    viewBox={`0 0 ${match.matched_prices.length} 100`}
                    preserveAspectRatio="none"
                  >
                    {/* Price line */}
                    <polyline
                      points={match.matched_prices
                        .map((price, i) => {
                          // Normalize prices to 0-100 range for SVG
                          const normalizedPrice =
                            ((price - stats.minPrice) / (stats.maxPrice - stats.minPrice)) * 80 +
                            10;
                          return `${i},${100 - normalizedPrice}`;
                        })
                        .join(' ')}
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="0.5"
                      vectorEffect="non-scaling-stroke"
                    />
                  </svg>
                </div>
                <div className="flex justify-between text-xs text-gray-600 mt-2">
                  <span>${stats.startPrice.toFixed(2)}</span>
                  <span>${stats.endPrice.toFixed(2)}</span>
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-4">
                <Link
                  href={`/stock/${match.symbol}`}
                  className="block w-full text-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                >
                  View Full Chart
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}