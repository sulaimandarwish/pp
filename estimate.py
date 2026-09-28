import math

def estimate(g,p,qty):
    dims=[x+2*p["stock_allowance_mm"] for x in g["dimensions_mm"]]
    if max(dims)>p["max_dimension_mm"]: raise ValueError("Part exceeds configured machine/stock envelope.")
    stock=math.prod(dims); removed=max(0,stock-g["volume_mm3"])
    rough=removed/p["mrr_mm3_min"]
    finish=g["surface_area_mm2"]*p["finish_surface_fraction"]/(p["finish_stepover_mm"]*p["finish_feed_mm_min"])
    complexity=1+min(.30,g["face_counts"].get("complex",0)*.01)
    machine=(rough+finish)*complexity+p["handling_min_part"]*g["assumed_setups"]+p["tool_rapid_min_part"]
    setup=g["assumed_setups"]*p["setup_min"]; programming=p["programming_min"]
    blank_kg=stock*p["density_kg_mm3"]
    rows={"Material + blank":qty*(blank_kg*p["material_cost_per_kg"]+p["blank_cut_cost"]),
          "Programming":programming/60*p["programming_cost_hour"],
          "Setup":setup/60*p["setup_cost_hour"],
          "Machining":qty*machine/60*p["machine_cost_hour"],
          "Inspection":qty*p["inspection_min_part"]/60*p["inspection_cost_hour"],
          "Consumables":qty*p["consumables_part"],
          "External finish":qty*p["external_finish_part"]}
    base=sum(rows.values()); total=max(p["minimum_order"],base/(1-p["margin"]))
    unit=total/qty
    return {"price_unit":round(unit,2),"price_batch":round(total,2),"cost_batch":round(base,2),
            "cost_rows":{k:round(v,2) for k,v in rows.items()},"machine_cycle_min_part":round(machine,1),
            "production_hours_batch":round((setup+qty*(machine+p["inspection_min_part"]))/60,1),
            "programming_min":programming,"setups":g["assumed_setups"],
            "range_low":round(unit*(1-p["sensitivity"]),2),"range_high":round(unit*(1+p["sensitivity"]),2)}
