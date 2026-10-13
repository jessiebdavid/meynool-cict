import type { ReactNode } from 'react';

/**
 * Reusable main content wrapper used by every route. Provides the
 * `main-content` landmark (skip-link target) and constrains width/overflow.
 */
export default function PageContainer({ children }: { children: ReactNode }) {
  return (
    <main id="main-content" className="main-content" tabIndex={-1}>
      {children}
    </main>
  );
}
