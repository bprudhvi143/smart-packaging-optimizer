import pandas as pd
import os

class SmartPackagingOptimizer:

    def __init__(self, box_dataset_path):

        # Make path absolute (safer)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, box_dataset_path)

        print("Loading dataset from:", full_path)  # debug line

        self.boxes = pd.read_csv(full_path)

    def optimize(self, product_length, product_width, product_height, weight, fragile=False):

        # Step 1: Add fragility buffer
        if fragile:
            product_length += 2
            product_width += 2
            product_height += 2

        product_volume = product_length * product_width * product_height

        best_box = None
        minimum_empty_space = float('inf')

        for _, box in self.boxes.iterrows():

            # Check fit condition
            if (
                product_length <= box["length_cm"] and
                product_width <= box["width_cm"] and
                product_height <= box["height_cm"] and
                weight <= box["max_weight_kg"]
            ):

                box_volume = (
                    box["length_cm"] *
                    box["width_cm"] *
                    box["height_cm"]
                )

                empty_space = box_volume - product_volume

                if empty_space < minimum_empty_space:
                    minimum_empty_space = empty_space
                    best_box = box

        if best_box is None:
            return {"error": "No suitable box found"}

        waste_percentage = (minimum_empty_space / (
            best_box["length_cm"] *
            best_box["width_cm"] *
            best_box["height_cm"]
        )) * 100

        efficiency_score = 100 - waste_percentage

        return {
            "selected_box": best_box["box_id"],
            "box_dimensions": (
                best_box["length_cm"],
                best_box["width_cm"],
                best_box["height_cm"]
            ),
            "empty_space_cm3": round(minimum_empty_space, 2),
            "waste_percentage": round(waste_percentage, 2),
            "efficiency_score": round(efficiency_score, 2)
        }