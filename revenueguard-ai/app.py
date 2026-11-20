import csv
import io
import pandas as pd
import streamlit as st
from sandbox_engine import run_scenario

st.set_page_config(page_title="RevenueGuard AI Sandbox", page_icon="🛡️", layout="wide")
st.title("RevenueGuard AI | Sandbox")
st.caption("Experimental · synthetic B2B financial records · USD · no generative AI in this release")
with st.sidebar:
    st.header("Simulation")
    customers = st.select_slider("Customers", options=[100, 500, 1000, 5000, 10000], value=1000)
    months = st.slider("Months", 1, 12, 12)
    seed = st.number_input("Seed", min_value=0, max_value=999999, value=42)
    rate = st.slider("Injected anomaly rate (%)", 0.0, 15.0, 3.5, .5)
    go = st.button("Run reconciliation", type="primary")
if go or "scenario" not in st.session_state:
    with st.spinner("Generating source records and reconciling..."):
        st.session_state.scenario = run_scenario(customers, months, seed, rate/100)
        st.session_state.config = (customers, months, seed, rate)
r = st.session_state.scenario
st.caption(f"Active run: {st.session_state.config}")
def money(x): return f"${x/100:,.2f}"
cols = st.columns(4)
for c, title, k in zip(cols, ["Expected billing","Actual billing","Underbilling exposure","Overbilling exposure"], ["expected","actual","under","over"]):
    c.metric(title, money(r[k]))
st.write(f"{r['events']:,} item-months checked · {len(r['rows']):,} exceptions")
overview, cases, benchmark, sources = st.tabs(["Overview", "Investigation", "Benchmark", "Data explorer"])
with overview:
    df = pd.DataFrame(r["monthly"]).set_index("period") / 100
    st.line_chart(df)
with cases:
    kind = st.selectbox("Defect", ["ALL","MISSING_BILLING","UNDERBILLING","OVERBILLING"])
    query = st.text_input("Contract or item ID")
    matches = [x for x in r["rows"] if (kind=="ALL" or x["defect"]==kind) and query.upper() in (x["contract"]+" "+x["item"]).upper()]
    st.caption("Amounts in integer USD cents. Sorted by absolute exposure.")
    st.dataframe(pd.DataFrame(matches), use_container_width=True)
    if matches:
        selected = st.selectbox("Inspect evidence", range(min(len(matches), 1000)), format_func=lambda i: matches[i]["item"]+" / "+matches[i]["period"])
        st.json(matches[selected])
        st.download_button("Download filtered exceptions CSV", pd.DataFrame(matches).to_csv(index=False), "exceptions.csv", "text/csv")
with benchmark:
    b = r["benchmark"]
    st.write({k: v for k, v in b.items()})
    st.info("Ground truth is used only after detection. These seeded rules-aligned cases do not establish production or AI accuracy.")
with sources:
    st.dataframe(pd.DataFrame(list(r["counts"].items()), columns=["Dataset","Rows"]), use_container_width=True)
    st.caption("Raw source export is available via the local simulator CLI; public demo exports exceptions.")
