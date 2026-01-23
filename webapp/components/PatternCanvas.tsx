'use client';

import { useRef, useState, useEffect } from 'react';
import { simplifyPattern, normalizePattern } from '@/lib/canvas-utils';
import PatternResults from './PatternResults';

interface Point {
  x: number;
  y: number;
}

interface StockMatch {
  symbol: string;
  distance: number;
  similarity_score: number;
  correlation: number | null;
  start_date: string;
  end_date: string;
  matched_prices: number[];
}

export default function PatternCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [points, setPoints] = useState<Point[]>([]);
  const [normalizedPoints, setNormalizedPoints] = useState<number[]>([]);
  const [numPoints, setNumPoints] = useState(30);  // 30 weeks (~7 months) - better for weekly timeframe
  const [matches, setMatches] = useState<StockMatch[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Draw grid
    drawGrid(ctx, canvas.width, canvas.height);
  }, []);

  const drawGrid = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.strokeStyle = '#2a2a2a';
    ctx.lineWidth = 1;

    // Vertical lines
    for (let x = 0; x <= width; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Horizontal lines
    for (let y = 0; y <= height; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  };

  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Redraw grid
    drawGrid(ctx, canvas.width, canvas.height);

    // Redraw pattern
    if (points.length > 1) {
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);

      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }

      ctx.stroke();
    }
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setPoints([{ x, y }]);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setPoints(prev => [...prev, { x, y }]);
    redrawCanvas();
  };

  const handleMouseUp = () => {
    if (!isDrawing) return;
    setIsDrawing(false);

    if (points.length > 2) {
      // Simplify and normalize the pattern
      const canvas = canvasRef.current;
      if (!canvas) return;

      const simplified = simplifyPattern(points, numPoints, canvas.height);
      const normalized = normalizePattern(simplified);

      setNormalizedPoints(normalized);
    }
  };

  // Touch event handlers for mobile support
  const handleTouchStart = (e: React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;

    setIsDrawing(true);
    setPoints([{ x, y }]);
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;

    setPoints(prev => [...prev, { x, y }]);
    redrawCanvas();
  };

  const handleTouchEnd = (e: React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    handleMouseUp();
  };

  const handleClear = () => {
    setPoints([]);
    setNormalizedPoints([]);
    setMatches([]);

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawGrid(ctx, canvas.width, canvas.height);
  };

  const handleSearch = async () => {
    if (normalizedPoints.length === 0) {
      alert('Please draw a pattern first');
      return;
    }

    setIsSearching(true);
    setMatches([]);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/pattern/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pattern: normalizedPoints,
          num_points: numPoints,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to search for patterns');
      }

      const results = await response.json();
      console.log('Pattern match results:', results);

      if (results.success && results.matches) {
        setMatches(results.matches);
      } else {
        alert(results.message || 'No matches found');
      }
    } catch (error) {
      console.error('Error searching for patterns:', error);
      alert('Error searching for patterns. Make sure the backend API is running.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-400">Points:</label>
            <input
              type="number"
              value={numPoints}
              onChange={(e) => setNumPoints(Number(e.target.value))}
              min="20"
              max="200"
              className="w-20 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            onClick={handleClear}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            Clear
          </button>

          <button
            onClick={handleSearch}
            disabled={normalizedPoints.length === 0 || isSearching}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
          >
            {isSearching ? 'Searching...' : 'Search Patterns'}
          </button>

          {normalizedPoints.length > 0 && (
            <div className="text-sm text-green-400">
              ✓ Pattern captured ({normalizedPoints.length} points)
            </div>
          )}
        </div>
      </div>

      {/* Canvas */}
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-1">Draw Your Pattern</h2>
          <p className="text-sm text-gray-400">
            Click and drag to draw a price pattern. The pattern will be simplified to {numPoints} weekly candles (~{Math.round(numPoints / 4)} months).
          </p>
        </div>

        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          className="w-full h-96 border border-gray-700 rounded-lg cursor-crosshair bg-[#111111]"
          style={{ touchAction: 'none' }}
        />
      </div>

      {/* Results */}
      <PatternResults matches={matches} isLoading={isSearching} />

      {/* Debug Info */}
      {normalizedPoints.length > 0 && matches.length === 0 && !isSearching && (
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h3 className="text-lg font-semibold mb-3">Normalized Pattern Data</h3>
          <div className="bg-gray-950 rounded p-4 overflow-x-auto">
            <pre className="text-xs text-gray-300">
              {JSON.stringify(normalizedPoints.slice(0, 10), null, 2)}
              {normalizedPoints.length > 10 && '\n... (' + (normalizedPoints.length - 10) + ' more points)'}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}