import { useState, useEffect, useCallback, useSyncExternalStore } from 'react';
import { api } from '../../../api/client';

const STORAGE_KEY = 'localization-vendor-id';

function readStoredId() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw === null) return null;
    const id = parseInt(raw, 10);
    return Number.isNaN(id) ? null : id;
  } catch {
    return null;
  }
}

// Shared selected-vendor id so the shell dropdown and every page stay in sync.
// It is backed by sessionStorage, so the selection also survives navigation.
let sharedSelectedId = readStoredId();
const idListeners = new Set();

function subscribeToSelectedId(listener) {
  idListeners.add(listener);
  return () => {
    idListeners.delete(listener);
  };
}

function getSharedSelectedId() {
  return sharedSelectedId;
}

function setSharedSelectedId(id) {
  sharedSelectedId = id;
  try {
    if (id === null || id === undefined) {
      sessionStorage.removeItem(STORAGE_KEY);
    } else {
      sessionStorage.setItem(STORAGE_KEY, String(id));
    }
  } catch {
    // sessionStorage unavailable; module state still keeps this tab in sync
  }
  idListeners.forEach((listener) => listener());
}

/**
 * Single source of truth for the selected vendor. Loads the roster with
 * api.vendorPortal.getRoster(), keeps the selected id in sessionStorage, and
 * defaults to the first roster vendor only when nothing valid is stored.
 */
export default function useSelectedVendor() {
  const [roster, setRoster] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const selectedId = useSyncExternalStore(subscribeToSelectedId, getSharedSelectedId);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.vendorPortal.getRoster();
        if (cancelled) return;
        const safeList = Array.isArray(data) ? data : [];
        setRoster(safeList);
        if (!safeList.some((v) => v.id === getSharedSelectedId())) {
          setSharedSelectedId(safeList[0]?.id ?? null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to load vendor roster.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectVendor = useCallback((id) => {
    setSharedSelectedId(id);
  }, []);

  const vendor = roster.find((v) => v.id === selectedId) || null;

  return { roster, vendor, selectVendor, loading, error };
}
