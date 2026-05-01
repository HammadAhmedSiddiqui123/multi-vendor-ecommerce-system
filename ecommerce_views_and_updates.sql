-- Top Rated Products View
CREATE VIEW vw_TopRatedProducts AS
SELECT
    p.product_id,
    p.product_name,
    p.price,
    ROUND(AVG(r.rating_value), 2) AS avg_rating,
    COUNT(r.review_id)            AS review_count
FROM Product p
JOIN Review r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name, p.price
HAVING avg_rating >= 4.0
ORDER BY avg_rating DESC;

-- Use it anywhere with a simple SELECT:
SELECT * FROM vw_TopRatedProducts;

-- Seller Dashboard View
CREATE VIEW vw_SellerDashboard AS
SELECT
    s.seller_id,
    s.shop_name,
    COUNT(DISTINCT p.product_id)  AS total_products,
    COUNT(DISTINCT o.order_id)    AS total_orders,
    COALESCE(SUM(oi.subtotal), 0) AS total_revenue
FROM Seller s
LEFT JOIN Product   p  ON s.seller_id   = p.seller_id
LEFT JOIN OrderItem oi ON p.product_id  = oi.product_id
LEFT JOIN `Order`   o  ON oi.order_id   = o.order_id AND o.status = 'delivered'
GROUP BY s.seller_id, s.shop_name;

-- Filter for one seller in Streamlit:
CREATE VIEW vw_SellerDashboard AS
SELECT
    s.seller_id,
    s.shop_name,
    COUNT(DISTINCT p.product_id)  AS total_products,
    COUNT(DISTINCT o.order_id)    AS total_orders,
    COALESCE(SUM(oi.subtotal), 0) AS total_revenue
FROM Seller s
LEFT JOIN Product   p  ON s.seller_id   = p.seller_id
LEFT JOIN OrderItem oi ON p.product_id  = oi.product_id
LEFT JOIN `Order`   o  ON oi.order_id   = o.order_id AND o.status = 'delivered'
GROUP BY s.seller_id, s.shop_name;

-- Filter for one seller in Streamlit:
CREATE VIEW vw_SellerDashboard AS
SELECT
    s.seller_id,
    s.shop_name,
    COUNT(DISTINCT p.product_id)  AS total_products,
    COUNT(DISTINCT o.order_id)    AS total_orders,
    COALESCE(SUM(oi.subtotal), 0) AS total_revenue
FROM Seller s
LEFT JOIN Product   p  ON s.seller_id   = p.seller_id
LEFT JOIN OrderItem oi ON p.product_id  = oi.product_id
LEFT JOIN `Order`   o  ON oi.order_id   = o.order_id AND o.status = 'delivered'
GROUP BY s.seller_id, s.shop_name;

-- Filter for one seller in Streamlit:
CREATE OR REPLACE VIEW vw_SellerDashboard AS
SELECT
    s.seller_id,
    s.shop_name,
    COUNT(DISTINCT p.product_id)  AS total_products,
    COUNT(DISTINCT o.order_id)    AS total_orders,
    COALESCE(SUM(oi.subtotal), 0) AS total_revenue
FROM Seller s
LEFT JOIN Product   p  ON s.seller_id   = p.seller_id
LEFT JOIN OrderItem oi ON p.product_id  = oi.product_id
LEFT JOIN `Order`   o  ON oi.order_id   = o.order_id AND o.status = 'delivered'
GROUP BY s.seller_id, s.shop_name;
-- Filter for one seller in Streamlit:
SELECT * FROM vw_SellerDashboard WHERE seller_id = ?;
-- Low Stock Alert View
CREATE VIEW vw_LowStock AS
SELECT
    p.product_name,
    s.shop_name AS seller,
    i.quantity_on_hand,
    i.reorder_level,
    w.name AS warehouse
FROM Inventory i
JOIN Product   p ON i.product_id   = p.product_id
JOIN Seller    s ON p.seller_id    = s.seller_id
JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
WHERE i.quantity_on_hand <= i.reorder_level;

-- Show alerts in admin/seller dashboard:
SELECT * FROM vw_LowStock;
 -- Update Order Status
UPDATE `Order`
SET status = 'shipped'
WHERE order_id = ?;

-- Also update the shipment:
UPDATE Shipment
SET status = 'dispatched', shipped_at = NOW()
WHERE order_id = ?;
-- Reduce Stock After Order Placed
-- Run this after each OrderItem is inserted:
UPDATE Product
SET stock = stock - ?   -- ? = quantity ordered
WHERE product_id = ?
  AND stock >= ?;    
--  Deactivate a Product
-- Preferred over DELETE — preserves order history
UPDATE Product
SET status = 'inactive'
WHERE product_id = ?
  AND seller_id  = ?; 
 --  Apply Coupon to Order
  -- Step 1: Validate coupon
SELECT coupon_id, discount_type, discount_value
FROM Coupon
WHERE code      = ?
  AND is_active = 1
  AND NOW() BETWEEN start_date AND end_date
  AND (max_uses IS NULL OR used_count < max_uses);

-- Step 2: If valid, update order and increment used_count
UPDATE Coupon SET used_count = used_count + 1 WHERE coupon_id = ?;