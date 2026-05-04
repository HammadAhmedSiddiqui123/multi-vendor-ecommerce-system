# Project Setup Guide: Multi-Vendor E-Commerce System

Follow these steps to set up the project on your local machine.

## 1. Prerequisites
Ensure you have the following installed:
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **MySQL Server**: [Download MySQL](https://dev.mysql.com/downloads/installer/) (Workbench is also recommended)
- **Git**: [Download Git](https://git-scm.com/downloads) (Optional, for cloning)

---

## 2. Database Configuration
You need to set up the MySQL database before running the application.

### Step A: Create the Database
Open your MySQL terminal or MySQL Workbench and run:
```sql
CREATE DATABASE ecommerce_db;
```

### Step B: Run SQL Scripts
Execute the following SQL files in the project root in this **exact order**:
1. `ecommerce_schema.sql` (Creates tables)
2. `ecommerce_triggers.sql` (Sets up automation for stock and coupons)
3. `ecommerce_views_and_updates.sql` (Sets up views for analytics)
4. `commerce_insert.sql` (Seeds the database with initial data/users)

---

## 3. Python Environment Setup
Navigate to the project directory in your terminal/command prompt.

### Step A: Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

### Step B: Activate the Virtual Environment
- **Windows**:
  ```bash
  .\venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step C: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. Environment Variables
1. Find the `.env.example` file in the project root.
2. Create a copy and rename it to `.env`.
3. Open `.env` and fill in your MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=ecommerce_db
   ```

---

## 5. Running the Application
Once everything is set up, start the application using Streamlit:
```bash
streamlit run app.py
```
The app will automatically open in your default browser (usually at `http://localhost:8501`).

---

## 6. Accessing the Dashboards
The project includes three roles. You can use the seeded users from `commerce_insert.sql` to log in:

- **Admin**: Full control over users, products, and analytics.
- **Seller**: Manage shop, products, and orders.
- **Customer**: Browse products, manage cart, and place orders.

> [!TIP]
> Check `commerce_insert.sql` for the default login credentials (emails and passwords). Note that passwords in the database are stored as SHA-256 hashes.
