from fastapi import FastAPI
from pydantic import BaseModel
from models.optimizer import SmartPackagingOptimizer
from utils.carbon_calculator import CarbonCalculator
from database.db import (
    insert_shipment,
    initialize_db,
    get_inventory,
    adjust_inventory,
    get_shipments,
)
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import timedelta

app = FastAPI()

# ensure database tables exist on startup
@app.on_event("startup")
def startup_event():
    initialize_db()

optimizer = SmartPackagingOptimizer("data/boxes.csv")
carbon_calc = CarbonCalculator("data/material_carbon_data.csv")

class Product(BaseModel):
    length: float
    width: float
    height: float
    weight: float
    fragile: bool = False


@app.post("/optimize")
def optimize_packaging(product: Product):

    result = optimizer.optimize(
        product_length=product.length,
        product_width=product.width,
        product_height=product.height,
        weight=product.weight,
        fragile=product.fragile
    )

    if "error" in result:
        return result

    optimized_volume = (
        result["box_dimensions"][0] *
        result["box_dimensions"][1] *
        result["box_dimensions"][2]
    )

    default_volume = optimized_volume * 1.5

    carbon_result = carbon_calc.calculate(
        optimized_box={"cost_per_box": 25},
        default_box_volume=default_volume,
        optimized_box_volume=optimized_volume
    )

    shipment_data = {
        "product_length": product.length,
        "product_width": product.width,
        "product_height": product.height,
        "weight": product.weight,
        "selected_box": result["selected_box"],
        "waste_percentage": result["waste_percentage"],
        "co2_saved": carbon_result["co2_saved_kg"],
        "cost_saved": carbon_result["cost_saved"],
        "sustainability_score": carbon_result["sustainability_score"]
    }

    insert_shipment(shipment_data)

    # update inventory: reduce stock by 1 and record usage
    adjust_inventory(result["selected_box"], change=-1, record_use=True)

    return {
        "optimization": result,
        "carbon_analysis": carbon_result
    }

@app.get("/inventory")
def inventory_list():
    """Return current inventory status."""
    return {"inventory": get_inventory()}

@app.get("/forecast")
def demand_forecast(weeks: int = 8):
    """Predict next week's box demand using simple linear regression on weekly counts."""
    rows = get_shipments()
    df = pd.DataFrame(rows)
    if df.empty or "created_at" not in df.columns:
        return {"error": "insufficient data"}

    df["created_at"] = pd.to_datetime(df["created_at"])
    # group by week start (Monday)
    weekly = df.groupby([pd.Grouper(key="created_at", freq="W-MON"), "selected_box"]).size().unstack(fill_value=0)
    overall = weekly.sum(axis=1).reset_index(name="count")
    overall["week_num"] = range(len(overall))

    # train on all weeks
    X = overall[["week_num"]]
    y = overall["count"]
    model = LinearRegression()
    model.fit(X, y)
    next_week_num = [[len(overall)]]
    next_overall = int(model.predict(next_week_num)[0])

    # by box
    box_preds = {}
    for box in weekly.columns:
        series = weekly[box].reset_index(name="count")
        series["week_num"] = range(len(series))
        if len(series) >= 2:
            m = LinearRegression().fit(series[["week_num"]], series["count"])
            box_preds[box] = int(m.predict([[len(series)]])[0])
        else:
            box_preds[box] = int(series["count"].iloc[-1] if not series.empty else 0)

    history = overall["count"].tolist()
    return {"overall_next_week": next_overall, "by_box": box_preds, "history": history}


@app.post("/inventory/update")
def inventory_update(box_size: str, change: int):
    """Adjust stock for a box size. Positive change adds stock, negative removes."""
    adjust_inventory(box_size, change=change)
    return {"status": "ok"}