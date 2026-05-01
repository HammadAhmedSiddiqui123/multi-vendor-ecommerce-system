DELIMITER $$

CREATE TRIGGER trg_check_stock
BEFORE INSERT ON OrderItem
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;

    SELECT stock INTO current_stock
    FROM Product
    WHERE product_id = NEW.product_id;

    IF current_stock < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough stock';
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_reduce_stock
AFTER INSERT ON OrderItem
FOR EACH ROW
BEGIN
    UPDATE Product
    SET stock = stock - NEW.quantity
    WHERE product_id = NEW.product_id;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_coupon_usage
AFTER UPDATE ON `Order`
FOR EACH ROW
BEGIN
    IF NEW.coupon_id IS NOT NULL AND OLD.coupon_id IS NULL THEN
        UPDATE Coupon
        SET used_count = used_count + 1
        WHERE coupon_id = NEW.coupon_id;
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_product_status
AFTER UPDATE ON Product
FOR EACH ROW
BEGIN
    IF NEW.stock = 0 THEN
        UPDATE Product
        SET status = 'out_of_stock'
        WHERE product_id = NEW.product_id;
    END IF;
END $$

DELIMITER ;
