-- View All Products with Category and Seller
SELECT
    p.product_id,
    p.product_name,
    p.price,
    p.stock,
    c.category_name,
    s.shop_name AS seller
FROM Product p
JOIN Category c USING (category_id)
JOIN Seller s   USING (seller_id)
ORDER BY p.created_at DESC;
-- View All Orders with Customer Name and Status
select 
o.order_id,
c.full_name,
o.status,
o.total_amount,
o. order_date
from `order` o
join customer c using(customer_id)
order by order_date desc;
-- Replace ? with the logged-in seller's seller_id (from Python)
SELECT
    product_id,
    product_name,
    price,
    stock,
    status
FROM Product 
WHERE seller_id = ?; 
-- Validate login credentials
SELECT user_id, name, role
FROM Users
WHERE email = ?
  AND password = SHA2(?, 256);
  
  SELECT
    o.order_id,
    c.full_name    AS customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.subtotal,
    o.status       AS order_status,
    o.order_date
FROM `Order` o
JOIN Customer   c  using(customer_id)
JOIN OrderItem  oi using(order_id)
JOIN Product    p  using(product_id)
ORDER BY o.order_date DESC;
-- Product Page Data (Product + Images + Brand + Category)
SELECT
    p.product_id,
    p.product_name,
    p.description,
    p.price,
    p.stock,
    b.brand_name,
    c.category_name,
    sc.subcategory_name,
    pi.image_url
FROM Product p
LEFT JOIN Brand       b  using(brand_id)       
LEFT JOIN Category    c  using(category_id) 
LEFT JOIN Sub_Category sc using(subcategory_id) 
LEFT JOIN ProductImage pi ON p.product_id    = pi.product_id AND pi.is_primary = 1
WHERE p.product_id = ?;
-- Order with Payment and Shipment Status
SELECT
    o.order_id,
    o.total_amount,
    o.status           AS order_status,
    pay.status         AS payment_status,
    pay.payment_date,
    sh.status          AS shipment_status,
    sh.tracking_code,
    sh.delivered_at
FROM `Order` o
LEFT JOIN Payment  pay using(order_id)
LEFT JOIN Shipment sh  using(order_id )
WHERE o.customer_id = ?;
-- Total Revenue Per Seller
SELECT
    s.shop_name,
    COUNT(DISTINCT o.order_id)  AS total_orders,
    SUM(oi.subtotal)            AS total_revenue,
    AVG(oi.unit_price)          AS avg_product_price
FROM Seller s
JOIN Product   p  ON s.seller_id   = p.seller_id
JOIN OrderItem oi ON p.product_id  = oi.product_id
JOIN `Order`   o  ON oi.order_id   = o.order_id
WHERE o.status = 'delivered'
GROUP BY s.seller_id, s.shop_name
ORDER BY total_revenue DESC;
-- Best-Selling Products
SELECT
    p.product_name,
    s.shop_name AS seller,
    SUM(oi.quantity)  AS total_units_sold,
    SUM(oi.subtotal)  AS total_revenue
FROM OrderItem oi
JOIN Product p ON oi.product_id = p.product_id
JOIN Seller  s ON p.seller_id   = s.seller_id
GROUP BY oi.product_id, p.product_name, s.shop_name
ORDER BY total_units_sold DESC
LIMIT 5;
-- Average Rating Per Product
SELECT
    p.product_name,
    ROUND(AVG(r.rating_value), 2) AS avg_rating,
    COUNT(r.review_id)            AS total_reviews
FROM Product p
LEFT JOIN Review r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name
HAVING COUNT(r.review_id) > 0
ORDER BY avg_rating DESC;

-- Monthly Revenue Report
SELECT
    YEAR(o.order_date)  AS year,
    MONTH(o.order_date) AS month,
    COUNT(o.order_id)   AS total_orders,
    SUM(o.total_amount) AS monthly_revenue
FROM `Order` o
WHERE o.status = 'delivered'
GROUP BY YEAR(o.order_date), MONTH(o.order_date)
ORDER BY year DESC, month DESC;

-- Products Priced Above Average
SELECT
    product_name,
    price,
    price - (SELECT AVG(price) FROM Product) AS above_average_by
FROM Product
WHERE price > (SELECT AVG(price) FROM Product)
ORDER BY price DESC;

--  Customers Who Have Placed More Than 2 Orders
SELECT full_name, email
FROM Customer
WHERE customer_id IN (
    SELECT customer_id
    FROM `Order`
    GROUP BY customer_id
    HAVING COUNT(order_id) > 2
);
 -- Products Never Ordered
 SELECT product_id, product_name, price
FROM Product
WHERE product_id NOT IN (
    SELECT DISTINCT product_id
    FROM OrderItem
);
-- Seller Whose Products Have the Highest Average Rating
SELECT
    s.shop_name,
    ROUND(AVG(r.rating_value), 2) AS avg_rating
FROM Seller s
JOIN Product p ON s.seller_id  = p.seller_id
JOIN Review  r ON p.product_id = r.product_id
GROUP BY s.seller_id
HAVING AVG(r.rating_value) = (
    SELECT MAX(avg_r)
    FROM (
        SELECT AVG(r2.rating_value) AS avg_r
        FROM Seller s2
        JOIN Product p2 ON s2.seller_id  = p2.seller_id
        JOIN Review  r2 ON p2.product_id = r2.product_id
        GROUP BY s2.seller_id
    ) sub
);
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

