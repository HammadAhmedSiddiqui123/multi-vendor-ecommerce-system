import sys
import os
sys.path.append(os.getcwd())
from database import get_connection

def test():
    conn = get_connection()
    if not conn:
        print("No connection")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    print("--- Warehouses ---")
    cursor.execute("SELECT * FROM Warehouse")
    warehouses = cursor.fetchall()
    print(warehouses)
    
    print("\n--- Products ---")
    cursor.execute("SELECT product_id, product_name, stock, seller_id FROM Product ORDER BY product_id DESC LIMIT 5")
    products = cursor.fetchall()
    print(products)
    
    print("\n--- Inventory ---")
    cursor.execute("SELECT * FROM inventory ORDER BY inventory_id DESC LIMIT 5")
    invs = cursor.fetchall()
    print(invs)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    test()
