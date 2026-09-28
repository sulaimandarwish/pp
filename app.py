import hashlib
import json
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

from estimate import estimate
from geometry import analyse_step
from rfq import rfq_html, rfq_json

st.set_page_config(
    page_title="Instant CNC RFQ",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.2rem 1.4rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 16px;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin: 0 0 .35rem 0;}
    .hero p {margin: 0; opacity: .8;}
    .badge {
        display: inline-block;
        padding: .25rem .6rem;
        border-radius: 999px;
        border: 1px solid rgba(128,128,128,.3);
        font-size: .82rem;
        margin-right: .35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ROOT = Path(__file__).parent
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

st.markdown(
    """
    <div class="hero">
      <h1>⚙️ Instant CNC RFQ Estimator</h1>
      <p>STEP → geometry analysis → manufacturability screen → indicative CNC price → RFQ export</p>
      <div style="margin-top:.8rem">
        <span class="badge">No paid API</span>
        <span class="badge">No database</span>
        <span class="badge">Free Streamlit hosting</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("RFQ inputs")
    part = st.text_input("Part number", "STEP-PART")
    qty = int(st.number_input("Quantity", min_value=1, max_value=100000, value=10, step=1))
    material = st.selectbox(
        "Material",
        [
            "Aluminium 6061",
            "Aluminium 7075",
            "Mild Steel",
            "Stainless Steel 304",
            "Custom",
        ],
    )
    finish = st.selectbox(
        "Finish",
        ["As machined", "Deburr + clean", "Anodised", "Powder coated", "Custom"],
    )
    tolerance = st.selectbox(
        "Tolerance",
        ["Standard ±0.10 mm", "Precision ±0.05 mm", "Tight ±0.02 mm", "Custom"],
    )
    currency = st.selectbox("Currency", ["GBP", "EUR", "USD", "SAR"])

    if material == "Custom":
        material = st.text_input("Custom material", "Custom")
    if finish == "Custom":
        finish = st.text_input("Custom finish", "Special finish")
    if tolerance == "Custom":
        tolerance = st.text_input("Custom tolerance", "Customer specified")

    st.divider()
    st.caption("Hosting target: Streamlit Community Cloud")
    st.caption("Website software cost: £0 on the free Community Cloud tier.")

up = st.file_uploader(
    "Upload a STEP/STP part",
    type=["step", "stp"],
    help="Upload one manufacturable solid at a time. Maximum upload size is 200 MB.",
)

if not up:
    st.info(
        "Upload a STEP/STP file to begin. The estimator analyses each uploaded part dynamically; "
        "it is not tied to one sample geometry."
    )
    st.stop()

try:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / up.name
        path.write_bytes(up.getvalue())
        geometry = analyse_step(path)
except Exception as ex:
    st.error(f"STEP analysis failed: {ex}")
    st.stop()

st.success("STEP geometry loaded and analysed.")

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "Size",
    " × ".join(f"{x:.1f}" for x in geometry["dimensions_mm"]) + " mm",
)
m2.metric("Volume", f"{geometry['volume_mm3']:,.0f} mm³")
m3.metric("Surface", f"{geometry['surface_area_mm2']:,.0f} mm²")
m4.metric("Route", geometry["route"])

st.subheader("Geometry & manufacturability")
st.write(
    f"Faces: {geometry['face_counts']} · "
    f"Cylinder axis groups: {geometry['cylinder_axis_groups']} · "
    f"Assumed setups: {geometry['assumed_setups']}"
)

if not geometry["estimate_allowed"]:
    st.warning("This geometry is outside the safe automatic-pricing envelope.")
    for reason in geometry["review_reasons"]:
        st.write("• " + reason)
    st.info(
        "The application intentionally refuses to invent a precise price for unsupported geometry. "
        "The same STEP analysis can later feed a process-specific CAM pricing model."
    )
    st.stop()

params = dict(cfg)
if material.startswith("Aluminium"):
    params["density_kg_mm3"] = 0.0000027
elif material.startswith("Stainless"):
    params["density_kg_mm3"] = 0.000008
elif material.startswith("Mild"):
    params["density_kg_mm3"] = 0.00000785

try:
    result = estimate(geometry, params, qty)
except Exception as ex:
    st.error(f"Estimate calculation failed: {ex}")
    st.stop()

symbol = {"GBP": "£", "EUR": "€", "USD": "$", "SAR": "SAR "}[currency]

st.subheader("Instant estimate")
x1, x2, x3, x4 = st.columns(4)
x1.metric("Unit price", f"{symbol}{result['price_unit']:,.2f}")
x2.metric("Order total", f"{symbol}{result['price_batch']:,.2f}")
x3.metric("Cycle / part", f"{result['machine_cycle_min_part']:.1f} min")
x4.metric("Production", f"{result['production_hours_batch']:.1f} h")

st.success(
    f"{qty} × {part}: indicative total {symbol}{result['price_batch']:,.2f}"
)

left, right = st.columns(2)
with left:
    st.subheader("Cost breakdown")
    st.table(
        [
            {"Item": key, "Cost": f"{symbol}{value:,.2f}"}
            for key, value in result["cost_rows"].items()
        ]
    )

with right:
    st.subheader("RFQ assumptions")
    st.write(f"Material: **{material}**")
    st.write(f"Finish: **{finish}**")
    st.write(f"Tolerance: **{tolerance}**")
    st.write(
        f"Price range: **{symbol}{result['range_low']:,.2f}–"
        f"{symbol}{result['range_high']:,.2f} / part**"
    )
    st.caption(
        "The range reflects pricing uncertainty; it is not a statistical confidence interval."
    )

reference = "RFQ-" + hashlib.sha256(up.getvalue()).hexdigest()[:10].upper()
data = {
    "reference": reference,
    "created": date.today().isoformat(),
    "part": part,
    "quantity": qty,
    "material": material,
    "finish": finish,
    "tolerance": tolerance,
    "source_file": up.name,
    "geometry": geometry,
    "estimate": result,
}

st.subheader("RFQ export")
q1, q2 = st.columns(2)
with q1:
    st.download_button(
        "Download RFQ JSON",
        rfq_json(data),
        "rfq.json",
        "application/json",
        use_container_width=True,
    )
with q2:
    st.download_button(
        "Download RFQ HTML",
        rfq_html(data, symbol),
        "rfq.html",
        "text/html",
        use_container_width=True,
    )

with st.expander("What this cannot prove from STEP alone"):
    for limitation in geometry["limitations"]:
        st.write("• " + limitation)
