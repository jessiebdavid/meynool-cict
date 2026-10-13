import { useEffect, useState } from 'react';

type ApiState = 'checking' | 'connected' | 'unavailable';
const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '');

const dimensions = [
  { number: '01', label: 'Literal source', detail: 'Original passage, edition, locator and textual uncertainty.' },
  { number: '02', label: 'Context & interpretation', detail: 'Historical setting, terminology and scholarly readings.' },
  { number: '03', label: 'Science & evidence', detail: 'Modern research, claim-level citations and contradictions.' },
  { number: '04', label: 'Chronology', detail: 'Source history and scientific developments, with unknown dates preserved.' },
];

function App() {
  const [apiState, setApiState] = useState<ApiState>('checking');
  const [query, setQuery] = useState('');

  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}/health`)
      .then((response) => {
        if (!response.ok) throw new Error('API unavailable');
        return response.json();
      })
      .then((data) => {
        if (active) setApiState(data.service === 'meynool-api' ? 'connected' : 'unavailable');
      })
      .catch(() => active && setApiState('unavailable'));
    return () => { active = false; };
  }, []);

  function submitSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Search is not implemented yet. Keep the query visible instead of implying results exist.
    if (query.trim()) {
      window.alert('Search is not connected yet. The backend contributor will implement the agreed search API.');
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" aria-label="Meynool home">
          <span className="brand-mark">மெ</span>
          <span><strong>Meynool</strong><small>மெய்நூல் · Research</small></span>
        </a>
        <div className="nav-caption">WORKSPACE</div>
        <nav className="nav-list" aria-label="Main navigation">
          <a className="nav-item active" href="#overview"><span>◫</span> Overview</a>
          <a className="nav-item" href="#library"><span>▤</span> Literary library <em>Planned</em></a>
          <a className="nav-item" href="#science"><span>⌕</span> Scientific literature <em>Planned</em></a>
          <a className="nav-item" href="#analysis"><span>◇</span> 1D–4D analysis <em>Planned</em></a>
          <a className="nav-item" href="#evidence"><span>⊙</span> Claims & evidence <em>Planned</em></a>
          <a className="nav-item" href="#hypotheses"><span>⌁</span> Hypotheses <em>Planned</em></a>
        </nav>
        <div className="sidebar-bottom">
          <div className="integrity-note"><span className="integrity-dot" /> Evidence before assertion</div>
          <p>Historical text, interpretation and verified science stay separate.</p>
          <div className="sidebar-version">LOCAL WORKSPACE · STARTER 0.1</div>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumb">Research workspace <span>/</span> Overview</div>
          <div className={`connection ${apiState}`}><span className="connection-dot" />{apiState === 'checking' ? 'Checking API' : apiState === 'connected' ? 'API connected' : 'API not connected'}</div>
        </header>

        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-line" /> SOURCE-GROUNDED RESEARCH</div>
            <h1>Read the past.<br /><span>Verify the claim.</span></h1>
            <p className="hero-description">Explore Tamil literary knowledge alongside modern scientific literature—with every interpretation separated from evidence, and every claim accountable to its sources.</p>
            <form className="search-form" onSubmit={submitSearch}>
              <span className="search-icon">⌕</span>
              <input aria-label="Search sources" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search a passage, concept, paper or claim…" />
              <button type="submit">Search <span>↗</span></button>
            </form>
            <div className="search-hint">Search will activate when the retrieval API is implemented.</div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit orbit-three" />
            <div className="art-core"><span>மெய்</span><small>TRUTH / EVIDENCE</small></div>
            <span className="art-node node-one">TXT</span><span className="art-node node-two">BIO</span><span className="art-node node-three">↗</span>
          </div>
          <div className="hero-footnote"><span className="tiny-star">✳</span> A research assistant—not a substitute for scientific validation.</div>
        </section>

        <section className="section-block" id="analysis">
          <div className="section-heading"><div><div className="eyebrow">THE MEYNOOL FRAMEWORK</div><h2>Four layers of understanding</h2></div><span className="section-meta">PROJECT-SPECIFIC ANALYSIS MODEL</span></div>
          <div className="dimension-grid">
            {dimensions.map((dimension) => <article className="dimension-card" key={dimension.number}>
              <div className="dimension-top"><span className="dimension-number">{dimension.number}</span><span className="dimension-symbol">{dimension.number === '01' ? '≋' : dimension.number === '02' ? '⌘' : dimension.number === '03' ? '⊙' : '◷'}</span></div>
              <h3>{dimension.label}</h3><p>{dimension.detail}</p><div className="card-state">IN DESIGN <span>↗</span></div>
            </article>)}
          </div>
        </section>

        <section className="lower-grid">
          <article className="panel" id="library"><div className="panel-heading"><div><div className="eyebrow">SOURCE CATALOGUE</div><h2>Research starts with provenance</h2></div><span className="panel-icon">▤</span></div>
            <p className="panel-copy">Original Tamil passages, edition details, attribution status and scientific publications will be linked without merging historical text with modern interpretation.</p>
            <div className="empty-state"><div className="empty-icon">＋</div><strong>No source records yet</strong><span>Source ingestion is not implemented.</span></div>
          </article>
          <article className="panel evidence-panel" id="evidence"><div className="panel-heading"><div><div className="eyebrow">EVIDENCE INTEGRITY</div><h2>Claims need traceable support</h2></div><span className="panel-icon">⊙</span></div>
            <div className="integrity-rows"><div><span className="status-ring muted" /><span>Supported by evidence</span><strong>—</strong></div><div><span className="status-ring muted" /><span>Contradicted / qualified</span><strong>—</strong></div><div><span className="status-ring muted" /><span>Unverified hypotheses</span><strong>—</strong></div></div>
            <div className="not-measured"><span>i</span><div><strong>Not measured yet</strong><p>Counts and hallucination rates will only appear after a reviewed evaluation set exists.</p></div></div>
          </article>
        </section>
        <footer className="page-footer"><span>மெய்நூல் · MEYNOOL</span><span>Truth. Text. Evidence.</span><span>Local-first · Research use only</span></footer>
      </main>
    </div>
  );
}

export default App;
