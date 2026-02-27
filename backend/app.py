from fastapi import FastAPI
from pydantic import BaseModel
from models.optimizer import SmartPackagingOptimizer
from utils.carbon_calculator import CarbonCalculator
from database.db import insert_shipment, initialize_db, get_inventory, adjust_inventory

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


@app.post("/inventory/update")
def inventory_update(box_size: str, change: int):
    """Adjust stock for a box size. Positive change adds stock, negative removes."""
    adjust_inventory(box_size, change=change)
    return {"status": "ok"}