import sys
import os
sys.path.append(os.getcwd())
from database import get_connection, add_product

def test():
    print("Testing add_product...")
    res = add_product(2, "Test Watch", "Test Desc", 99.99, 1, "Electronics")
    print("Result:", res)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product ORDER BY product_id DESC LIMIT 1")
    print("Product:", cursor.fetchone())
    
    cursor.execute("SELECT * FROM inventory ORDER BY inventory_id DESC LIMIT 1")
    print("Inventory:", cursor.fetchone())
    
if __name__ == '__main__':
    test()
