# Instant CNC RFQ Estimator

Upload almost any STEP/STP solid and get an immediate indicative CNC manufacturing estimate.

## What it does
- reads STEP geometry with Open Cascade
- validates usable solids
- extracts dimensions, volume, surface area and face types
- identifies likely milling/turning/indexed/complex geometry
- estimates stock, material removal, machining time, setups and cost
- supports quantity, material, finish and tolerance inputs
- exports RFQ JSON and customer-friendly HTML

## Run
`pip install -r requirements.txt` then `streamlit run app.py`

The model is geometry-driven rather than tied to one sample part. Parts outside the safe automatic-pricing envelope are flagged for manual engineering review instead of receiving a misleading precise price.

Calibrate `config.json` to your actual machine, labour, tooling, material and finishing costs. This is an indicative estimator, not a binding quotation.
