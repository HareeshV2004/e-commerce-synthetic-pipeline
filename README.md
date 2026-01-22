
# E-Commerce Synthetic Data Pipeline  
**End-to-End Data Generation, Storage, and Analytics Consumption**

---

##  Problem Statement
Real-world e-commerce data is often **restricted, incomplete, or inaccessible** due to privacy, compliance, and commercial constraints. Despite this, analytics teams must still develop, test, and validate **data pipelines, dashboards, and analytical workflows**.

This project builds an **end-to-end synthetic data pipeline** that simulates realistic e-commerce transactions and demonstrates how data flows through **generation, ingestion, storage, and analytics layers**.

>  The objective is **not model accuracy**, but **pipeline realism, reproducibility, and downstream usability**.

---

##  Why This Problem Is Hard
- Synthetic data must preserve **statistical realism** without exposing real users  
- Poor pipeline design breaks downstream analytics  
- Many analytics projects fail due to **data availability**, not modeling  
- Modern data scientists are expected to **own data flows**, not just notebooks  

This mirrors real industry practices where synthetic data is used for **testing, prototyping, and compliance-safe analytics**.

---

##  Pipeline Architecture

**1. Data Generation**
- Simulated customers, products, and transactions  
- Controlled distributions for price, quantity, categories, and timestamps  
- Temporal consistency for time-series analysis  

**2. Data Ingestion**
- Automated ingestion scripts  
- Structured formats suitable for analytics consumption  

**3. Data Storage**
- Relational schema design  
- Normalized tables:
  - Customers  
  - Orders  
  - Products  

**4. Analytics Consumption**
- SQL-ready tables  
- Compatible with:
  - Python analytics  
  - BI dashboards (Power BI / Tableau)  
<img width="800" height="533" alt="image" src="https://github.com/user-attachments/assets/d62635b4-9822-4da4-9f2f-fc3c15844140" />


---

## Methodology

### Synthetic Data Design
- Defined realistic ranges and probability distributions  
- Preserved relational integrity across tables  
- Introduced controlled randomness to mimic real variability  

### Data Engineering Considerations
- Schema optimized for analytical queries  
- Clear separation between raw and processed data  
- Reproducible data generation for consistent testing  

### Analytics Readiness
Data structured to support:
- Sales trend analysis  
- Customer segmentation  
- Funnel and cohort analysis  

---

## Key Insights
- Synthetic datasets can effectively support **analytics development and validation**  
- Proper schema design significantly reduces downstream cleaning effort  
- Pipeline consistency matters more than raw data volume for analytics reliability  

---

## Assumptions & Limitations
- Synthetic data approximates patterns but cannot capture true human behavior  
- External business dynamics (marketing, competition) are not modeled  
- Designed for **testing and prototyping**, not production decision-making  

---

## Practical Applications
- BI dashboard development without privacy risk  
- Analytics pipeline testing before real data availability  
- Training datasets for junior analysts and data scientists  

---

## Future Enhancements
- Event-level clickstream simulation  
- Automated data validation checks  
- Pipeline orchestration (scheduled runs)  
- Direct integration with BI tools for live dashboards  

---

## Tech Stack
- Python  
- Pandas, NumPy  
- SQL (relational schema)  
- Jupyter Notebook  

---

## Repository Structure


## Dataset Files

### 1. customers.csv
Contains customer information with ~1,000 rows.

**Schema:**
- `customer_id` (integer): Unique identifier for each customer
- `first_name` (string): Customer's first name
- `last_name` (string): Customer's last name
- `email` (string): Customer's email address
- `signup_date` (date, YYYY-MM-DD): Date when customer signed up (range: 2022-01-01 to 2025-10-31)
- `country` (string): Customer's country of residence

**Primary Key:** `customer_id`

**Sample Data:**
```
customer_id,first_name,last_name,email,signup_date,country
1,John,Doe,john.doe123@example.com,2022-03-15,United States
2,Jane,Smith,jane.smith456@example.com,2022-05-22,United Kingdom
```

---

### 2. products.csv
Contains product catalog information with ~500 rows.

**Schema:**
- `product_id` (integer): Unique identifier for each product
- `name` (string): Product name
- `category` (string): Product category (Electronics, Apparel, Home & Garden, Sports & Outdoors, Books, Toys & Games, Health & Beauty, Automotive, Food & Beverages, Office Supplies)
- `price` (decimal): Product price in currency units (range: $5.00 - $5,000.00)
- `launch_date` (date, YYYY-MM-DD): Date when product was launched (range: 2022-01-01 to 2025-09-01)

**Primary Key:** `product_id`

**Sample Data:**
```
product_id,name,category,price,launch_date
1,Acme Corp Smartphone,Electronics,599.99,2022-04-10
2,Brand X Laptop,Electronics,1299.00,2022-06-15
```

---

### 3. orders.csv
Contains order information with ~2,000 rows.

