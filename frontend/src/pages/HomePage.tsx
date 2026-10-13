import { useState } from 'react';
import {
  Activity,
  ArrowRight,
  BookOpen,
  Database,
  FileCheck,
  FlaskConical,
  Leaf,
  Network,
  Search,
} from 'lucide-react';

/* ---------- Discovery cards (existing dashboard content) ---------- */
const DISCOVERY_CARDS = [
  { id: 'texts', title: 'Explore Tamil Texts', desc: 'Read and analyse classical Tamil literature', Icon: BookOpen, iconKind: 'gold', route: '#texts' },
  { id: 'nature', title: 'Discover Natural Knowledge', desc: 'Explore plants, environment and traditional understanding', Icon: Leaf, iconKind: 'teal', route: '#natural-knowledge' },
  { id: 'science2', title: 'View Scientific Evidence', desc: 'Find modern research and verify claims', Icon: FlaskConical, iconKind: 'gold', route: '#science' },
  { id: 'connects', title: 'Find Connections', desc: 'Explore relationships between literature and science', Icon: Network, iconKind: 'blue', route: '#connections' },
] as const;

const SUGGEST_PILLS = [
  'Siddha medicine',
  'Plants in Sangam literature',
  'Human biology',
  'Ecology',
  'Nutrition',
  'Mind and cognition',
];

interface HomePageProps {
  onNavigate: (route: string) => void;
}

/**
 * Existing Meynool landing dashboard, preserved inside the new shell.
 * Search is honestly unconnected: submitting shows an explicit notice instead
 * of fabricating results. Topic chips populate the search field only.
 */
export default function HomePage({ onNavigate }: HomePageProps) {
  const [query, setQuery] = useState('');
  const [searchNotice, setSearchNotice] = useState(false);

  function submitSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Honest behaviour: no search backend is connected, so we state that
    // plainly instead of inventing results.
    setSearchNotice(query.trim().length > 0);
  }

  return (
    <>
      {/* Hero */}
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><span>TAMIL LITERATURE</span><span className="eyebrow-line" /><span>×</span><span className="eyebrow-line" /><span>SCIENTIFIC EXPLORATION</span></div>
          <h1>
            Ancient wisdom.<br />
            <span className="line-two">Living knowledge.</span>
          </h1>
          <p className="hero-subtitle">Explore Tamil literary heritage alongside modern scientific research.</p>
        </div>
      </section>

      {/* Search + chips */}
      <section style={{ paddingTop: 10 }}>
        <form className="search-form" onSubmit={submitSearch}>
          <span className="search-icon" aria-hidden="true"><Search size={17} strokeWidth={1.8} /></span>
          <input
            id="dashboard-search"
            aria-label="Search Tamil texts, scientific concepts, or research topics"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (searchNotice) setSearchNotice(false);
            }}
            placeholder="Search Tamil texts, scientific concepts, or research topics..."
          />
          <button type="submit" className="search-go" aria-label="Search">
            <ArrowRight size={16} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </form>
        {searchNotice && (
          <p className="search-notice" role="status">
            Search is not connected yet — no Tamil literature or scientific database has been queried, so there are no results to show.
          </p>
        )}
        <div className="search-pills">
          <span className="try-label">Try:</span>
          <div className="pill-list">
            {SUGGEST_PILLS.map((p) => (
              <button
                key={p}
                className="search-pill"
                type="button"
                onClick={() => {
                  setQuery(p);
                  setSearchNotice(false);
                  document.getElementById('dashboard-search')?.focus();
                }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Discovery cards */}
      <section style={{ paddingTop: 6 }}>
        <div className="cards-row">
          {DISCOVERY_CARDS.map((card) => (
            <article key={card.id} className="discovery-card">
              <div className={`card-icon ${card.iconKind}`}>
                <card.Icon size={20} strokeWidth={1.7} aria-hidden="true" />
              </div>
              <h3>{card.title}</h3>
              <p>{card.desc}</p>
              <button
                className="card-action"
                type="button"
                aria-label={`Open ${card.title}`}
                onClick={() => onNavigate(card.route)}
              >
                <ArrowRight size={14} strokeWidth={1.7} aria-hidden="true" />
              </button>
            </article>
          ))}
        </div>
      </section>

      {/* Platform status — truthful only; no fabricated connection state */}
      <section style={{ paddingBottom: 4 }}>
        <div className="status-bar">
          <div className="status-header">Platform Status</div>
          <div className="status-col">
            <div className="status-indicator"><Activity size={18} strokeWidth={1.7} aria-hidden="true" /></div>
            <div className="status-title">API</div>
            <div className="status-sub">Not connected</div>
          </div>
          <div className="status-col">
            <div className="status-indicator"><Database size={18} strokeWidth={1.7} aria-hidden="true" /></div>
            <div className="status-title">Database</div>
            <div className="status-sub">Not connected</div>
          </div>
          <div className="status-col">
            <div className="status-indicator"><FileCheck size={18} strokeWidth={1.7} aria-hidden="true" /></div>
            <div className="status-title">Research Data</div>
            <div className="status-sub">Not yet available</div>
          </div>
        </div>
      </section>
    </>
  );
}
