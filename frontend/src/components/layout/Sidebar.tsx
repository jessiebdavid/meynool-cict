import { useEffect, useRef, type Ref } from 'react';
import {
  BarChart3,
  Bell,
  BookOpen,
  Home,
  Library,
  Microscope,
  Network,
  Settings,
  Telescope,
  X,
} from 'lucide-react';
import { routeMatches } from '../../hooks/useHashRoute';

/**
 * Original Meynool brand mark — a gold lotus/botanical emblem drawn as SVG.
 * Decorative; the accessible name comes from the adjacent brand text.
 */
function LotusIcon({ size = 54, color = 'currentColor' }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" aria-hidden="true">
      <path d="M32 10c4 8 4 14 0 22-4-8-4-14 0-22z" fill={color} opacity=".95" />
      <path d="M18 18c7 3 11 8 14 14-8-1-13-5-14-14z" fill={color} opacity=".8" />
      <path d="M46 18c-7 3-11 8-14 14 8-1 13-5 14-14z" fill={color} opacity=".8" />
      <path d="M10 30 C 17 29, 24 31, 30 36 C 22 40, 14 38, 10 30 Z" fill={color} opacity=".62" />
      <path d="M54 30 C 47 29, 40 31, 34 36 C 42 40, 50 38, 54 30 Z" fill={color} opacity=".62" />
      <path
        d="M12 44c6 6 13 9 20 9s14-3 20-9"
        stroke={color}
        strokeWidth="2.2"
        strokeLinecap="round"
        opacity=".8"
      />
      <circle cx="32" cy="33" r="3.6" fill="#D7A64B" opacity=".9" />
    </svg>
  );
}

interface NavItemDef {
  id: string;
  label: string;
  route: string;
  Icon: typeof Home;
}

const NAV_ITEMS: NavItemDef[] = [
  { id: 'home', label: 'Home', route: '#home', Icon: Home },
  { id: 'texts', label: 'Tamil Texts', route: '#texts', Icon: BookOpen },
  { id: 'research', label: 'Research', route: '#research', Icon: Telescope },
  { id: 'science', label: 'Scientific Literature', route: '#science', Icon: Microscope },
  { id: 'connections', label: 'Connections', route: '#connections', Icon: Network },
  { id: 'analysis', label: 'Analysis', route: '#analysis', Icon: BarChart3 },
  { id: 'collections', label: 'Collections', route: '#collections', Icon: Library },
];

const SECONDARY_ITEMS: NavItemDef[] = [
  { id: 'notifications', label: 'Notifications', route: '#notifications', Icon: Bell },
  { id: 'settings', label: 'Settings', route: '#settings', Icon: Settings },
];

interface NavigationItemProps {
  item: NavItemDef;
  active: boolean;
  onNavigate: (route: string) => void;
  anchorRef?: Ref<HTMLAnchorElement>;
}

function NavigationItem({ item, active, onNavigate, anchorRef }: NavigationItemProps) {
  const { Icon } = item;
  return (
    <li>
      <a
        ref={anchorRef}
        href={item.route}
        className={`nav-item${active ? ' active' : ''}`}
        aria-current={active ? 'page' : undefined}
        onClick={(event) => {
          event.preventDefault();
          onNavigate(item.route);
        }}
      >
        <span className="nav-icon">
          <Icon size={17} strokeWidth={1.8} />
        </span>
        <span>{item.label}</span>
      </a>
    </li>
  );
}

interface SidebarProps {
  route: string;
  onNavigate: (route: string) => void;
  drawerOpen: boolean;
  onCloseDrawer: () => void;
}

function isDrawerViewport(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(max-width: 780px)').matches;
}

export default function Sidebar({ route, onNavigate, drawerOpen, onCloseDrawer }: SidebarProps) {
  const firstLinkRef = useRef<HTMLAnchorElement>(null);

  // Move focus into the drawer when it opens on small screens.
  useEffect(() => {
    if (drawerOpen && isDrawerViewport()) {
      firstLinkRef.current?.focus();
    }
  }, [drawerOpen]);

  // Escape closes the drawer; focus returns to the menu toggle.
  useEffect(() => {
    if (!drawerOpen) return undefined;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onCloseDrawer();
        document.querySelector<HTMLElement>('.menu-toggle')?.focus();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [drawerOpen, onCloseDrawer]);

  // Prevent background scrolling while the drawer is open (small screens only).
  useEffect(() => {
    if (drawerOpen && isDrawerViewport()) {
      const previous = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = previous;
      };
    }
    return undefined;
  }, [drawerOpen]);

  return (
    <aside
      id="app-sidebar"
      className={`sidebar${drawerOpen ? ' drawer-open' : ''}`}
      aria-label="Main navigation"
    >
      <button
        type="button"
        className="control-btn drawer-close"
        aria-label="Close navigation"
        onClick={() => {
          onCloseDrawer();
          document.querySelector<HTMLElement>('.menu-toggle')?.focus();
        }}
      >
        <X size={16} />
      </button>

      <div className="brand">
        <span className="brand-lotus">
          <LotusIcon />
        </span>
        <div>
          <div className="brand-name">Meynool</div>
          <div className="brand-sub">மெய்நூல்</div>
        </div>
      </div>

      <nav aria-label="Primary">
        <div className="nav-caption">EXPLORE</div>
        <ul className="nav-list">
          {NAV_ITEMS.map((item, index) => (
            <NavigationItem
              key={item.id}
              item={item}
              active={routeMatches(route, item.route)}
              anchorRef={index === 0 ? firstLinkRef : undefined}
              onNavigate={(target) => {
                onNavigate(target);
                onCloseDrawer();
              }}
            />
          ))}
        </ul>

        <div className="nav-divider" />
        <div className="nav-caption">WORKSPACE</div>
        <ul className="nav-list">
          {SECONDARY_ITEMS.map((item) => (
            <NavigationItem
              key={item.id}
              item={item}
              active={routeMatches(route, item.route)}
              onNavigate={(target) => {
                onNavigate(target);
                onCloseDrawer();
              }}
            />
          ))}
        </ul>
      </nav>

      <div className="sidebar-bottom">
        <p className="sidebar-quote" lang="ta">
          அறிவும் இயற்கையும் ஒன்றே உலகம்
        </p>
        <div className="sidebar-version">LOCAL WORKSPACE · STARTER 0.1</div>
      </div>
    </aside>
  );
}
