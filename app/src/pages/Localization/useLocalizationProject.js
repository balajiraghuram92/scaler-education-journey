import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../../api/client';

/**
 * Single source of truth for the selected Localization Lab project.
 * Reads the slug from the `project` URL query parameter, falling back to the
 * first project from the API, and loads the full project (with locales).
 */
export default function useLocalizationProject() {
  const [searchParams, setSearchParams] = useSearchParams();
  const querySlug = searchParams.get('project');

  const [projects, setProjects] = useState([]);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setProject(null);

    (async () => {
      try {
        const list = await api.localization.getProjects();
        if (cancelled) return;
        const safeList = Array.isArray(list) ? list : [];
        setProjects(safeList);

        const resolved = (querySlug && safeList.some((p) => p.slug === querySlug))
          ? querySlug
          : safeList[0]?.slug || null;
        if (!resolved) return;

        const loaded = await api.localization.getProject(resolved);
        if (!cancelled) setProject(loaded);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to load localization project.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [querySlug]);

  const selectProject = useCallback((nextSlug) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set('project', nextSlug);
      return next;
    });
  }, [setSearchParams]);

  return { slug: project?.slug || null, project, projects, loading, error, selectProject };
}
