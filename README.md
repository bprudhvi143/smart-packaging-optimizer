# smart-packaging-optimizer
Smart Packaging Size Optimizer + Waste Analytics Dashboard for Retail

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

