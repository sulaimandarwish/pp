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

## Deploy as a private website

This repository is prepared for Streamlit Community Cloud. The intended setup is a **private app**, not a public website.

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Connect your GitHub account with permission to access this repository.
3. Choose **Create app**.
4. Select repository `sulaimandarwish/pp`.
5. Select branch `main`.
6. Set the main file to `app.py`.
7. Choose Python `3.12` in Advanced settings if it is shown.
8. Deploy the app.
9. In the app's **Settings → Sharing**, set **Who can view this app** to **Only specific people can view this app**.
10. Add only the email addresses that should be allowed to use the RFQ tool.

Streamlit Community Cloud supports private apps and private repositories. A private app is not indexed by search engines and viewers must be explicitly authorized. Each Community Cloud workspace can have one private app. The cloud build reads `requirements.txt` for Python packages and `packages.txt` for the Linux dependency required by OpenCascade.

**Important:** the current GitHub repository is public, so the source code is visible on GitHub even when the deployed Streamlit app is private. If you want the source code private too, change the GitHub repository visibility to **Private** before connecting it to Streamlit Community Cloud.

After deployment, Streamlit gives you a `*.streamlit.app` URL. Only authorized viewers can open the private app.

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