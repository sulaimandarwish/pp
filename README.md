# Instant CNC RFQ Estimator

Upload a STEP/STP solid and get an immediate indicative CNC manufacturing estimate.

## What it does

- reads STEP geometry with Open Cascade
- validates usable solids
- extracts dimensions, volume, surface area and face types
- identifies likely milling/turning/indexed/complex geometry
- estimates stock, material removal, machining time, setups and cost
- supports quantity, material, finish and tolerance inputs
- exports RFQ JSON and customer-friendly HTML

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal, normally `http://localhost:8501`.

## Deploy as a live website

This repository is prepared for Streamlit Community Cloud.

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app**.
3. Select repository **sulaimandarwish/pp**.
4. Select branch **main**.
5. Set the main file to **app.py**.
6. Open **Advanced settings** and select **Python 3.12**.
7. Click **Deploy**.

The cloud build reads `requirements.txt` for Python packages and `packages.txt` for the Linux dependency required by OpenCascade. The Streamlit configuration is in `.streamlit/config.toml`.

After deployment, Streamlit gives you a public `*.streamlit.app` URL. Opening that URL shows the actual RFQ interface rather than the GitHub source files.

## Using the estimator

1. Enter the part number, quantity, material, finish, tolerance and currency.
2. Upload a `.step` or `.stp` file.
3. The app analyses the geometry dynamically.
4. Supported geometry gets an indicative unit price, order total, cycle time, production time and cost breakdown.
5. Download the generated RFQ as JSON or HTML.

Parts outside the safe automatic-pricing envelope are deliberately flagged for engineering review rather than receiving a misleading precise price.

## Pricing model

The estimator uses `config.json` for material, machining, setup, programming, inspection, consumables, finishing, margin and uncertainty assumptions. Calibrate these values to your own machines, labour rates, tooling and material costs before using the output for commercial decisions.

## Important limitations

STEP geometry alone does not prove:

- tolerances
- threads
- tool accessibility
- fixturing/workholding
- stock availability
- actual CAM toolpaths
- collision-free machining
- final inspection requirements

This is an **indicative automated estimate**, not a binding quotation.