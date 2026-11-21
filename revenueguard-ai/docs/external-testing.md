# External testing

## Browser sandbox
https://denisisikawa.github.io/business-science-lab/revenueguard-sandbox/

The standalone GitHub Pages experiment runs the Python generator and reconciliation engine via Pyodide 0.27.7. It is deliberately unlinked from the portfolio landing page and uses a noindex directive (not access control). Requires network access to jsDelivr on initial load. The HTML embeds snapshots of simulator.py and sandbox_engine.py; regenerate those definitions whenever the engine changes. Browser memory and CPU constrain the largest runs; choose 100 or 1,000 customers on mobile. No backend or LLM is used.

## Optional Streamlit deployment
Visit https://share.streamlit.io/ and sign in with GitHub. Create a public app from:
- Repository: denisisikawa/business-science-lab
- Branch: main
- Main file: revenueguard-ai/app.py

Select a free available subdomain. The colocated requirements.txt isolates demo dependencies. Local: cd revenueguard-ai; pip install -r requirements.txt; streamlit run app.py.

## Acceptance test
- Run 100 customers / 12 months / seed 42 / 0%: 2,400 item-months and zero exceptions.
- Run the same at 3.5%: nonzero exceptions, expected minus actual equals underbilling minus overbilling.
- Repeat identical settings: identical outcomes.
- Change filter and inspect evidence; export CSV.
- Review benchmark separately. A perfect result on injected matching rules is not an AI evaluation.
- Public sandbox does not provide arbitrary raw-source downloads; use simulator CLI locally. No AI chat, Telegram or production security claims.

## Financial exposure heatmap and action plan
The browser sandbox includes a bilingual matrix of defect × product or billing period. Each cell sums absolute expected-minus-actual amounts in integer USD cents and counts affected item-period records. Totals never net underbilling against overbilling. Color is scaled to the largest cell in the selected matrix; numbers are always shown. Clicking a cell or plan row filters the investigation list by defect and dimension. CSV export respects the active scope.

The plan sorts nonzero cells by absolute exposure descending, breaking ties by defect and dimension key. P1 includes groups until cumulative exposure reaches at least 80%; P2 covers the rest. P1 coverage may exceed 80% due to indivisible groups. Suggested owners, timeboxes and acceptance checks are rules-based recommendations; they neither estimate actual effort nor establish root cause or recoverable revenue. Remediation requires human approval and verification. Groupings are alternative views of the same exposure, not additive to each other. In the current model exceptions are mutually exclusive at item-period grain.

Acceptance checks: verify heatmap grand total equals underbilling plus overbilling exposure; check row and column totals; confirm that clicking a nonzero cell filters the same defect and product/period; clear the focus; switch language and dimensions; verify P1 covers at least 80% when exposure is positive, and zero-rate scenarios display no remediation groups. No generative AI is used.
