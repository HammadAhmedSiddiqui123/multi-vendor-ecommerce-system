-- Users (insert first)
INSERT INTO users (name, email, password, role) VALUES
('Admin User', 'admin@store.com', SHA2('admin123',256), 'admin'),
('Ali Ahmed', 'ali@store.com', SHA2('seller123',256), 'seller'),
('Sara Khan', 'sara@store.com', SHA2('seller456',256), 'seller'),
('Hassan Ali', 'hassan@store.com', SHA2('seller789',256), 'seller'),
('John Doe', 'john@email.com', SHA2('cust123',256), 'customer'),
('Ayesha Malik', 'ayesha@email.com', SHA2('cust456',256), 'customer'),
('Bilal Khan', 'bilal@email.com', SHA2('cust789',256), 'customer'),
('Fatima Noor', 'fatima@email.com', SHA2('cust999',256), 'customer'),
('Usman Tariq', 'usman@email.com', SHA2('cust321',256), 'customer'),
('Zara Sheikh', 'zara@email.com', SHA2('cust654',256), 'customer');

-- Sellers (after User)
INSERT INTO seller (user_id, shop_name, phone, address) VALUES
(2, 'Ali Electronics', '03001234567', 'Karachi'),
(3, 'Sara Fashion', '03112345678', 'Lahore'),
(4, 'Hassan Mart', '03214567890', 'Islamabad');

-- Customers (after User)
INSERT INTO customer (user_id, full_name, email, phone) VALUES
(5, 'John Doe', 'john@email.com', '03221234567'),
(6, 'Ayesha Malik', 'ayesha@email.com', '03331234567'),
(7, 'Bilal Khan', 'bilal@email.com', '03451234567'),
(8, 'Fatima Noor', 'fatima@email.com', '03009876543'),
(9, 'Usman Tariq', 'usman@email.com', '03111222333'),
(10,'Zara Sheikh', 'zara@email.com', '03219876543');
-- Categories
INSERT INTO category (category_name, discription) VALUES
('Electronics', 'Phones and gadgets'),
('Clothing', 'Fashion items'),
('Books', 'All books'),
('Sports', 'Sports equipment'),
('Beauty', 'Cosmetics');

INSERT INTO sub_category (category_id, subcategory_name, discriprion) VALUES
(1, 'Mobiles', 'Smartphones'),
(1, 'Accessories', 'Tech accessories'),
(2, 'Shoes', 'Footwear'),
(2, 'Shirts', 'Upper wear'),
(3, 'Self-help', 'Motivation books'),
(4, 'Fitness', 'Gym equipment');

-- Brands
INSERT INTO brand (brand_name, country) VALUES
('Samsung', 'Korea'),
('Nike', 'USA'),
('Adidas', 'Germany'),
('Penguin', 'UK'),
('L’Oreal', 'France');

-- Products
INSERT INTO product 
(seller_id, category_id, subcategory_id, brand_id, product_name, description, price, stock, status)
VALUES
(1,1,1,1,'Samsung Galaxy A54','128GB phone',65000,30,'active'),
(1,1,2,1,'Samsung Earbuds','Wireless earbuds',8500,50,'active'),
(2,2,3,2,'Nike Shoes','Running shoes',12000,40,'active'),
(2,2,4,2,'Nike T-Shirt','Cotton shirt',3000,60,'active'),
(3,4,6,3,'Dumbbells','10kg pair',5000,25,'active'),
(3,4,6,3,'Yoga Mat','Exercise mat',2000,70,'active'),
(2,3,5,4,'Atomic Habits','Self-help book',1800,100,'active'),
(2,3,5,4,'Deep Work','Productivity book',1500,80,'active'),
(1,1,1,1,'Samsung Tablet','10-inch tablet',45000,20,'active'),
(3,5,NULL,5,'Face Wash','Skin cleanser',900,90,'active');

-- User Addresses
INSERT INTO useraddress (user_id, label, street, city, postal_code) VALUES
(5,'Home','Street 1','Karachi','75000'),
(6,'Home','Street 2','Lahore','54000'),
(7,'Home','Street 3','Karachi','75010'),
(8,'Home','Street 4','Islamabad','44000'),
(9,'Home','Street 5','Karachi','75020'),
(10,'Home','Street 6','Lahore','54010');

