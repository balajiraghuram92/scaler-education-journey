const UNITS = [
  { limit: 60, divisor: 1, unit: 'second' },
  { limit: 3600, divisor: 60, unit: 'minute' },
  { limit: 86400, divisor: 3600, unit: 'hour' },
  { limit: 604800, divisor: 86400, unit: 'day' },
  { limit: 2629800, divisor: 604800, unit: 'week' },
  { limit: 31557600, divisor: 2629800, unit: 'month' },
  { limit: Infinity, divisor: 31557600, unit: 'year' }
];

/**
 * "3 minutes ago" style label for an ISO timestamp. Returns '' for missing/invalid input.
 */
export function timeAgo(value, now = Date.now()) {
  if (!value) return '';
  const time = new Date(value).getTime();
  if (Number.isNaN(time)) return '';

  const seconds = Math.round((now - time) / 1000);
  if (seconds < 45) return 'just now';

  const match = UNITS.find((entry) => seconds < entry.limit);
  const amount = Math.max(1, Math.floor(seconds / match.divisor));
  return `${amount} ${match.unit}${amount === 1 ? '' : 's'} ago`;
}

/**
 * Compact duration such as "2h 15m" or "40m" from a number of seconds.
 */
export function formatDuration(totalSeconds) {
  const seconds = Math.max(0, Math.round(totalSeconds || 0));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m`;
  return seconds > 0 ? '<1m' : '0m';
}
