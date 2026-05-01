-- 1.user table
create table users(
user_id INT auto_increment primary key ,
name varchar(100) not null,
email varchar(100) not null unique,
password varchar(255) not null,
role enum('admin','seller','customer') not null,
is_active TINYINT(1) DEFAULT 1,
created_at timestamp default current_timestamp
);
-- 2.customer
create table customer(
customer_id int auto_increment primary key,
user_id int not null,
full_name varchar(100) not null,
email varchar (100)  not null unique,
phone varchar(15) not null,
registration_date timestamp default current_timestamp,
foreign key (user_id) references users(user_id) on delete cascade
);
-- 3. seller 
create table seller(
seller_id int auto_increment primary key,
user_id int not null,
shop_name varchar(150) not null,
phone varchar(15) not null,
address varchar (500) ,
rating decimal (3,2),
joined_at timestamp default current_timestamp,
foreign key (user_id) references users(user_id) on delete cascade
);
-- 4.admin
create table admin(
admin_id int auto_increment primary key,
user_id int not null,
full_name varchar(150) not null ,
email varchar(100) unique not null,
created_at timestamp default current_timestamp,
foreign key (user_id) references users(user_id) on delete cascade
);
-- 5. user access
create table useraddress(
address_id int auto_increment primary key,
user_id int not null ,
label varchar(50) not null ,
street varchar(255) not null ,
city varchar(100) not null,
postal_code varchar(20),
foreign key (user_id) references users(user_id) on delete cascade
);
-- 6.category

create table category(
category_id int auto_increment primary key ,
category_name varchar(100) not null,
discription text
);
-- 7.sub_category
create table sub_category(
sub_category int auto_increment primary key,
category_id int not null,
subcategory_name varchar(100) not null,
discriprion text ,
foreign key(category_id) references category(category_id) on delete cascade 
);
ALTER TABLE sub_category
CHANGE sub_category subcategory_id INT AUTO_INCREMENT;
-- 8.brand 
create table brand (
brand_id int auto_increment primary key,
brand_name varchar(100) not null,
logo_url varchar(255),
country varchar(100)
);
-- 9. product 
create table product(
product_id int auto_increment primary key,
seller_id int not null,
category_id int ,
subcategory_id int ,
brand_id int,
product_name varchar(150) not null,
description text ,
price decimal(10,2) not null,
stock int default 0,
status enum('active','inactive','out_of stock') not null,
created_at timestamp default current_timestamp,
 FOREIGN KEY (seller_id)      REFERENCES seller(seller_id)         ON DELETE CASCADE,
 FOREIGN KEY (category_id)    REFERENCES category(category_id)     ON DELETE SET NULL,
 FOREIGN KEY (subcategory_id) REFERENCES sub_Category(subcategory_id) ON DELETE SET NULL,
 FOREIGN KEY (brand_id)       REFERENCES Brand(brand_id)           ON DELETE SET NULL
);
-- 10.productimage
create table productimage(
image_id int auto_increment primary key,
product_id int not null default 0,
image_url varchar(255) not null,
is_primary tinyint(1) not null default 0,
soft_order int default 0,
foreign key (product_id) references product(product_id) on delete cascade 
);
-- 11. WAREHOUSE (no FK dependencies)
CREATE TABLE Warehouse (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    address      VARCHAR(255) NOT NULL,
    city         VARCHAR(100) NOT NULL,
    phone        VARCHAR(20),
    is_active    TINYINT(1) NOT NULL DEFAULT 1
);
-- 12. SUPPLIER (no FK dependencies)
CREATE TABLE Supplier (
    supplier_id    INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    contact_person VARCHAR(150),
    phone          VARCHAR(20) NOT NULL,
    email          VARCHAR(150),
    address        VARCHAR(255),
    is_active      TINYINT(1) NOT NULL DEFAULT 1
);
-- 13. inventory 
create table inventory(
inventory_id int auto_increment primary key ,
product_id int not null,
warehouse_id int not null,
quantity_on_hand decimal(10,2) not null default 0,
reorder_level    DECIMAL(10,2) NOT NULL DEFAULT 10,
updated_at       DATETIME,
FOREIGN KEY (product_id)   REFERENCES Product(product_id)     ON DELETE CASCADE,
FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id) ON DELETE CASCADE 
);
-- 14.cart 
create table cart(
cart_id int auto_increment primary key,
customer_id int not null,
created_at timestamp default current_timestamp,
update_at timestamp default current_timestamp on update current_timestamp,
foreign key (customer_id) references customer(customer_id) on delete cascade
);
-- 15. coupon 
CREATE TABLE Coupon (
    coupon_id         INT AUTO_INCREMENT PRIMARY KEY,
    code              VARCHAR(50) NOT NULL UNIQUE,
    discount_type     ENUM('percentage','fixed') NOT NULL,
    discount_value    DECIMAL(8,2) NOT NULL,
    min_order_amount  DECIMAL(8,2) NOT NULL DEFAULT 0,
    max_uses          INT,
    used_count        INT NOT NULL DEFAULT 0,
    start_date        DATETIME NOT NULL,
    end_date          DATETIME NOT NULL,
    is_active         TINYINT(1) NOT NULL DEFAULT 1
);
-- 16.cartitem
CREATE TABLE CartItem (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id      INT NOT NULL,
    product_id   INT NOT NULL,
    quantity     INT NOT NULL DEFAULT 1,
    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id)    REFERENCES Cart(cart_id)       ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE
);
-- 17.whishlist
CREATE TABLE Wishlist (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id  INT NOT NULL,
    added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)   ON DELETE CASCADE
);
-- 18. ORDER 
CREATE TABLE `Order` (
    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    address_id      INT NOT NULL,
    coupon_id       INT,
    status          ENUM('pending','confirmed','processing','shipped','delivered','cancelled') DEFAULT 'pending',
    subtotal        DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount    DECIMAL(10,2) NOT NULL,
    order_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes           TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)   ON DELETE CASCADE,
    FOREIGN KEY (address_id)  REFERENCES UserAddress(address_id) ON DELETE RESTRICT,
    FOREIGN KEY (coupon_id)   REFERENCES Coupon(coupon_id)       ON DELETE SET NULL
);

