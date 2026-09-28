import hashlib,json,tempfile
from pathlib import Path
from datetime import date
import streamlit as st
from geometry import analyse_step
from estimate import estimate
from rfq import rfq_json,rfq_html

st.set_page_config(page_title="Instant CNC RFQ",page_icon="⚙️",layout="wide")
st.title("⚙️ Instant CNC RFQ Estimator")
st.caption("STEP → geometry → manufacturability screen → instant indicative price → RFQ")
ROOT=Path(__file__).parent
cfg=json.loads((ROOT/"config.json").read_text())
with st.sidebar:
    st.header("Order")
    part=st.text_input("Part number","STEP-PART")
    qty=int(st.number_input("Quantity",1,100000,10))
    material=st.selectbox("Material",["Aluminium 6061","Aluminium 7075","Mild Steel","Stainless Steel 304","Custom"])
    finish=st.selectbox("Finish",["As machined","Deburr + clean","Anodised","Powder coated","Custom"])
    tolerance=st.selectbox("Tolerance",["Standard ±0.10 mm","Precision ±0.05 mm","Tight ±0.02 mm","Custom"])
    currency=st.selectbox("Currency",["GBP","EUR","USD","SAR"])
    if material=="Custom": material=st.text_input("Custom material","Custom")
    if finish=="Custom": finish=st.text_input("Custom finish","Special finish")
    if tolerance=="Custom": tolerance=st.text_input("Custom tolerance","Customer specified")
up=st.file_uploader("Upload a STEP/STP part",type=["step","stp"])
if not up:
    st.info("Upload a STEP file to begin. The estimator analyses each part dynamically; it is not limited to one sample geometry.")
    st.stop()
try:
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/up.name
        p.write_bytes(up.getvalue())
        g=analyse_step(p)
except Exception as ex:
    st.error(str(ex)); st.stop()

a,b,c,d=st.columns(4)
a.metric("Size"," × ".join(f"{x:.1f}" for x in g["dimensions_mm"])+" mm")
b.metric("Volume",f"{g['volume_mm3']:,.0f} mm³")
c.metric("Surface",f"{g['surface_area_mm2']:,.0f} mm²")
d.metric("Route",g["route"])

st.subheader("Geometry & manufacturability")
st.write(f"Faces: {g['face_counts']} · Cylinder axis groups: {g['cylinder_axis_groups']} · Assumed setups: {g['assumed_setups']}")
if not g["estimate_allowed"]:
    st.warning("This geometry is outside the safe automatic-pricing envelope.")
    for x in g["review_reasons"]: st.write("• "+x)
    st.info("The application intentionally refuses to invent a precise price for unsupported geometry. Add a process-specific model later and the same STEP analysis can feed it.")
    st.stop()

params=dict(cfg)
if material.startswith("Aluminium"): params["density_kg_mm3"]=0.0000027
elif material.startswith("Stainless"): params["density_kg_mm3"]=0.000008
elif material.startswith("Mild"): params["density_kg_mm3"]=0.00000785
try: e=estimate(g,params,qty)
except Exception as ex: st.error(str(ex)); st.stop()

sym={"GBP":"£","EUR":"€","USD":"$","SAR":"SAR "}[currency]
st.subheader("Instant estimate")
x1,x2,x3,x4=st.columns(4)
x1.metric("Unit",f"{sym}{e['price_unit']:,.2f}")
x2.metric("Order",f"{sym}{e['price_batch']:,.2f}")
x3.metric("Cycle / part",f"{e['machine_cycle_min_part']:.1f} min")
x4.metric("Production",f"{e['production_hours_batch']:.1f} h")
st.success(f"{qty} × {part}: indicative total {sym}{e['price_batch']:,.2f}")
l,r=st.columns(2)
with l:
    st.subheader("Cost breakdown")
    st.table([{"Item":k,"Cost":f"{sym}{v:,.2f}"} for k,v in e["cost_rows"].items()])
with r:
    st.subheader("Assumptions")
    st.write(f"Material: **{material}**")
    st.write(f"Finish: **{finish}**")
    st.write(f"Tolerance: **{tolerance}**")
    st.write(f"Price range: **{sym}{e['range_low']:,.2f}–{sym}{e['range_high']:,.2f} / part**")
    st.write("The range reflects pricing uncertainty; it is not a statistical confidence interval.")

ref="RFQ-"+hashlib.sha256(up.getvalue()).hexdigest()[:10].upper()
data={"reference":ref,"created":date.today().isoformat(),"part":part,"quantity":qty,"material":material,"finish":finish,"tolerance":tolerance,"source_file":up.name,"geometry":g,"estimate":e}
st.subheader("RFQ export")
q1,q2=st.columns(2)
with q1: st.download_button("Download RFQ JSON",rfq_json(data),"rfq.json","application/json",use_container_width=True)
with q2: st.download_button("Download RFQ HTML",rfq_html(data,sym),"rfq.html","text/html",use_container_width=True)
with st.expander("What this cannot prove from STEP alone"):
    for x in g["limitations"]: st.write("• "+x)
