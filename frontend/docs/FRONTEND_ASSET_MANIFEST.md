# Meynool — Frontend Asset Manifest

## Status

Living document for the frontend contributor. Records every visual asset the Meynool UI actually depends on: where it comes from, what licence applies, where it lives locally, and what it is used for. **Do not invent assets, sources, or licence claims.** If an asset has not been verified, mark it as such.

## Visual target

- **Reference image:** `public/meynool-ref.png` (1672×941, ~2.45 MB).
- This image is the primary visual reference for composition, atmosphere, typography, palette and layout. It is **not** shipped as a runtime background asset — it is a design reference only.
- Do not flatten the scene into a single background image. The environment is built as layered, animated SVG/CSS artwork (see below).

## Excluded assets

- **Background video:** The previously mentioned `gemini_generated_video_e0bab046.mp4` is **not used**. It has been removed from the project and is not imported, referenced, or optimised by this frontend. The brief explicitly excludes a looping background video. The environment is achieved through layered CSS keyframes and original SVG artwork instead.

## Typography

All fonts are loaded from Google Fonts at build/dev time and are not a runtime artwork dependency for the animated environment. Verify the licence for each family before any public launch.

| Family | Weights used | Intended role | Source URL |
|---|---|---|---|
| Noto Serif Tamil | 400, 600, 700 | Tamil brand wordmark and Tamil literary glyphs in the environment | https://fonts.google.com/specimen/Noto+Serif+Tamil |
| Playfair Display | 400, 600, 700, 800 | Display headlines and sidebar quote | https://fonts.google.com/specimen/Playfair+Display |
| Inter | 400, 500, 600 | UI body, controls, labels | https://fonts.google.com/specimen/Inter |

**Current loading path:** `src/styles.css` `@import`s the combined Google Fonts CSS. If the team later prefers self-hosted font files, download the permitted files from Google Fonts, store them under `public/fonts/`, record the download source and licence here, and update the CSS `url()` paths.

**Licence note:** Google Fonts are licensed for the web under the terms of their respective licences (commonly the SIL Open Font Licence for these families, or the Apache Licence 2.0 for Inter). Confirm the current licence on each Google Fonts specimen page before launch and record the exact terms here. Do not assert a licence this manifest has not verified.

## Interface icons

- **Library:** Lucide React, version 1.56.0 (installed as a project dependency via the repository’s existing package manager).
- **Lockfile:** `package-lock.json` updated to include `lucide-react`.
- **Usage:** consistent interface icons across the sidebar, top bar, discovery cards and platform status. Prefer Lucide React over hand-rolled inline SVGs where an icon already exists in the library.
- **Icons used in this phase:** `Book`, `Search`, `Bell`, `Settings`, `Layers`, `BarChart3`, `GitBranch`, `Leaf`, `Disc`, `FileCheck`, `ChevronDown`, `Menu`, `X`, `Network`, `Brain`, `Flower2`, `TreePine`, `Cloud`, `Sparkles`, `CloudRain`, `Sun`, `Moon`, `Wind`, `Waves`, `Mountain`, `Droplets`, `Compass`, `Navigation2`, `Anchor`, `Radio`, `Circle`, `Square`, `Triangle`, `Hexagon`, `Octagon`, `BellRing`, `BellOff`, `Volume2`, `VolumeX`, `MousePointer`, `Move`, `ZoomIn`, `ZoomOut`, `Maximize`, `Minimize`, `Move3D`, `RotateCcw`, `RotateCw`, `ArrowLeft`, `ArrowUp`, `ArrowDown`, `ChevronsLeft`, `ChevronsRight`, `ChevronsUp`, `ChevronsDown`, `Plus`, `Minus`, `Divide`, `Percent`, `Equal`, `Infinity`, `Lambda`, `Sigma`.
- **Custom inline SVG retained:** a small number of original botanical SVG components (lotus, leaf, petal, firefly, tree silhouettes, kolam curves) are authored locally because they need independent animation and are not available as Lucide icons.

## Animated environment — original layered SVG/CSS

The cinematic Tamil literary garden background is **original artwork**, implemented as layered SVG + CSS animations inside `src/App.tsx` and `src/styles.css`. No external image is required for the animated environment.

Layers (parallax depth, back to front):

1. **Deep background** — CSS radial-gradient sky/water wash with slow ambient drift.
2. **Distant atmospheric silhouettes** — original SVG distant mountain/forest/temple-tower silhouette bands for depth, animated subtly.
3. **Trees/branches** — original `TreeSilhouetteLeftSVG` / `TreeSilhouetteRightSVG` SVGs with independent branch and foliage sway keyframes.
4. **Hanging leaves and vines near the upper corners** — `LeafSVG` / vine instances with drift keyframes.
5. **Water + lotus reflection strip near the bottom** — CSS shimmer plus `LotusFlowerSVG` floats.
6. **Golden fireflies** — `FireflySVG` particles with varied drift keyframes.
7. **Foreground leaves + petals** — `LeafSVG` and `PetalSVG` instances drifting in the lower/mid foreground.
8. **Tamil literary glyphs** — faint `Noto Serif Tamil` glyphs placed sparingly in the midground, animated subtly. Avoid random floating Tamil glyphs.
9. **Kolam-inspired ornamental curves** — `KolamCurveSVG`, very subtle, slow pulse.
10. **Cursor-reactive ambient light** — a single efficient pointer-easing rAF loop sets CSS custom properties on `[data-layer]` elements; respects `prefers-reduced-motion` and touch.

