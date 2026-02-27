import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="packaging_user",
        password="Pack@123",
        database="smart_packaging"
    )

def insert_shipment(data):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO shipments
    (product_length, product_width, product_height, weight,
     selected_box, waste_percentage, co2_saved,
     cost_saved, sustainability_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["product_length"],
        data["product_width"],
        data["product_height"],
        data["weight"],
        data["selected_box"],
        data["waste_percentage"],
        data["co2_saved"],
        data["cost_saved"],
        data["sustainability_score"]
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()