import { useEffect, useState, type ReactNode } from 'react';
import BotanicalEnvironment from '../environment/BotanicalEnvironment';
import AppHeader from './AppHeader';
import PageContainer from './PageContainer';
import Sidebar from './Sidebar';

interface AppShellProps {
  route: string;
  onNavigate: (route: string) => void;
  children: ReactNode;
}

/**
 * Application shell shared by every route.
 *
 * The botanical environment stays mounted above the route switch, so the
 * background never restarts on navigation. Sidebar navigation, header
 * controls, and the content container are provided here.
 */
export default function AppShell({ route, onNavigate, children }: AppShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Closing the drawer on any navigation keeps navigation predictable.
  useEffect(() => {
    setDrawerOpen(false);
  }, [route]);

  // The sidebar's own Escape handling covers the drawer; the backdrop covers
  // pointer dismissal. Nothing else is needed here.
  const closeDrawer = () => setDrawerOpen(false);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>

      <BotanicalEnvironment />

      <Sidebar
        route={route}
        onNavigate={onNavigate}
        drawerOpen={drawerOpen}
        onCloseDrawer={closeDrawer}
      />
      {drawerOpen && (
        <div
          className="nav-backdrop"
          aria-hidden="true"
          onClick={closeDrawer}
        />
      )}

      <div className="app-column">
        <AppHeader
          route={route}
          onNavigate={onNavigate}
          drawerOpen={drawerOpen}
          onToggleDrawer={() => setDrawerOpen((open) => !open)}
        />

        <PageContainer>{children}</PageContainer>

        <footer className="page-footer">
          <span>Meynool — Tamil Literary Knowledge &amp; Scientific Evidence Intelligence Platform</span>
          <span>Frontend foundation · Phase 1 &amp; 2</span>
        </footer>
      </div>
    </div>
  );
}