**Schema:**
- `order_id` (integer): Unique identifier for each order
- `customer_id` (integer): Foreign key referencing `customers.customer_id`
- `order_date` (date, YYYY-MM-DD): Date when order was placed (range: 2022-01-01 to 2025-10-31)
- `ship_date` (date, YYYY-MM-DD): Date when order was shipped (1-7 days after order_date, empty for Pending/Cancelled orders)
- `status` (string): Order status (Pending, Processing, Shipped, Delivered, Cancelled)

**Primary Key:** `order_id`  
**Foreign Keys:** 
- `customer_id` → `customers.customer_id`

**Sample Data:**
```
order_id,customer_id,order_date,ship_date,status
1,123,2023-01-15,2023-01-18,Delivered
2,456,2023-02-20,,Pending
```

**Constraints:**
- `order_date` must be on or after the customer's `signup_date`
- `ship_date` is empty for orders with status "Pending" or "Cancelled"

---

### 4. order_items.csv
Contains individual line items for orders with ~4,000 rows (multiple items per order).

**Schema:**
- `order_item_id` (integer): Unique identifier for each order item
- `order_id` (integer): Foreign key referencing `orders.order_id`
- `product_id` (integer): Foreign key referencing `products.product_id`
- `quantity` (integer): Quantity of product ordered (range: 1-5)
- `item_price` (decimal): Price per item at time of order (typically 90-110% of base product price)

**Primary Key:** `order_item_id`  
**Foreign Keys:**
- `order_id` → `orders.order_id`
- `product_id` → `products.product_id`

**Sample Data:**
```
order_item_id,order_id,product_id,quantity,item_price
1,1,50,2,599.99
2,1,75,1,1299.00
3,2,120,3,29.99
```

**Note:** Multiple order items can belong to the same order.

---

### 5. shipments.csv
Contains shipment tracking information with ~1,500 rows.

**Schema:**
- `shipment_id` (integer): Unique identifier for each shipment
- `order_id` (integer): Foreign key referencing `orders.order_id`
- `shipment_date` (date, YYYY-MM-DD): Date when shipment was created/shipped
- `carrier` (string): Shipping carrier name (UPS, FedEx, USPS, DHL, Amazon Logistics, OnTrac)
- `tracking_number` (string): Unique tracking number for the shipment
- `shipment_cost` (decimal): Cost of shipment (range: $5.00 - $50.00)

**Primary Key:** `shipment_id`  
**Foreign Keys:**
- `order_id` → `orders.order_id`

**Sample Data:**
```
shipment_id,order_id,shipment_date,carrier,tracking_number,shipment_cost
1,1,2023-01-18,UPS,UP1234567890,12.50
2,5,2023-02-10,FedEx,FE9876543210,18.75
```

**Constraints:**
- `shipment_date` is typically on or after the order's `ship_date`
- Orders with status "Shipped" or "Delivered" are more likely to have shipments
- Some orders may have multiple shipments

---

## Data Characteristics

### Date Ranges
- **Signup dates:** 2022-01-01 to 2025-10-31
- **Order dates:** 2022-01-01 to 2025-10-31 (always on or after customer signup)
- **Product launch dates:** 2022-01-01 to 2025-09-01
- **Ship dates:** Typically 1-7 days after order date

### Referential Integrity
All foreign key relationships are maintained:
- Every `customer_id` in `orders.csv` exists in `customers.csv`
- Every `product_id` in `order_items.csv` exists in `products.csv`
- Every `order_id` in `order_items.csv` exists in `orders.csv`
- Every `order_id` in `shipments.csv` exists in `orders.csv`

### Data Volume
- **Customers:** ~1,000 rows
- **Products:** ~500 rows
- **Orders:** ~2,000 rows
- **Order Items:** ~4,000 rows (average of 2 items per order)
- **Shipments:** ~1,500 rows (some orders have multiple shipments)

## File Format

- **Format:** CSV (Comma-Separated Values)
- **Delimiter:** Comma (`,`)
- **Header Row:** Yes (column names in first row)
- **Encoding:** UTF-8
- **Index Column:** No

## Usage

### Python (pandas)
```python
import pandas as pd

# Load datasets
customers = pd.read_csv('customers.csv')
products = pd.read_csv('products.csv')
orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
shipments = pd.read_csv('shipments.csv')

# Parse dates
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
orders['order_date'] = pd.to_datetime(orders['order_date'])
```

### SQL (Example)
```sql
-- Join customers with orders
SELECT c.first_name, c.last_name, o.order_id, o.order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Calculate order totals
SELECT oi.order_id, SUM(oi.quantity * oi.item_price) as total
FROM order_items oi
GROUP BY oi.order_id;
```

## Generation

Datasets are generated using `generate_datasets.py` script with the following dependencies:
- `pandas` >= 2.0.0
- `faker` >= 19.0.0

To regenerate the datasets:
```bash
pip install -r requirements.txt
python generate_datasets.py
```

## Notes

- All data is synthetically generated and does not represent real customers, products, or transactions
- Prices, names, and other attributes are randomly generated for demonstration purposes
- Date relationships are maintained to ensure logical consistency (e.g., order dates after signup dates)
- Some orders may have multiple line items and/or multiple shipments

