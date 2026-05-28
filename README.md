# Olist E-Commerce Analytics: Data Warehouse, Iceberg Cube và Dự Đoán Review Xấu

## 1. Giới thiệu

Dự án này phân tích bộ dữ liệu **Brazilian E-Commerce Public Dataset by Olist** trên Kaggle. Đây là bộ dữ liệu thương mại điện tử đã được ẩn danh, mô tả đơn hàng, khách hàng, người bán, sản phẩm, thanh toán, vận chuyển, review và vị trí địa lý của marketplace Olist tại Brazil.

Mục tiêu đồ án:

- Mô tả đầy đủ bộ dữ liệu và quan hệ giữa các bảng.
- Thực hiện EDA để rút ra insight kinh doanh.
- Tiền xử lý dữ liệu và tạo đặc trưng phục vụ khai phá dữ liệu.
- Xây dựng data warehouse bằng PostgreSQL hoặc SQL Server.
- Tính toán Iceberg Cube để tìm các mẫu tổng hợp có ý nghĩa.
- Huấn luyện mô hình classification dự đoán đơn hàng có khả năng nhận review xấu.
- Triển khai API và ứng dụng Streamlit dashboard.

## 2. Dataset

Đặt 9 file CSV của Olist trong thư mục `dataset/`:

| File | Vai trò |
|---|---|
| `olist_orders_dataset.csv` | Đơn hàng, trạng thái và các mốc thời gian |
| `olist_customers_dataset.csv` | Khách hàng, thành phố, bang và zip prefix |
| `olist_order_items_dataset.csv` | Item trong đơn hàng, seller, giá và phí vận chuyển |
| `olist_order_payments_dataset.csv` | Phương thức thanh toán và giá trị thanh toán |
| `olist_order_reviews_dataset.csv` | Điểm review và comment |
| `olist_products_dataset.csv` | Sản phẩm, danh mục, kích thước và khối lượng |
| `olist_sellers_dataset.csv` | Người bán, thành phố, bang và zip prefix |
| `olist_geolocation_dataset.csv` | Tọa độ theo zip code prefix |
| `product_category_name_translation.csv` | Dịch danh mục sản phẩm sang tiếng Anh |

Thông tin nhanh đã kiểm tra:

- Orders: 99,441 dòng.
- Order items: 112,650 dòng.
- Payments: 103,886 dòng.
- Reviews: 99,224 dòng.
- Products: 32,951 dòng.
- Sellers: 3,095 dòng.
- Geolocation: 1,000,163 dòng.
- Khoảng thời gian đơn hàng: từ 2016-09-04 đến 2018-10-17.

## 3. Cấu trúc dự án

```text
.
├── api/                         # FastAPI service
├── app/                         # Streamlit dashboard
├── dataset/                     # Raw Olist CSV files, không commit
├── data/
│   ├── processed/               # Processed CSV được sinh từ pipeline
│   └── warehouse/               # Kết quả Iceberg Cube dạng CSV
├── docs/                        # Checklist, hướng dẫn database và report
├── models/                      # Model đã train và metrics, không commit file nặng
├── notebooks/                   # EDA, preprocessing, DWH/cube, classification
├── scripts/                     # Pipeline scripts có thể chạy lại
└── src/                         # ETL, OLAP, ML và cấu hình
```

## 4. Cài đặt

Khuyến nghị dùng môi trường ảo `.venv312` đã tạo trong project:

```powershell
.\.venv312\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nếu tạo môi trường mới:

```powershell
python -m venv .venv312
.\.venv312\Scripts\Activate.ps1
pip install -r requirements.txt
```

Lưu ý: nên dùng Python chính thức từ python.org hoặc conda. Python MSYS2/UCRT có thể khiến pip build pandas/numpy từ source và phát sinh lỗi SSL/cmake.

## 5. Cấu hình database

Dự án **không dùng SQLite** cho warehouse. Loader hỗ trợ PostgreSQL và SQL Server.

Sao chép `.env.example` thành `.env`, sau đó sửa thông tin database.

PostgreSQL:

```env
OLIST_DB_DIALECT=postgresql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=5432
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=postgres
OLIST_DB_PASSWORD=postgres
```

SQL Server:

```env
OLIST_DB_DIALECT=mssql
OLIST_DB_HOST=localhost
OLIST_DB_PORT=1433
OLIST_DB_NAME=olist_dwh
OLIST_DB_USER=sa
OLIST_DB_PASSWORD=YourStrongPassword
OLIST_DB_DRIVER=ODBC Driver 17 for SQL Server
```

## 6. Chạy pipeline

Tạo processed data và star schema CSV:

```powershell
python scripts/build_processed.py
```

Load star schema vào PostgreSQL hoặc SQL Server:

```powershell
python scripts/load_warehouse.py
```

Chạy Iceberg Cube:

```powershell
python scripts/run_iceberg_cube.py
```

Train mô hình classification:

```powershell
python scripts/train_bad_review_model.py
```

## 7. Chạy ứng dụng

API:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Streamlit:

```powershell
streamlit run app/Home.py
```

## 8. Bài toán classification

Mô hình dự đoán `bad_review`:

- `bad_review = 1` nếu `review_score <= 2`.
- `bad_review = 0` nếu `review_score >= 4`.
- Bỏ qua `review_score = 3` khi train để tránh nhãn trung tính.

Feature chính:

- Giá trị đơn hàng, phí ship, tỷ lệ phí ship trên giá trị hàng.
- Payment type và số kỳ trả góp.
- Số item, số sản phẩm, số seller.
- Category, customer state, seller state.
- Delivery days, delay days, delayed flag.
- Tháng mua hàng và thứ trong tuần.

## 9. Data warehouse và Iceberg Cube

Star schema:

- `fact_order_items`
- `dim_date`
- `dim_customer`
- `dim_seller`
- `dim_product`
- `dim_payment`
- `dim_order_status`

Iceberg Cube được tính theo các chủ đề:

- Doanh thu theo thời gian, danh mục và bang của khách hàng.
- Chất lượng giao hàng theo bang của seller, danh mục và trạng thái trễ.
- Mức độ hài lòng theo phương thức thanh toán, nhóm trả góp và nhóm review.
- Luồng giao dịch theo bang khách hàng, bang seller và nhóm review.

## 10. Tài liệu

- Checklist công việc: `docs/olist_project_tasks.md`
- Hướng dẫn database: `docs/database_setup.md`
- Report khung: `docs/report/olist_report.md`