All of the above SVG components are original and authored in this repository. They are not sourced from third parties, so no external attribution is required for them. If any later layer is replaced by a downloaded artwork, record its source and licence here.

## Optional future online assets

These are **not required for the current step** and are not present in the project yet. If used later, source, download, store locally, and record the source URL, licence, attribution and local path here before referencing them in code.

- **Tamil manuscript imagery:** possible sources include Wikimedia Commons. If used, verify the individual file’s licence (for example CC BY / CC BY-SA / public domain) and record the exact file page URL, licence, attribution text and local path. Do not use a file whose licence does not permit the intended use.
- **Landscape / botanical textures:** possible sources include Unsplash. If used, verify the Unsplash licence terms for the intended use and record the photo page URL, attribution requirements and local path.

## Colour palette (design tokens)

Defined in `src/styles.css` `:root`. Key families:

- Midnight navy: `#06131A`
- Deep forest teal: `#082B2D`
- Botanical green: `#123E35`
- Peacock teal: `#20BFA8`
- Antique gold: `#D7A64B`
- Warm ivory: `#F5EBD3`
- Muted blue-gray: `#9AAEB5`
- Lavender accent: `#A887D8`
- Derived working shades used sparingly for glows, borders and surfaces are documented inline in the CSS `:root` block.

## Reference image local path

- `public/meynool-ref.png`
- Do not delete the reference image; it is the visual source of truth for this step.

## Files that ship visual assets in this step

- `public/meynool-ref.png` — design reference (not a runtime background).
- `src/styles.css` — design tokens, font import, animated environment styles.
- `src/App.tsx` — layered environment composition + UI shell (original SVG artwork embedded, Lucide React icons for interface elements).
- `docs/FRONTEND_ASSET_MANIFEST.md` — this file.

## Files explicitly excluded from this step

- `public/gemini_generated_video_e0bab046.mp4` — removed; not used.
- Any runtime dependency on an external website for essential background artwork — avoided; the animated environment is self-contained original SVG/CSS.

## Implementation summary

### Phase 0 — Audit and foundation

- **Preserved:** React 19 + Vite 6 + TypeScript 5.7 entry points (`main.tsx`, `App.tsx`, `styles.css`), Google Fonts `@import`, existing build commands (`npm run dev`, `npm run build` = `tsc -b && vite build`), Vite config serving on `127.0.0.1:5173`, `.env.example` with `VITE_API_BASE_URL`, `vite-env.d.ts`.
- **Added:** `lucide-react` 1.56.0 dependency and updated `package-lock.json`.
- **Created:** `docs/FRONTEND_ASSET_MANIFEST.md`.
- **Removed:** `public/gemini_generated_video_e0bab046.mp4` (excluded video), `public/probe-video.html` (diagnostic probe, no longer needed).
- **Fixed:** sidebar decorative quote now reads `அறிவும் இயற்கையும் ஒன்றே உலகம்` without classical attribution; platform status is truthful (API / Database / Research Data all shown as not connected / not yet available, with no fabricated green connected indicators); design tokens include `--lavender` / `--lavender-bright` so the “Find Connections” card renders correctly; card 4 icon kind aligned to the lavender token.

### Phase 1 — Visual foundation and cursor-reactive motion

- Rebuilt the CSS design system around the brief’s exact palette and a coherent spacing/radius/shadow/motion scale.
- Rebuilt the reusable layered botanical environment with distant atmospheric silhouettes, tree branches, hanging vines/leaves, fireflies, drifting petals, mist, lotus pond, manuscript details and a cursor-following ambient light layer.
- Kept animations CSS-keyframe-based and continuous when the pointer is stationary; added `prefers-reduced-motion` and touch fallbacks.
- Retained the existing sidebar, hero, search, topic chips, four discovery cards, platform status and footer as the Phase 1 shell.

### Known limitations and unverified features

- **Screenshots:** the browser preview screenshot capture did not produce composited frames in this environment, so the final visual result was verified through the accessibility-tree snapshot and computed-style evaluation rather than a pixel screenshot. The environment renders, the dev server returns HTTP 200, and there are no console errors.
- **Reference-match fidelity:** the reference image’s exact temple-tower silhouette and atmospheric palette are approximated with original SVG/CSS layers; fine visual tuning should be confirmed by eye in a normal browser.
- **External licensed artwork:** none downloaded yet. Any future Wikimedia Commons / Unsplash assets must be verified individually and recorded here before use.
- **Backend integration:** no backend, database, migration, API contract, ingestion or retrieval changes were made. Platform status is intentionally truthful and shows services as unavailable/unverified.
- **Tamil validation:** the brand name and the decorative quote have not been reviewed by a fluent Tamil scholar; see `docs/BRAND.md`.
- **Lucide icon finalisation:** the interface icon set is appropriate for this phase but may be refined in later phases; the exact list is recorded above.
