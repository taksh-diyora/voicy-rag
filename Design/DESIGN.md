---
name: Nocturne Scholar
colors:
  surface: '#101319'
  surface-dim: '#101319'
  surface-bright: '#363940'
  surface-container-lowest: '#0b0e14'
  surface-container-low: '#191c22'
  surface-container: '#1d2026'
  surface-container-high: '#272a31'
  surface-container-highest: '#32353c'
  on-surface: '#e1e2eb'
  on-surface-variant: '#c3c6d4'
  inverse-surface: '#e1e2eb'
  inverse-on-surface: '#2e3037'
  outline: '#8c909e'
  outline-variant: '#424752'
  surface-tint: '#aec6ff'
  primary: '#aec6ff'
  on-primary: '#002e6b'
  primary-container: '#5c8ff1'
  on-primary-container: '#00275e'
  inverse-primary: '#1c5bba'
  secondary: '#b6c7e5'
  on-secondary: '#203149'
  secondary-container: '#394a63'
  on-secondary-container: '#a8b9d7'
  tertiary: '#ffb2b7'
  on-tertiary: '#67001c'
  tertiary-container: '#ec6374'
  on-tertiary-container: '#5b0017'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#aec6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004396'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#b6c7e5'
  on-secondary-fixed: '#091c32'
  on-secondary-fixed-variant: '#374860'
  tertiary-fixed: '#ffdadb'
  tertiary-fixed-dim: '#ffb2b7'
  on-tertiary-fixed: '#40000e'
  on-tertiary-fixed-variant: '#8a182f'
  background: '#101319'
  on-background: '#e1e2eb'
  surface-variant: '#32353c'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  label-code:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-badge:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  meta-mono:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '400'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system embodies the contemplative, distraction-free atmosphere of a quiet night desk. Designed for intense study, active audio-text synthesis, and retrieval-augmented reading, the interface retreats into the background so literature, papers, and AI discourse remain the central focus.

The visual style blends **Deep Night Minimalist** precision with **Technical Modernism**:
- **Atmosphere:** Deep ink slate tones, evoking late-night research sessions under a directional lamp.
- **Demeanor:** Scholarly, composed, deliberate, and high-utility. Zero decorative noise or saturated distractions.
- **Tactility:** Crisp hair-thin glass-edge divisions (`rgba(255, 255, 255, 0.07)`), sharp typographic contrast, and restrained interactive blue accents that activate only when focus or synthesis is engaged.

## Colors

The palette is tuned specifically for sustained nocturnal legibility and low cognitive fatigue.

### Core Palette
- **Canvas Base (`#0E1117`):** The primary deep ink backdrop. Grounding, light-absorbent, and pitch-calibrated.
- **Surface Layer (`#161B27`):** Working reading panels, sidebar tiers, and audio waveform dock canvases.
- **Elevated Canvas (`#1E2535`):** Cards, popovers, contextual tooltips, and floating transcription HUDs.
- **Structural Border (`rgba(255, 255, 255, 0.07)`): Precise 1px architectural lines defining container edges without visual weight.

### Functional & Semantic Accents
- **Interactive Blue (`#5B8EF0`):** Action items, active focus states, text selection, and vector search query highlights.
- **Recording Crimson (`#E05A6B`):** Active microphone capture, audio streaming states, and hotkey recording indicators.
- **Active / Parsed Green (`#4ADE80`):** System status dots, index sync confirmations, and grounded source citations.
- **Amber Citation (`#FBBF24`):** Retrieval warning notices, speculative answer badges, and highlighted margin notes.

### Text Contrast Tiers
- **Primary Text (`#E2E8F4`):** Cool off-white, optimized for readable prose without blinding glare.
- **Secondary / Slate (`#6E7F9A`):** Low-contrast interface chrome, column titles, and structural labels.
- **Subtle Muted (`#445168`):** Inactive timestamps, inactive shortcut keys, and collapsed metadata.

## Typography

Typography delivers three distinct responsibilities:
1. **Plus Jakarta Sans (Brand & Document Titling):** Soft geometric structure for reader chapter headers and structural panel markers.
2. **Inter (Reading & Interactive UI):** Clean, neutral, high-legibility glyphs designed for long-form reading of extracted PDF fragments, synthesize-responses, and menu states.
3. **JetBrains Mono (Metadata, Transcriptions & Citations):** Technical monospaced cadence for document offsets, chunk boundaries, voice latency meters, and keyboard accelerator labels.

