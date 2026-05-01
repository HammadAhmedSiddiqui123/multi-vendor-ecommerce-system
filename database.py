import mysql.connector
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables from .env file
load_dotenv()

def get_connection():
    """
    Creates and returns a connection to the MySQL database
    using credentials from the .env file.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def validate_login(email, password):
    conn = get_connection()
    if not conn: return None
    try:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT user_id, name, email, role
            FROM Users
            WHERE email = %s AND password = %s AND is_active = 1
        """
        cursor.execute(query, (email, hashed_pw))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        print(f"Error during login validation: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def register_user(name, email, password, role):
    conn = get_connection()
    if not conn: return False
    try:
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor = conn.cursor(buffered=True)
        query = """
            INSERT INTO Users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_pw, role))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error during user registration: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_or_create_customer(user_id, name, email):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT customer_id FROM customer WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        if res:
            return res['customer_id']
        
        # Create customer profile
        cursor.execute("INSERT INTO customer (user_id, full_name, email, phone) VALUES (%s, %s, %s, '0000000000')", 
                      (user_id, name, email))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(e)
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_products(search_query="", category="All"):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT p.product_id, p.product_name, p.price, p.stock, c.category_name, s.shop_name AS seller
            FROM Product p
            LEFT JOIN Category c USING (category_id)
            LEFT JOIN Seller s USING (seller_id)
            WHERE p.status = 'active'
        """
        params = []
        if search_query:
            query += " AND p.product_name LIKE %s"
            params.append(f"%{search_query}%")
        if category != "All":
            query += " AND c.category_name = %s"
            params.append(category)
            
        query += " ORDER BY p.created_at DESC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_categories():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT category_name FROM category")
        return [row['category_name'] for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_product_details(product_id):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT p.product_id, p.product_name, p.description, p.price, p.stock,
                   b.brand_name, c.category_name, sc.subcategory_name, pi.image_url
            FROM Product p
            LEFT JOIN Brand b USING(brand_id)       
            LEFT JOIN Category c USING(category_id) 
            LEFT JOIN Sub_Category sc USING(subcategory_id) 
            LEFT JOIN ProductImage pi ON p.product_id = pi.product_id AND pi.is_primary = 1
            WHERE p.product_id = %s
        """
        cursor.execute(query, (product_id,))
        return cursor.fetchone()
    except Exception as e:
        print(e)
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_product_reviews(product_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT r.rating_value, r.comment, r.review_date, c.full_name as customer_name
            FROM Review r
            JOIN Customer c USING(customer_id)
            WHERE r.product_id = %s
            ORDER BY r.review_date DESC
        """
        cursor.execute(query, (product_id,))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_customer_orders(customer_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT o.order_id, o.total_amount, o.status AS order_status, o.order_date,
                   pay.status AS payment_status, sh.status AS shipment_status, sh.tracking_code,
                   ua.label AS address_label, ua.street AS address_street, ua.city AS address_city
            FROM `Order` o
            LEFT JOIN Payment pay USING(order_id)
            LEFT JOIN Shipment sh USING(order_id)
            LEFT JOIN UserAddress ua USING(address_id)
            WHERE o.customer_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (customer_id,))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_order_items(order_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT p.product_name, oi.quantity, oi.unit_price, oi.subtotal, s.shop_name AS seller_name
            FROM OrderItem oi
            JOIN Product p USING(product_id)
            JOIN Seller s USING(seller_id)
            WHERE oi.order_id = %s
        """
        cursor.execute(query, (order_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching order items: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_cart_items(customer_id):
    conn = get_connection()
    if not conn: return [], None
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT cart_id FROM cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
            conn.commit()
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['cart_id']

        query = """
            SELECT ci.cart_item_id, ci.product_id, ci.quantity, p.product_name, p.price, p.stock
            FROM CartItem ci
            JOIN Product p USING(product_id)
            WHERE ci.cart_id = %s
        """
        cursor.execute(query, (cart_id,))
        return cursor.fetchall(), cart_id
    except Exception as e:
        print(e)
        return [], None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_to_cart(customer_id, product_id, quantity=1):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT cart_id FROM cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
            conn.commit()
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['cart_id']
            
        cursor.execute("SELECT cart_item_id, quantity FROM CartItem WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))
        item = cursor.fetchone()
        
        if item:
            cursor.execute("UPDATE CartItem SET quantity = quantity + %s WHERE cart_item_id = %s", (quantity, item['cart_item_id']))
        else:
            cursor.execute("INSERT INTO CartItem (cart_id, product_id, quantity) VALUES (%s, %s, %s)", (cart_id, product_id, quantity))
        
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def remove_from_cart(cart_item_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("DELETE FROM CartItem WHERE cart_item_id = %s", (cart_item_id,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_or_create_seller(user_id, name):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT seller_id FROM seller WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        if res:
            return res['seller_id']
        
        # Create seller profile
        cursor.execute("INSERT INTO seller (user_id, shop_name, phone, address) VALUES (%s, %s, '0000000000', 'Not Provided')", 
                      (user_id, name + "'s Shop"))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(e)
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_seller_stats(seller_id):
    conn = get_connection()
    if not conn: return {"total_orders": 0, "total_revenue": 0}
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT COUNT(DISTINCT o.order_id) AS total_orders,
                   COALESCE(SUM(oi.subtotal), 0) AS total_revenue
            FROM Product p
            JOIN OrderItem oi ON p.product_id = oi.product_id
            JOIN `Order` o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s AND o.status = 'delivered'
        """
        cursor.execute(query, (seller_id,))
        return cursor.fetchone()
    except Exception as e:
        print(e)
        return {"total_orders": 0, "total_revenue": 0}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_seller_products(seller_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT p.product_id, p.product_name, p.price, p.stock, p.status, c.category_name
            FROM Product p
            LEFT JOIN Category c USING(category_id)
            WHERE p.seller_id = %s AND p.status != 'inactive'
            ORDER BY p.created_at DESC
        """
        cursor.execute(query, (seller_id,))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_product(seller_id, name, description, price, stock, category_name):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        
        # Check if product name already exists for this seller
        cursor.execute("SELECT product_id FROM Product WHERE seller_id = %s AND product_name = %s AND status != 'inactive'", (seller_id, name))
        if cursor.fetchone():
            return "exists"
            
        # Get category_id
        cursor.execute("SELECT category_id FROM category WHERE category_name = %s", (category_name,))
        cat = cursor.fetchone()
        category_id = cat['category_id'] if cat else None
        
        query = """
            INSERT INTO Product (seller_id, category_id, product_name, description, price, stock, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'active')
        """
        cursor.execute(query, (seller_id, category_id, name, description, price, stock))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_product(product_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        if e.errno == 1451: # Cannot delete or update a parent row: a foreign key constraint fails
            try:
                cursor.execute("UPDATE Product SET status = 'inactive' WHERE product_id = %s", (product_id,))
                conn.commit()
                return True
            except Exception as inner_e:
                print(inner_e)
                return False
        print(e)
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_seller_orders(seller_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT o.order_id, o.order_date, o.status AS order_status, 
                   p.product_name, oi.quantity, oi.subtotal, c.full_name AS customer_name
            FROM OrderItem oi
            JOIN Product p USING(product_id)
            JOIN `Order` o USING(order_id)
            JOIN Customer c USING(customer_id)
            WHERE p.seller_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (seller_id,))
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_users():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT user_id, name, email, role, created_at FROM Users WHERE is_active = 1 ORDER BY created_at DESC")
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_user(user_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        if e.errno == 1451:
            try:
                cursor.execute("UPDATE Users SET is_active = 0 WHERE user_id = %s", (user_id,))
                conn.commit()
                return True
            except Exception as inner_e:
                print(inner_e)
                return False
        print(e)
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_orders():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT o.order_id, o.order_date, c.full_name, o.total_amount, o.status
            FROM `Order` o
            JOIN Customer c USING(customer_id)
            ORDER BY o.order_date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_monthly_revenue():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT YEAR(o.order_date) AS year, MONTH(o.order_date) AS month,
                   COUNT(o.order_id) AS total_orders, SUM(o.total_amount) AS monthly_revenue
            FROM `Order` o
            WHERE o.status = 'delivered'
            GROUP BY YEAR(o.order_date), MONTH(o.order_date)
            ORDER BY year ASC, month ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_daily_revenue():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT DATE(o.order_date) AS order_day,
                   COUNT(o.order_id) AS total_orders,
                   SUM(o.total_amount) AS daily_revenue
            FROM `Order` o
            GROUP BY DATE(o.order_date)
            ORDER BY order_day ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_coupons():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT * FROM Coupon ORDER BY end_date DESC")
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_coupon(code, discount_type, discount_value, min_order, max_uses, start_date, end_date):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            INSERT INTO Coupon (code, discount_type, discount_value, min_order_amount, max_uses, start_date, end_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """
        cursor.execute(query, (code, discount_type, discount_value, min_order, max_uses, start_date, end_date))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def validate_purchase_for_review(customer_id, product_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT o.order_id 
            FROM `Order` o
            JOIN OrderItem oi USING(order_id)
            WHERE o.customer_id = %s AND oi.product_id = %s AND o.status = 'delivered'
        """
        cursor.execute(query, (customer_id, product_id))
        return cursor.fetchone() is not None
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def submit_review(customer_id, product_id, rating, comment):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            INSERT INTO Review (product_id, customer_id, rating_value, comment)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (product_id, customer_id, rating, comment))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def validate_coupon(code, cart_total):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT coupon_id, discount_type, discount_value, min_order_amount 
            FROM Coupon 
            WHERE code = %s 
              AND is_active = 1 
              AND start_date <= NOW() 
              AND end_date >= NOW()
              AND (max_uses IS NULL OR used_count < max_uses)
        """
        cursor.execute(query, (code,))
        coupon = cursor.fetchone()
        
        if not coupon:
            return {"valid": False, "msg": "Invalid or expired coupon."}
        
        if float(cart_total) < float(coupon['min_order_amount']):
            return {"valid": False, "msg": f"Minimum order amount is ${float(coupon['min_order_amount']):.2f}"}
            
        discount_amount = 0
        if coupon['discount_type'] == 'percentage':
            discount_amount = float(cart_total) * (float(coupon['discount_value']) / 100.0)
        else:
            discount_amount = float(coupon['discount_value'])
            
        return {
            "valid": True, 
            "discount_amount": discount_amount,
            "new_total": float(cart_total) - discount_amount,
            "coupon_id": coupon['coupon_id']
        }
    except Exception as e:
        print(f"Coupon DB Error: {e}")
        return {"valid": False, "msg": f"Database error: {str(e)}"}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ─── Address Management ────────────────────────────────────────────

def get_customer_addresses(user_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT address_id, label, street, city, postal_code
            FROM UserAddress
            WHERE user_id = %s
            ORDER BY address_id ASC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Get Addresses Error: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_address(user_id, label, street, city, postal_code):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            INSERT INTO UserAddress (user_id, label, street, city, postal_code)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, label, street, city, postal_code))
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Address Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_address(address_id, user_id, label, street, city, postal_code):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            UPDATE UserAddress
            SET label = %s, street = %s, city = %s, postal_code = %s
            WHERE address_id = %s AND user_id = %s
        """
        cursor.execute(query, (label, street, city, postal_code, address_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Address Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_address(address_id, user_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        # Prevent deleting if it's used in an existing order
        cursor.execute("SELECT order_id FROM `Order` WHERE address_id = %s LIMIT 1", (address_id,))
        if cursor.fetchone():
            return "in_use"
        cursor.execute("DELETE FROM UserAddress WHERE address_id = %s AND user_id = %s", (address_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete Address Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def process_checkout(customer_id, cart_id, total_amount, coupon_id=None, address_id=None):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        conn.start_transaction()
        
        # 0. Resolve the shipping address
        if not address_id:
            # Check if user has any address
            cursor.execute("SELECT user_id FROM Customer WHERE customer_id = %s", (customer_id,))
            user_row = cursor.fetchone()
            if not user_row:
                conn.rollback()
                return False
            user_id = user_row['user_id']
            cursor.execute("SELECT address_id FROM UserAddress WHERE user_id = %s LIMIT 1", (user_id,))
            addr = cursor.fetchone()
            if not addr:
                # No address found and none provided, fail checkout
                conn.rollback()
                return False
            address_id = addr['address_id']
        
        # 1. Get Cart Items
        cursor.execute("""
            SELECT ci.product_id, ci.quantity, p.price, p.stock 
            FROM CartItem ci 
            JOIN Product p USING(product_id) 
            WHERE ci.cart_id = %s
        """, (cart_id,))
        items = cursor.fetchall()
        
        if not items:
            conn.rollback()
            return False
            
        # Calculate subtotal explicitly
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        discount_amount = float(subtotal) - float(total_amount)
        if discount_amount < 0: discount_amount = 0
            
        # 2. Check stock manually just in case
        for item in items:
            if item['stock'] < item['quantity']:
                conn.rollback()
                return False
                
        # 3. Create Order
        cursor.execute("""
            INSERT INTO `Order` (customer_id, address_id, coupon_id, status, subtotal, discount_amount, total_amount, order_date)
            VALUES (%s, %s, %s, 'pending', %s, %s, %s, NOW())
        """, (customer_id, address_id, coupon_id, subtotal, discount_amount, total_amount))
        order_id = cursor.lastrowid
        
        # 4. Move to OrderItem
        for item in items:
            item_subtotal = item['price'] * item['quantity']
            cursor.execute("""
                INSERT INTO OrderItem (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price'], item_subtotal))
            
            # NOTE: We do not update Product stock here because trg_reduce_stock MySQL trigger handles it automatically!
            
        # 5. Clear Cart
        cursor.execute("DELETE FROM CartItem WHERE cart_id = %s", (cart_id,))
        
        # 6. Update Coupon usage
        if coupon_id:
            cursor.execute("UPDATE Coupon SET used_count = used_count + 1 WHERE coupon_id = %s", (coupon_id,))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Checkout SQL Error: {e}")
        conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_order_status(order_id, status):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("UPDATE `Order` SET status = %s WHERE order_id = %s", (status, order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Order Status error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_sellers():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT seller_id, shop_name FROM Seller")
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_admin_detailed_orders():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT o.order_id, o.order_date, c.full_name AS customer_name, o.total_amount, o.status AS order_status, 
                   s.shop_name AS seller_name, p.product_name, oi.quantity, oi.subtotal
            FROM `Order` o
            JOIN Customer c USING(customer_id)
            JOIN OrderItem oi USING(order_id)
            JOIN Product p USING(product_id)
            JOIN Seller s USING(seller_id)
            ORDER BY o.order_date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_revenue_by_category():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT c.category_name, SUM(oi.subtotal) as revenue
            FROM OrderItem oi
            JOIN Product p USING(product_id)
            JOIN Category c USING(category_id)
            JOIN `Order` o USING(order_id)
            WHERE o.status = 'delivered'
            GROUP BY c.category_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_top_sellers():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(buffered=True, dictionary=True)
        query = """
            SELECT s.shop_name, SUM(oi.subtotal) as revenue
            FROM OrderItem oi
            JOIN Product p USING(product_id)
            JOIN Seller s USING(seller_id)
            JOIN `Order` o USING(order_id)
            WHERE o.status = 'delivered'
            GROUP BY s.shop_name
            ORDER BY revenue DESC
            LIMIT 5
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_product_stock(product_id, new_stock):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("UPDATE Product SET stock = %s WHERE product_id = %s", (new_stock, product_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Update Stock Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