-- 19. ORDERITEM 
CREATE TABLE OrderItem (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL,
    subtotal      DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES `Order`(order_id)     ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)   ON DELETE RESTRICT
);
-- 20. PAYMENTMETHOD 
CREATE TABLE PaymentMethod (
    method_id  INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    type       ENUM('card','wallet','bank_transfer','cash_on_delivery') NOT NULL,
    details    VARCHAR(255),
    is_default TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE
);
-- 21. PAYMENT 
CREATE TABLE Payment (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL UNIQUE,
    method_id       INT,
    amount          DECIMAL(10,2) NOT NULL,
    status          ENUM('pending','completed','failed','refunded') DEFAULT 'pending',
    transaction_ref VARCHAR(100),
    payment_date    TIMESTAMP,
    FOREIGN KEY (order_id)  REFERENCES `Order`(order_id)         ON DELETE RESTRICT,
    FOREIGN KEY (method_id) REFERENCES PaymentMethod(method_id)  ON DELETE SET NULL
);
-- 22. DELIVERYAGENT 
CREATE TABLE DeliveryAgent (
    agent_id     INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(150) NOT NULL,
    phone        VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type ENUM('bike','car','bicycle') NOT NULL,
    is_available TINYINT(1) NOT NULL DEFAULT 1,
    rating       DECIMAL(3,2) DEFAULT 0.00,
    joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 23. SHIPMENT 
CREATE TABLE Shipment (
    shipment_id   INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT NOT NULL UNIQUE,
    agent_id      INT,
    status        ENUM('processing','dispatched','in_transit','delivered','failed') DEFAULT 'processing',
    tracking_code VARCHAR(100),
    shipped_at    TIMESTAMP,
    delivered_at  TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id)         ON DELETE RESTRICT,
    FOREIGN KEY (agent_id) REFERENCES DeliveryAgent(agent_id)   ON DELETE SET NULL
);
-- 24. REVIEW 
CREATE TABLE Review (
    review_id    INT AUTO_INCREMENT PRIMARY KEY,
    product_id   INT NOT NULL,
    customer_id  INT NOT NULL,
    rating_value TINYINT NOT NULL CHECK (rating_value >= 1 AND rating_value <= 5),
    comment      TEXT,
    review_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)     ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)   ON DELETE CASCADE
);
-- 25. RATING 
CREATE TABLE Rating (
    rating_id   INT AUTO_INCREMENT PRIMARY KEY,
    product_id  INT NOT NULL,
    customer_id INT NOT NULL,
    rating      TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    rated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)   ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE CASCADE
);