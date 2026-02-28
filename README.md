# smart-packaging-optimizer
Smart Packaging Size Optimizer + Waste Analytics Dashboard for Retail

## Development notes

- The frontend is a Streamlit app (`frontend/app.py`) that communicates
  with a FastAPI backend (`backend/app.py`). During local development the
  frontend expects the API to be running at `http://127.0.0.1:8000`.
  
- Clicking **Optimize Packaging** will POST to `/optimize`. If nothing
  happens, verify that the backend is reachable and also ensure the
  `BACKEND_URL` secret (or env var) points to the correct host.

- To override the endpoint (for staging/production) set a secret in
  `.streamlit/secrets.toml`::

    [general]
    BACKEND_URL = "https://smart-packaging-optimizer.onrender.com"


## Getting Started

The repository exposes a small command line interface via `main.py`.

```bash
# interactively prompt for dimensions
python main.py

# run the built-in sample example (no DB insert)
python main.py --sample

# supply explicit values and persist to database
python main.py --length 12 --width 8 --height 4 --weight 1 --fragile
```

When run successfully with real inputs the script will print the
optimization and carbon analysis results and insert a record into the
MySQL database using `database/db.py`.

For development you can also import `run_optimization` from the module and
call it directly from tests or other tooling.

