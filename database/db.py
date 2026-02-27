import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="packaging_user",
        password="Pack@123",
        database="smart_packaging"
    )

def initialize_db():
    """Create required tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()
    # shipment table assumed to already exist; create inventory if missing
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        box_size VARCHAR(255) PRIMARY KEY,
        stock INT DEFAULT 0,
        usage_count INT DEFAULT 0
    )
    """)
    conn.commit()
    cur.close()
    conn.close()

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


def get_inventory():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT box_size, stock, usage_count FROM inventory")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def adjust_inventory(box_size: str, change: int = 0, record_use: bool = False):
    """Update inventory stock by change and optionally increment usage_count."""
    connection = get_connection()
    cursor = connection.cursor()

    # ensure the row exists
    cursor.execute(
        "INSERT INTO inventory (box_size, stock, usage_count) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE stock = stock, usage_count = usage_count",
        (box_size, 0, 0)
    )

    if change != 0:
        cursor.execute(
            "UPDATE inventory SET stock = stock + %s WHERE box_size = %s",
            (change, box_size)
        )
    if record_use:
        cursor.execute(
            "UPDATE inventory SET usage_count = usage_count + 1 WHERE box_size = %s",
            (box_size,)
        )

    connection.commit()
    cursor.close()
    connection.close()


def get_shipments():
    """Return all shipment rows as list of dicts."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows