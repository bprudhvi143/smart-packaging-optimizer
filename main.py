from models.optimizer import SmartPackagingOptimizer

def main():
    print("=" * 50)
    print("Smart Packaging Optimizer")
    print("=" * 50)
    
    optimizer = SmartPackagingOptimizer("data/boxes.csv")
    
    # Get user input for product dimensions
    try:
        product_length = float(input("Enter product length (cm): "))
        product_width = float(input("Enter product width (cm): "))
        product_height = float(input("Enter product height (cm): "))
        weight = float(input("Enter product weight (kg): "))
        
        fragile_input = input("Is the product fragile? (yes/no): ").lower().strip()
        fragile = fragile_input in ['yes', 'y', 'true', '1']
        
        # Run optimization
        result = optimizer.optimize(
            product_length=product_length,
            product_width=product_width,
            product_height=product_height,
            weight=weight,
            fragile=fragile
        )
        
        print("\n" + "=" * 50)
        print("Optimization Result:")
        print("=" * 50)
        print(result)
        
    except ValueError:
        print("Error: Please enter valid numeric values for dimensions and weight.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()