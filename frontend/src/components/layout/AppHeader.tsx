import { Bell, ChevronDown, Menu, Search } from 'lucide-react';
import { isHomeRoute } from '../../hooks/useHashRoute';

interface AppHeaderProps {
  route: string;
  onNavigate: (route: string) => void;
  drawerOpen: boolean;
  onToggleDrawer: () => void;
}

/**
 * Compact application header.
 *
 * - Search shortcut focuses the home page's search field (navigating home first
 *   when needed); it performs no searching itself.
 * - Notifications and profile are honest placeholders: the application has no
 *   account or notification system yet, so they are marked aria-disabled and
 *   explain themselves via accessible labels and tooltips.
 */
export default function AppHeader({
  route,
  onNavigate,
  drawerOpen,
  onToggleDrawer,
}: AppHeaderProps) {
  const focusSearch = () => {
    const focus = () => document.getElementById('dashboard-search')?.focus();
    if (isHomeRoute(route)) {
      focus();
    } else {
      onNavigate('#home');
      window.setTimeout(focus, 90);
    }
  };

  return (
    <header className="app-header">
      <button
        type="button"
        className="control-btn menu-toggle"
        aria-expanded={drawerOpen}
        aria-controls="app-sidebar"
        aria-label={drawerOpen ? 'Close navigation menu' : 'Open navigation menu'}
        onClick={onToggleDrawer}
      >
        <Menu size={17} />
      </button>

      <span className="header-context" aria-hidden="true">
        Meynool · Tamil literary knowledge workspace
      </span>

      <div className="topbar-controls">
        <button
          type="button"
          className="control-btn header-search-btn"
          aria-label="Search — focus the search field"
          title="Search the workspace"
          onClick={focusSearch}
        >
          <Search size={16} />
          <span className="header-search-label">Search</span>
        </button>

        <button
          type="button"
          className="control-btn"
          aria-disabled="true"
          aria-label="Notifications — not connected yet"
          title="Notifications are not connected yet."
        >
          <Bell size={16} />
        </button>

        <button
          type="button"
          className="topbar-user"
          aria-disabled="true"
          aria-label="Profile: placeholder identity. No account system is connected."
          title="Placeholder profile — no account system is connected yet."
        >
          <span className="avatar" aria-hidden="true">J</span>
          <span className="user-name">Jessie</span>
          <span className="user-tag">placeholder</span>
          <ChevronDown size={14} aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
