# Olist E-Commerce Analytics: Data Warehouse, Iceberg Cube and Bad Review Prediction

## 1. Gioi thieu

Du an nay phan tich bo du lieu **Brazilian E-Commerce Public Dataset by Olist** tren Kaggle. Day la bo du lieu thuong mai dien tu da an danh, mo ta don hang, khach hang, seller, san pham, thanh toan, van chuyen, review va vi tri dia ly cua marketplace Olist tai Brazil.

Muc tieu do an:

- Mo ta day du bo du lieu va cac quan he giua bang.
- Thuc hien EDA de rut ra insight kinh doanh.
- Tien xu ly va tao dac trung phuc vu khai pha du lieu.
- Xay dung data warehouse bang PostgreSQL hoac SQL Server.
- Tinh toan Iceberg Cube de tim cac mau tong hop co y nghia.
- Huan luyen mo hinh classification du doan don hang co kha nang nhan review xau.
- Trien khai API va ung dung Streamlit dashboard.

## 2. Dataset

Dat 9 file CSV cua Olist trong thu muc `dataset/`:

| File | Vai tro |
|---|---|
| `olist_orders_dataset.csv` | Don hang, trang thai va moc thoi gian |
| `olist_customers_dataset.csv` | Khach hang, city/state/zip prefix |
| `olist_order_items_dataset.csv` | Item trong don hang, seller, gia va phi van chuyen |
| `olist_order_payments_dataset.csv` | Phuong thuc thanh toan va gia tri thanh toan |
| `olist_order_reviews_dataset.csv` | Review score va comment |
| `olist_products_dataset.csv` | San pham, category, kich thuoc, khoi luong |
| `olist_sellers_dataset.csv` | Seller, city/state/zip prefix |
| `olist_geolocation_dataset.csv` | Toa do theo zip code prefix |
| `product_category_name_translation.csv` | Dich category sang tieng Anh |

Thong tin nhanh da kiem tra:

- Orders: 99,441 dong.
- Order items: 112,650 dong.
- Payments: 103,886 dong.
- Reviews: 99,224 dong.
- Products: 32,951 dong.
- Sellers: 3,095 dong.
- Geolocation: 1,000,163 dong.
- Khoang thoi gian don hang: 2016-09-04 den 2018-10-17.

## 3. Cau truc du an

```text
.
├── api/                         # FastAPI service
├── app/                         # Streamlit dashboard
├── dataset/                     # Raw Olist CSV files
├── data/
│   ├── processed/               # Generated processed CSV files
│   └── warehouse/               # Generated Iceberg Cube CSV exports
├── docs/                        # Project tasks and report
├── models/                      # Generated trained model and metrics
├── notebooks/                   # EDA, preprocessing, DWH/cube, classification notebooks
├── scripts/                     # Reproducible pipeline scripts
└── src/                         # ETL, OLAP, ML and config modules
```

## 4. Cai dat

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Neu virtual environment cua ban co cau truc `bin/`:

```powershell
.\.venv\bin\Activate.ps1
pip install -r requirements.txt
```

Luu y: nen dung Python chinh thuc tu python.org hoac conda. Neu dung Python MSYS2/UCRT, pip co the build pandas/numpy tu source va loi SSL/cmake.

## 5. Cau hinh database

Du an khong dung SQLite cho warehouse. Mac dinh loader dung PostgreSQL.

Sao chep `.env.example` thanh `.env`, sau do sua thong tin database:

```env
OLIST_DB_DIALECT=postgresql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=5432
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=postgres
OLIST_DB_PASSWORD=postgres
```

Neu dung SQL Server:

```env
OLIST_DB_DIALECT=mssql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=1433
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=sa
OLIST_DB_PASSWORD=YourStrongPassword
OLIST_DB_DRIVER=ODBC Driver 17 for SQL Server
```

Can tao database `olist_dwh` truoc trong PostgreSQL/SQL Server.

## 6. Chay pipeline

Tao processed data va star schema CSV:

```powershell
python scripts/build_processed.py
```

Load star schema vao PostgreSQL hoac SQL Server:

```powershell
python scripts/load_warehouse.py
```

Chay Iceberg Cube:

```powershell
python scripts/run_iceberg_cube.py
```

Train classification model:

```powershell
python scripts/train_bad_review_model.py
```

## 7. Chay ung dung

API:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Streamlit:

```powershell
streamlit run app/Home.py
```

## 8. Bai toan classification

Mo hinh du doan `bad_review`:

- `bad_review = 1` neu `review_score <= 2`.
- `bad_review = 0` neu `review_score >= 4`.
- Bo qua `review_score = 3` khi train de tranh nhan trung tinh.

Feature chinh:

- Gia tri don hang, phi ship, ti le ship/gia.
- Payment type, installments.
- So item, so product, so seller.
- Category, customer state, seller state.
- Delivery days, delay days, delayed flag.
- Thang mua hang, thu trong tuan.

## 9. Data warehouse va Iceberg Cube

Star schema:

- `fact_order_items`
- `dim_date`
- `dim_customer`
- `dim_seller`
- `dim_product`
- `dim_payment`
- `dim_order_status`

Iceberg Cube duoc tinh theo cac chu de:

- Sales by time, category and customer state.
- Delivery quality by seller state, category and delay flag.
- Payment satisfaction by payment type, installments and review group.
- Geographic trade lanes by customer state, seller state and review group.

## 10. Tai lieu

- Checklist cong viec: `docs/olist_project_tasks.md`
- Report khung: `docs/report/olist_report.md`
