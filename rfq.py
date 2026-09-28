import json,html
def rfq_json(data): return json.dumps(data,indent=2)
def rfq_html(data,symbol):
    e=data["estimate"]; g=data["geometry"]
    rows="".join(f"<tr><td>{html.escape(k)}</td><td>{symbol}{v:,.2f}</td></tr>" for k,v in e["cost_rows"].items())
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{data['reference']}</title>
    <style>body{{font:16px Arial;max-width:900px;margin:40px auto;color:#222}}.card{{border:1px solid #ddd;padding:18px;margin:14px 0;border-radius:10px}}.price{{font-size:32px;font-weight:bold}}table{{width:100%;border-collapse:collapse}}td{{padding:8px;border-bottom:1px solid #ddd}}</style></head>
    <body><h1>Instant CNC RFQ Estimate</h1><p>{data['reference']} · {data['created']}</p>
    <div class='card'><b>Part:</b> {html.escape(data['part'])}<br><b>Quantity:</b> {data['quantity']}<br><b>Material:</b> {html.escape(data['material'])}<br><b>Finish:</b> {html.escape(data['finish'])}<br><b>Tolerance:</b> {html.escape(data['tolerance'])}</div>
    <div class='card'><div class='price'>{symbol}{e['price_unit']:,.2f} / part</div><p>{symbol}{e['price_batch']:,.2f} total</p><p>Indicative range: {symbol}{e['range_low']:,.2f}–{symbol}{e['range_high']:,.2f} / part</p></div>
    <div class='card'><h2>Geometry</h2><p>Route: {html.escape(g['route'])}</p><p>Dimensions: {' × '.join(f'{x:.1f}' for x in g['dimensions_mm'])} mm</p><p>Volume: {g['volume_mm3']:,.0f} mm³ · Surface: {g['surface_area_mm2']:,.0f} mm²</p></div>
    <div class='card'><h2>Cost breakdown</h2><table>{rows}</table></div>
    <div class='card'><b>Important:</b> indicative automated estimate only. Engineering review is required before a binding quotation.</div></body></html>"""
