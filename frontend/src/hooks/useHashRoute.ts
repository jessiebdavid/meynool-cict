import { useEffect, useState } from 'react';

/**
 * Minimal hash router — matches the repository's existing `#route`
 * navigation convention (no router dependency added).
 *
 * Route strings look like "#/texts" or "#/".
 */
function currentRoute(): string {
  const h = window.location.hash;
  return h === '' ? '#/' : h;
}

export function useHashRoute(): [string, (route: string) => void] {
  const [route, setRoute] = useState<string>(currentRoute);

  useEffect(() => {
    const onHashChange = () => setRoute(currentRoute());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigate = (next: string) => {
    if (next === route) return;
    window.location.hash = next;
  };

  return [route, navigate];
}

/** True when the given route (or its base path) is active. */
export function routeMatches(route: string, target: string): boolean {
  if (target === '#/' || target === '/') return route === '#/' || route === '' || route === '#';
  return route === target || route.startsWith(`${target}/`);
}
