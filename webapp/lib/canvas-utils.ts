interface Point {
  x: number;
  y: number;
}

/**
 * Simplifies a drawn pattern to exactly N points using linear interpolation.
 * Extracts only Y values (normalized to 0-1 range based on canvas height).
 *
 * @param points - Array of {x, y} points from the canvas drawing
 * @param numPoints - Target number of points (e.g., 50)
 * @param canvasHeight - Height of the canvas for normalization
 * @returns Array of normalized Y values (0-1 range, inverted so higher values = higher prices)
 */
export function simplifyPattern(
  points: Point[],
  numPoints: number,
  canvasHeight: number
): number[] {
  if (points.length === 0) return [];
  if (points.length === 1) return [1 - points[0].y / canvasHeight];

  // Find the min and max X coordinates to establish the range
  const minX = Math.min(...points.map(p => p.x));
  const maxX = Math.max(...points.map(p => p.x));
  const xRange = maxX - minX;

  if (xRange === 0) {
    // All points have the same X, just return the first Y value
    return [1 - points[0].y / canvasHeight];
  }

  // Create evenly spaced X positions across the drawn range
  const targetXPositions: number[] = [];
  for (let i = 0; i < numPoints; i++) {
    const ratio = i / (numPoints - 1);
    targetXPositions.push(minX + ratio * xRange);
  }

  // Interpolate Y values for each target X position
  const simplifiedYValues: number[] = [];

  for (const targetX of targetXPositions) {
    // Find the two points that bracket this X position
    let leftPoint = points[0];
    let rightPoint = points[points.length - 1];

    for (let i = 0; i < points.length - 1; i++) {
      if (points[i].x <= targetX && points[i + 1].x >= targetX) {
        leftPoint = points[i];
        rightPoint = points[i + 1];
        break;
      }
    }

    // Linear interpolation
    let y: number;
    if (leftPoint.x === rightPoint.x) {
      y = leftPoint.y;
    } else {
      const ratio = (targetX - leftPoint.x) / (rightPoint.x - leftPoint.x);
      y = leftPoint.y + ratio * (rightPoint.y - leftPoint.y);
    }

    // Normalize to 0-1 range and invert (so lower Y on canvas = lower value)
    // Invert: canvas Y increases downward, but we want higher prices to be higher values
    const normalizedY = 1 - (y / canvasHeight);
    simplifiedYValues.push(normalizedY);
  }

  return simplifiedYValues;
}

/**
 * Applies Z-Score normalization to the pattern.
 * Formula: z = (x - μ) / σ
 *
 * This allows comparing patterns based on their shape rather than absolute values.
 *
 * @param values - Array of Y values to normalize
 * @returns Array of Z-score normalized values
 */
export function normalizePattern(values: number[]): number[] {
  if (values.length === 0) return [];
  if (values.length === 1) return [0];

  // Calculate mean (μ)
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;

  // Calculate standard deviation (σ)
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);

  // Handle case where all values are the same (stdDev = 0)
  if (stdDev === 0) {
    return values.map(() => 0);
  }

  // Apply Z-score normalization
  return values.map(val => (val - mean) / stdDev);
}

/**
 * Calculates basic statistics for a pattern.
 * Useful for debugging and validation.
 */
export function getPatternStats(values: number[]): {
  mean: number;
  stdDev: number;
  min: number;
  max: number;
  range: number;
} {
  if (values.length === 0) {
    return { mean: 0, stdDev: 0, min: 0, max: 0, range: 0 };
  }

  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min;

  return { mean, stdDev, min, max, range };
}

/**
 * Validates that a pattern has sufficient variance to be meaningful.
 * Returns true if the pattern is valid for matching.
 */
export function isValidPattern(values: number[], minStdDev: number = 0.1): boolean {
  if (values.length < 10) return false;

  const stats = getPatternStats(values);
  return stats.stdDev >= minStdDev;
}