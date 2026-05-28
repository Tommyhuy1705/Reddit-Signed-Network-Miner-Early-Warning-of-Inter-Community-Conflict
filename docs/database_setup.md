# Hướng dẫn setup database cho PostgreSQL hoặc SQL Server

Dự án không dùng SQLite cho data warehouse. Pipeline dùng SQLAlchemy để load star schema vào PostgreSQL hoặc SQL Server.

## 1. PostgreSQL

Tạo database:

```sql
CREATE DATABASE olist_dwh;
```

File `.env`:

```env
OLIST_DB_DIALECT=postgresql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=5432
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=postgres
OLIST_DB_PASSWORD=postgres
```

Chạy loader:

```powershell
python scripts/load_warehouse.py
```

## 2. SQL Server

Tạo database:

```sql
CREATE DATABASE olist_dwh;
GO
```

File `.env`:

```env
OLIST_DB_DIALECT=mssql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=1433
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=sa
OLIST_DB_PASSWORD=YourStrongPassword
OLIST_DB_DRIVER=ODBC Driver 17 for SQL Server
```

Chạy loader:

```powershell
python scripts/load_warehouse.py
```

## 3. Các bảng warehouse

- `dim_date`
- `dim_customer`
- `dim_seller`
- `dim_product`
- `dim_payment`
- `dim_order_status`
- `fact_order_items`

Grain của fact table: 1 dòng = 1 item trong 1 order.

## 4. Query OLAP mẫu

Doanh thu theo tháng:

```sql
SELECT
    d.year,
    d.month,
    COUNT(DISTINCT f.order_id) AS orders,
    SUM(f.price) AS revenue,
    SUM(f.freight_value) AS freight
FROM fact_order_items f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

Top category theo doanh thu:

```sql
SELECT
    p.product_category_name_english,
    COUNT(DISTINCT f.order_id) AS orders,
    SUM(f.price) AS revenue,
    AVG(f.review_score) AS avg_review_score
FROM fact_order_items f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY revenue DESC;
```

Delay rate theo bang của seller:

```sql
SELECT
    s.seller_state,
    COUNT(DISTINCT f.order_id) AS orders,
    AVG(CAST(f.is_delayed AS FLOAT)) AS delay_rate,
    AVG(f.delay_days) AS avg_delay_days
FROM fact_order_items f
JOIN dim_seller s ON f.seller_id = s.seller_id
GROUP BY s.seller_state
HAVING COUNT(DISTINCT f.order_id) >= 100
ORDER BY delay_rate DESC;
```

Bad review rate theo category và payment type:

```sql
SELECT
    p.product_category_name_english,
    pay.payment_type,
    COUNT(DISTINCT f.order_id) AS orders,
    AVG(CAST(f.bad_review AS FLOAT)) AS bad_review_rate
FROM fact_order_items f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_payment pay ON f.payment_key = pay.payment_key
WHERE f.bad_review IS NOT NULL
GROUP BY p.product_category_name_english, pay.payment_type
HAVING COUNT(DISTINCT f.order_id) >= 100
ORDER BY bad_review_rate DESC;
```
