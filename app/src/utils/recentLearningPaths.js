const STORAGE_KEY = 'neuralascent.recentLearningPaths.v1';
const STORAGE_VERSION = 1;
const MAX_STORED_ITEMS = 50;

function isValidTimestamp(value) {
  return Number.isFinite(value) && value > 0;
}

function normalizeActivityItems(value) {
  const items = Array.isArray(value) ? value : value?.items;
  if (!Array.isArray(items)) return [];

  const newestBySlug = new Map();

  items.forEach((item) => {
    const slug = typeof item?.slug === 'string' ? item.slug.trim() : '';
    const lastOpenedAt = Number(item?.lastOpenedAt);

    if (!slug || !isValidTimestamp(lastOpenedAt)) return;

    const previousTimestamp = newestBySlug.get(slug);
    if (!previousTimestamp || lastOpenedAt > previousTimestamp) {
      newestBySlug.set(slug, lastOpenedAt);
    }
  });

  return Array.from(newestBySlug, ([slug, lastOpenedAt]) => ({ slug, lastOpenedAt }))
    .sort((left, right) => right.lastOpenedAt - left.lastOpenedAt);
}

export function readRecentLearningPathActivity() {
  if (typeof window === 'undefined') return [];

  try {
    const rawValue = window.localStorage.getItem(STORAGE_KEY);
    if (!rawValue) return [];

    const parsedValue = JSON.parse(rawValue);
    if (!parsedValue || typeof parsedValue !== 'object' || parsedValue.version !== STORAGE_VERSION) {
      return [];
    }

    return normalizeActivityItems(parsedValue.items);
  } catch {
    return [];
  }
}

export function markLearningPathOpened(slug, openedAt = Date.now()) {
  const normalizedSlug = typeof slug === 'string' ? slug.trim() : '';
  const timestamp = Number(openedAt);

  if (!normalizedSlug || !isValidTimestamp(timestamp) || typeof window === 'undefined') return;

  const itemsBySlug = new Map(
    readRecentLearningPathActivity().map((item) => [item.slug, item.lastOpenedAt])
  );
  itemsBySlug.set(normalizedSlug, timestamp);

  const items = Array.from(itemsBySlug, ([itemSlug, lastOpenedAt]) => ({
    slug: itemSlug,
    lastOpenedAt
  }))
    .sort((left, right) => right.lastOpenedAt - left.lastOpenedAt)
    .slice(0, MAX_STORED_ITEMS);

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({
      version: STORAGE_VERSION,
      items
    }));
  } catch {
    // Storage is a convenience only; navigation must continue if it is unavailable.
  }
}

export function sortLearningPathsByRecency(paths, activity) {
  if (!Array.isArray(paths)) return [];

  const activityBySlug = new Map(
    normalizeActivityItems(activity).map((item) => [item.slug, item.lastOpenedAt])
  );

  return paths
    .map((path, originalIndex) => ({
      path: {
        ...path,
        lastOpenedAt: activityBySlug.get(path?.slug)
      },
      originalIndex
    }))
    .sort((left, right) => {
      const leftTimestamp = left.path.lastOpenedAt;
      const rightTimestamp = right.path.lastOpenedAt;
      const leftVisited = isValidTimestamp(leftTimestamp);
      const rightVisited = isValidTimestamp(rightTimestamp);

      if (leftVisited !== rightVisited) return leftVisited ? -1 : 1;
      if (leftVisited && rightVisited && leftTimestamp !== rightTimestamp) {
        return rightTimestamp - leftTimestamp;
      }
      return left.originalIndex - right.originalIndex;
    })
    .map(({ path }) => path);
}

export function formatLastOpened(lastOpenedAt, now = Date.now()) {
  const timestamp = Number(lastOpenedAt);
  const suppliedNow = Number(now);
  const currentTimestamp = isValidTimestamp(suppliedNow) ? suppliedNow : Date.now();

  if (!isValidTimestamp(timestamp)) return 'Never opened';

  const elapsedMs = Math.max(0, currentTimestamp - timestamp);
  if (elapsedMs < 60 * 1000) return 'Just now';
  if (elapsedMs < 60 * 60 * 1000) return `${Math.floor(elapsedMs / (60 * 1000))} minutes ago`;
  if (elapsedMs < 24 * 60 * 60 * 1000) return `${Math.floor(elapsedMs / (60 * 60 * 1000))} hours ago`;

  const openedDate = new Date(timestamp);
  const currentDate = new Date(currentTimestamp);
  const openedDay = new Date(openedDate.getFullYear(), openedDate.getMonth(), openedDate.getDate());
  const currentDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
  const calendarDays = Math.round((currentDay - openedDay) / (24 * 60 * 60 * 1000));

  if (calendarDays === 1) return 'Yesterday';
  if (calendarDays > 1) return `${calendarDays} days ago`;
  return `${Math.floor(elapsedMs / (24 * 60 * 60 * 1000))} days ago`;
}
