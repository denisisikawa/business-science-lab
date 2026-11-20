# External testing

## Browser sandbox
https://denisisikawa.github.io/denis-isikawa-databricks/revenueguard-sandbox/

The standalone GitHub Pages experiment runs the Python generator and reconciliation engine via Pyodide 0.27.7. It is deliberately unlinked from the portfolio landing page and uses a noindex directive (not access control). Requires network access to jsDelivr on initial load. The HTML embeds snapshots of simulator.py and sandbox_engine.py; regenerate those definitions whenever the engine changes. Browser memory and CPU constrain the largest runs; choose 100 or 1,000 customers on mobile. No backend or LLM is used.

## Optional Streamlit deployment
Visit https://share.streamlit.io/ and sign in with GitHub. Create a public app from:
- Repository: denisisikawa/denis-isikawa-databricks
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
