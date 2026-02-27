import argparse
from models.optimizer import SmartPackagingOptimizer
from utils.carbon_calculator import CarbonCalculator
from database.db import insert_shipment


# helper function used by both interactive and scripted runs

from pathlib import Path


def run_optimization(product_length: float,
                     product_width: float,
                     product_height: float,
                     weight: float,
                     fragile: bool):
    """Perform optimization and carbon analysis, then persist to database.

    Returns a tuple of (result, carbon_result) where either may contain an
    "error" key if something went wrong.
    """
    # paths are resolved relative to this file so the module can be
    # imported from anywhere in the package.
    base = Path(__file__).parent
    optimizer = SmartPackagingOptimizer(str(base / "data" / "boxes.csv"))
    carbon_calc = CarbonCalculator(str(base / "data" / "material_carbon_data.csv"))

    result = optimizer.optimize(
        product_length=product_length,
        product_width=product_width,
        product_height=product_height,
        weight=weight,
        fragile=fragile,
    )

    carbon_result = None
    if "error" not in result:
        optimized_volume = (
            result["box_dimensions"][0]
            * result["box_dimensions"][1]
            * result["box_dimensions"][2]
        )
        default_volume = optimized_volume * 1.5
        carbon_result = carbon_calc.calculate(
            optimized_box={"cost_per_box": 25},
            default_box_volume=default_volume,
            optimized_box_volume=optimized_volume,
        )

        # persist the shipment to the database
        shipment_data = {
            "product_length": product_length,
            "product_width": product_width,
            "product_height": product_height,
            "weight": weight,
            "selected_box": result.get("selected_box"),
            "waste_percentage": result.get("waste_percentage"),
            "co2_saved": carbon_result.get("co2_saved_kg"),
            "cost_saved": carbon_result.get("cost_saved"),
            "sustainability_score": carbon_result.get("sustainability_score"),
        }
        insert_shipment(shipment_data)

    return result, carbon_result


def main():
    parser = argparse.ArgumentParser(
        description="Run smart packaging optimization and carbon analysis."
    )
    parser.add_argument(
        "--length",
        type=float,
        help="Product length in cm",
    )
    parser.add_argument(
        "--width",
        type=float,
        help="Product width in cm",
    )
    parser.add_argument(
        "--height",
        type=float,
        help="Product height in cm",
    )
    parser.add_argument(
        "--weight",
        type=float,
        help="Product weight in kg",
    )
    parser.add_argument(
        "--fragile",
        action="store_true",
        help="Flag to indicate product is fragile",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run a built-in sample shipment (no database insert).",
    )

    args = parser.parse_args()

    if args.sample:
        # sample values for quick demonstrations
        args.length = 12
        args.width = 8
        args.height = 4
        args.weight = 1
        args.fragile = True

    # if required args are missing and not running sample, switch to interactive
    if not args.sample and (
        args.length is None
        or args.width is None
        or args.height is None
        or args.weight is None
    ):
        print("=" * 50)
        print("Smart Packaging Optimizer – interactive mode")
        print("=" * 50)
        try:
            args.length = float(input("Enter product length (cm): "))
            args.width = float(input("Enter product width (cm): "))
            args.height = float(input("Enter product height (cm): "))
            args.weight = float(input("Enter product weight (kg): "))
            fragile_input = input("Is the product fragile? (yes/no): ").lower().strip()
            args.fragile = fragile_input in ["yes", "y", "true", "1"]
        except ValueError:
            print("Error: Please enter valid numeric values for dimensions and weight.")
            return

    result, carbon_result = run_optimization(
        args.length, args.width, args.height, args.weight, args.fragile
    )

    print("\n" + "=" * 50)
    print("Optimization Result:")
    print("=" * 50)
    print(result)
    if carbon_result:
        print("\n" + "=" * 50)
        print("Carbon Analysis:")
        print("=" * 50)
        print(carbon_result)
        if not args.sample:
            print("\n✅ Data inserted into MySQL successfully!")


if __name__ == "__main__":
    main()

    