Use `body-lg` strictly within the reader content canvas to preserve rhythmic optical pace.

## Layout & Spacing

### Fixed-Viewport Architectural Philosophy
- **Zero Page-Level Scrolling:** The root canvas (`100vh`/`100dvh`, `100vw`) is pinned. No browser-level scrollbars are permitted.
- **Docked Three-Column App Shell:**
  - **Left Rail (Source Navigation / Vector Index):** Fixed 260px–320px width, containing loaded PDFs, document structure, and bookmark tiers.
  - **Center Stage (The Reader Viewport):** Flex-grow layout bounded by maximum readable line-length (68ch to 75ch), featuring independent internal vertical scrolling.
  - **Right Rail (Voice Agent & Synthesis Panel):** 360px–420px width, housing continuous RAG stream summaries, audio timeline controls, and citation verification nodes.
- **Persistent Bottom Voice Bar:** 64px fixed-height floating or docked console housing the microphone state, waveform visualization, and hotkey listeners.
- **Grid Gutters & Inner Spacing:** A tight, disciplined 4px/8px modular base scale governs all internal micro-gaps to keep panels dense, technical, and compact.

## Elevation & Depth

Visual plane differentiation relies on strict tone shifting and precision borders rather than heavy dropshadows:

1. **Base Floor (`#0E1117`):** The foundational substrate behind sidebars and gutters.
2. **First Tier Surfaces (`#161B27`):** Reading stage, navigation sidebars, and top navigation header. Defined by `border: 1px solid rgba(255, 255, 255, 0.07)`.
3. **Floating & Elevated Tier (`#1E2535`):** Cards, contextual citation previews, query boxes, and playback floating pills. Uses a fine ambient shadow: `box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45)`.
4. **Active Focus & Hover Highlights:** Interactive panels gain a subtle outer glow: `box-shadow: 0 0 0 1px #5B8EF0, 0 4px 16px rgba(91, 142, 240, 0.15)`.

## Shapes

The interface employs strict geometric rules:
- **Cards and Panels:** Explicitly clamped to **10px** (`0.625rem`) corner radius.
- **Interactive Controls (Buttons, Text Inputs, Dropdowns):** Strict **8px** (`0.5rem`) corner radius.
- **Chips, Audio Badges, and Status Indicators:** Full pill geometry clamped at **50px** (`3.125rem`).

## Components

### Buttons
- **Primary Interactive:** Background `#5B8EF0`, foreground `#FFFFFF`, border-radius 8px, padding `8px 16px`, typography `Inter` 14px SemiBold. Hover: `#4A7DE0`.
- **Ghost/Tertiary:** Background transparent, text `#6E7F9A`, border: 1px solid transparent. Hover: background `rgba(255, 255, 255, 0.04)`, text `#E2E8F4`.
- **Voice Action Button:** Pill-shaped (`rounded-full`), 44px height. Idle: background `#1E2535`, border `rgba(255, 255, 255, 0.1)`. Active Recording: background `#E05A6B`, text `#FFFFFF`, subtle breathing outline animation.

### Badges & Pill Chips
- **Citation Badges:** Height 22px, border-radius 50px, background `#1E2535`, border `1px solid rgba(255, 255, 255, 0.08)`, typography `JetBrains Mono` 11px uppercase.
- **Audio Timecode Chips:** Background `rgba(91, 142, 240, 0.12)`, text `#5B8EF0`, border `1px solid rgba(91, 142, 240, 0.25)`.

### Input Fields & Prompt Consoles
- **Search & RAG Query Bar:** Background `#161B27`, border `1px solid rgba(255, 255, 255, 0.08)`, border-radius 8px, height 40px, padding `0 12px`. Text `#E2E8F4`, placeholder `#6E7F9A`. Focus ring: `1px solid #5B8EF0`.

### Cards & Reading Panels
- **Chunk / Citation Node:** Background `#1E2535`, border `1px solid rgba(255, 255, 255, 0.07)`, border-radius 10px, padding 16px. Internal monospace metadata row on top, readable `body-md` body, and grounded link indicators below.

### Status Indicators
- **Real-Time Indicators:** 6px circular dot (`rounded-full`). Connected/Indexed: `#4ADE80`. Indexing/Syncing: `#FBBF24`. Mic Hot: `#E05A6B` with outward pulse ring.