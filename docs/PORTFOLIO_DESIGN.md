# Portfolio visual system and review

This is a refinement of the existing static portfolio, not a replacement of its projects or identity. GitHub renamed `denisisikawa/denis-isikawa-databricks` to `denisisikawa/business-science-lab`. The canonical Pages URL is https://denisisikawa.github.io/business-science-lab/; the former Pages path returned 404 during review on 25 November 2026. No publishing settings or default branches were changed.

## Visual system

- Keep the dark royal burgundy surfaces, restrained gold accents and existing Denis pixel-art identity. Gold marks actions and the executive review hub, rather than every element.
- Preserve DM Sans for reading, Manrope for display and the existing serif accents. Use relative sizes for the refinement, readable line spacing and short label text. Existing legacy micro-labels are not all rewritten in this pass.
- Center content within the established 1220px container. Preserve all eight projects, their category filters, bilingual copy, scope notices and evidence links.
- Use native `details`/`summary`. All disclosures start closed and show an opening action; expanded panels use full catalog width. Deep links intentionally open the containing panels.
- Keep keyboard focus visible, offer reduced-motion and forced-colors fallbacks, retain reading content without JavaScript, and expose mobile navigation without JavaScript.
- Avoid new libraries, remote diagram renderers, generated claims, additional analytics or decorative animation. Existing Google Fonts requests remain; there is no Lighthouse performance score from this review.

The refinement lives in `portfolio-refinement.css`, loaded after the existing styles to keep the change reversible. A future consolidation could remove the historical CSS overrides after broader regression review.

## Diagram reading order

The executive FP&A view is a fan-in: synthetic actuals/budget and public economic indicators feed one monthly cost review, which supports decisions about investigation and forecast assumptions. It is a conceptual reading view, not an assertion of parallel API execution.

The technical view preserves the actual runtime description: BCB is requested before IBGE, fixture mode is explicit, monthly keys and indicators are validated, successful runs write atomically, and failures stop with an error. On wide screens validation and outcomes sit beside one another; on narrow screens the source order remains readable. All formulas, eight-column output contract and source links remain available.

## Reference review — no installation

The following upstream instruction files and available dependency manifests were inspected as design references. No upstream scripts, installer, lifecycle hooks, renderers or gates were executed. Accordingly this work does not claim a full certified run of any external skill. User requirements for existing branding, real content, static delivery and review by PR take precedence over their generic templates and installation suggestions.

| Reference | Inspected revision | Instruction file | Applicable guidance and dependency findings |
| :-- | :-- | :-- | :-- |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill) | `d1a2bb4` | `skills/taste-skill/SKILL.md` | Client-specific composition and real material. Full toolkit requires Node 22+ and a Chromium browser; optional FFmpeg. Its hook and rendering scripts were not installed. |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `8db3633` | `.claude/skills/ui-ux-pro-max/SKILL.md` | Accessibility, responsive layout, explicit disclosure and readable type. Search documents Python 3 with no external dependencies; CLI manifest includes chalk, commander, ora and prompts. No CLI or styling stack installed. |
| [Hallmark](https://github.com/Nutlope/hallmark) | `04977e1` | `skills/hallmark/SKILL.md` | Inspect before redesign, preserve facts, limit visual defaults, keep content visible without scripting. Manifest has no runtime dependency section; optional Together AI workflows were not used. |
| [Interface Skills](https://github.com/jakubkrehel/skills) | `672ae44` | `skills/better-accessibility/SKILL.md`, `skills/better-typography/SKILL.md` | Native semantics, focus, keyboard, motion and text resizing. These are instruction documents; no installation needed for reference reading. |
| [Diagram Design](https://github.com/cathrynlavery/diagram-design) | `b228c5d` | `skills/diagram-design/SKILL.md` | Semantic relationships, restrained focal emphasis and moderate density. Used existing brand tokens; no installation or export tool executed. |
| [Archify](https://github.com/tt-a1i/archify) | `dd71ddd` | `archify/SKILL.md` | Distinguish sources, runtime boundaries and conditional outcomes, retaining source evidence. Repository manifest specifies Node >=18 and development packages including ajv, parse5, saxes and yaml; package manifest also lists simple-icons. No renderer or browser-check gate executed. |

## Validation

- The site has no compilation step: GitHub Pages serves `docs/` directly. `python scripts/check_portfolio_site.py` validates translation pairs, unique IDs, in-page anchors, existing local resources and all disclosures starting closed.
- Embedded application JavaScript and the monthly-close module pass Node syntax checks. The existing banking cost-impact test passes its 576 comparisons and simulation checks.
- Browser review covered 320, 390, 768, 1024 and 1440 CSS-pixel widths; the open macro diagrams did not cause page-level horizontal overflow. The long ABC table retains its own scroll area.
- Filters, EN/PT switching, native keyboard disclosure, deep-link opening and mobile menu/Escape behavior were exercised. No console errors were observed in that session.
- A separate link review covers all four static HTML pages and both READMEs, mapping repository URLs back to actual files as well as checking public HTTP responses. LinkedIn may reject automated HEAD requests; that is not evidence of a broken profile.
- Before/after screenshots were captured from the checked-out original and revised files using the same browser and viewport dimensions. They are review evidence, not a separate deployed version.

Not verified: full screen-reader operation, Safari/iOS and Firefox rendering, a complete WCAG conformance audit, Lighthouse/Core Web Vitals, live Databricks/Genie integrations or the entire Python/dbt/Spark suite. Business logic was not changed. The PR replaces the pre-existing downloaded Codecov shell uploader with a retained coverage artifact so reviewing the branch does not execute that unaudited remote script.
