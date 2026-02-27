# utils/carbon_calculator.py

import pandas as pd

class CarbonCalculator:

    def __init__(self, material_dataset_path):
        self.material_data = pd.read_csv(material_dataset_path)

    def calculate(self, optimized_box, default_box_volume, optimized_box_volume):

        # Approximate cardboard weight
        cardboard_density = 0.0007  # kg per cubic cm

        default_weight = default_box_volume * cardboard_density
        optimized_weight = optimized_box_volume * cardboard_density

        weight_saved = default_weight - optimized_weight

        # Get CO2 factor for cardboard
        co2_factor = self.material_data[
            self.material_data["material_type"] == "cardboard"
        ]["co2_per_kg_kg"].values[0]

        co2_saved = weight_saved * co2_factor

        # Cost difference
        default_cost = optimized_box["cost_per_box"] * 1.5  # simulate oversized
        optimized_cost = optimized_box["cost_per_box"]

        cost_saved = default_cost - optimized_cost

        sustainability_score = min(100, (co2_saved * 10))

        return {
            "weight_saved_kg": round(weight_saved, 4),
            "co2_saved_kg": round(co2_saved, 4),
            "cost_saved": round(cost_saved, 2),
            "sustainability_score": round(sustainability_score, 2)
        }