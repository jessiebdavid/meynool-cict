import { ArrowLeft, Clock } from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  onNavigate: (route: string) => void;
}

/**
 * Honest empty state for navigation destinations that belong to later
 * roadmap phases. It loads and claims nothing: no data, no search, no
 * services — just a truthful explanation and a way back.
 */
export default function PlaceholderPage({ title, onNavigate }: PlaceholderPageProps) {
  return (
    <section className="route-placeholder" aria-labelledby="placeholder-title">
      <div className="ph-icon" aria-hidden="true">
        <Clock size={22} strokeWidth={1.7} />
      </div>
      <h1 id="placeholder-title">{title}</h1>
      <p>
        This section is part of a later roadmap phase and has not been
        implemented yet. Nothing has been loaded, searched, or connected here.
      </p>
      <p className="ph-note">
        Available now: the Home dashboard. Scientific literature search,
        analysis, connections, and backend data arrive in future phases after
        review.
      </p>
      <button
        type="button"
        className="ph-back"
        onClick={() => onNavigate('#home')}
      >
        <ArrowLeft size={14} strokeWidth={1.8} aria-hidden="true" />
        Back to Home
      </button>
    </section>
  );
}