INSERT INTO Coupon 
(code, discount_type, discount_value, min_order_amount, max_uses, start_date, end_date, is_active)
VALUES
('SAVE10',   'percentage', 10.00, 500.00, 100, '2025-01-01', '2026-12-31', 1),
('FLAT200',  'fixed',     200.00, 1000.00, 50, '2025-01-01', '2026-12-31', 1),
('SAVE20',   'percentage', 20.00, 2000.00, 30, '2025-01-01', '2026-12-31', 1),
('WELCOME50','fixed',      50.00, 300.00, 200, '2025-01-01', '2026-12-31', 1),
('MEGA500',  'fixed',     500.00, 5000.00, 20, '2025-01-01', '2026-12-31', 1);
-- Orders
INSERT INTO `Order` (customer_id, address_id, subtotal, total_amount, status) VALUES
(1,1,65000,65000,'delivered'),
(2,2,13800,13800,'processing'),
(3,3,5000,5000,'delivered'),
(4,4,2000,2000,'confirmed'),
(5,5,3000,3000,'shipped'),
(6,6,1500,1500,'pending');

-- Order Items
INSERT INTO OrderItem (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1,1,1,65000,65000),
(2,3,1,12000,12000),
(2,4,1,3000,3000),
(3,5,1,5000,5000),
(4,6,1,2000,2000),
(5,4,1,3000,3000),
(6,8,1,1500,1500),
(6,7,1,1800,1800);

INSERT INTO Payment (order_id, amount, status, payment_date) VALUES
(1,65000,'completed',NOW()),
(2,13800,'pending',NULL),
(3,5000,'completed',NOW()),
(4,2000,'completed',NOW()),
(5,3000,'pending',NULL),
(6,1500,'pending',NULL);

-- Reviews
INSERT INTO Review (product_id, customer_id, rating_value, comment) VALUES
(1,1,5,'Excellent phone'),
(3,2,4,'Comfortable shoes'),
(5,3,5,'Good quality'),
(6,4,3,'Average'),
(7,6,4,'Nice book');
INSERT INTO `Order`
(customer_id, address_id, subtotal, discount_amount, total_amount, status, order_date)
VALUES
(1, 1, 5000, 0, 5000, 'delivered', '2025-01-05'),
(2, 2, 12000, 200, 11800, 'delivered', '2025-01-10'),
(3, 3, 3000, 0, 3000, 'delivered', '2025-02-02'),
(4, 4, 7000, 500, 6500, 'delivered', '2025-02-15'),
(5, 5, 1500, 0, 1500, 'delivered', '2025-03-01'),
(6, 6, 9000, 0, 9000, 'delivered', '2025-03-10'),
(1, 1, 2500, 0, 2500, 'delivered', '2025-04-05'),
(2, 2, 11000, 200, 10800, 'delivered', '2025-04-18'),
(3, 3, 4500, 0, 4500, 'delivered', '2025-05-02'),
(4, 4, 8000, 0, 8000, 'delivered', '2025-05-20'),
(5, 5, 6000, 0, 6000, 'delivered', '2025-06-01'),
(6, 6, 2000, 0, 2000, 'delivered', '2025-06-12');
INSERT INTO OrderItem (order_id, product_id, quantity, unit_price, subtotal) VALUES
(7, 1, 1, 5000, 5000),
(8, 3, 1, 12000, 12000),
(9, 2, 1, 3000, 3000),
(10, 5, 1, 7000, 7000),
(11, 6, 1, 1500, 1500),
(12, 4, 1, 9000, 9000),
(13, 5, 1, 2500, 2500),
(14, 3, 1, 11000, 11000),
(15, 2, 1, 4500, 4500),
(16, 1, 1, 8000, 8000),
(17, 6, 1, 6000, 6000),
(18, 4, 1, 2000, 2000);

-- UPDATE `Order`
-- SET coupon_id = 1, discount_amount = 6500
-- WHERE order_id = 1;

-- UPDATE `Order`
-- SET coupon_id = 2, discount_amount = 200
-- WHERE order_id = 2;

-- UPDATE `Order`
-- SET coupon_id = 4, discount_amount = 50
-- WHERE order_id = 4;
