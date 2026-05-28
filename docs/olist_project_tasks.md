# Kế hoạch hoàn thiện đồ án với Olist Brazilian E-Commerce Dataset

## 1. Mục tiêu đề tài

Đề tài mới nên trình bày theo hướng:

**Xây dựng data warehouse và khai phá dữ liệu thương mại điện tử trên bộ dữ liệu Olist Brazilian E-Commerce, kết hợp Iceberg Cube và mô hình dự đoán mức độ hài lòng của khách hàng.**

Bộ dữ liệu phù hợp với chủ đề kinh tế/kinh doanh vì mô tả quá trình vận hành sàn thương mại điện tử: đơn hàng, khách hàng, người bán, sản phẩm, thanh toán, vận chuyển, review và vị trí địa lý.

## 2. Tổng quan dataset

Dataset hiện có trong thư mục `dataset/` gồm 9 file CSV:

| File | Số dòng | Số cột | Vai trò |
|---|---:|---:|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | Bảng đơn hàng, trạng thái và các mốc thời gian xử lý/giao hàng |
| `olist_customers_dataset.csv` | 99,441 | 5 | Thông tin khách hàng, city/state/zip prefix |
| `olist_order_items_dataset.csv` | 112,650 | 7 | Chi tiết sản phẩm trong đơn hàng, seller, giá và phí vận chuyển |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Phương thức thanh toán, số lần trả góp, giá trị thanh toán |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Điểm đánh giá và nội dung review |
| `olist_products_dataset.csv` | 32,951 | 9 | Thông tin sản phẩm, danh mục, kích thước, khối lượng |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Thông tin người bán, city/state/zip prefix |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | Vĩ độ/kinh độ theo zip code prefix |
| `product_category_name_translation.csv` | 71 | 2 | Dịch tên danh mục sản phẩm từ tiếng Bồ Đào Nha sang tiếng Anh |

Thông tin nên đưa vào báo cáo:

- Khoảng thời gian đơn hàng: từ `2016-09-04 21:15:19` đến `2018-10-17 17:30:18`.
- Phần lớn đơn hàng có trạng thái `delivered`.
- Payment type phổ biến nhất là `credit_card`, sau đó là `boleto`.
- Review 5 sao chiếm tỷ lệ lớn nhất, nhưng vẫn có đủ review 1-2 sao để xây dựng bài toán classification.
- Bảng `orders` có missing ở các cột thời gian giao hàng.
- Bảng `products` có một số sản phẩm thiếu category/kích thước.
- Bảng `reviews` thiếu nhiều comment text, nhưng `review_score` vẫn đủ dùng cho bài toán dự đoán review xấu.

## 3. Các thiếu sót của phiên bản Reddit cần khắc phục

- README cũ bị lỗi encoding tiếng Việt và nội dung vẫn theo đề tài Reddit.
- Notebook EDA, preprocessing, DWH và model chỉ là placeholder.
- `src/olap/iceberg_cube.py` chưa cài đặt thuật toán thật.
- `src/models/train.py` chưa huấn luyện model thật.
- Streamlit app chỉ có title placeholder.
- FastAPI chỉ có endpoint `/health`.
- Chưa có dữ liệu đã xử lý, warehouse, cube result hoặc model artifact.

## 4. Công việc cần làm để đáp ứng yêu cầu của thầy

### 4.1. Cập nhật README và cấu trúc dự án

- [x] Chuyển mô tả dự án từ Reddit sang Olist E-Commerce Analytics.
- [x] Sửa tiếng Việt trong tài liệu sang dạng có dấu.
- [x] Bổ sung mô tả dataset, mục tiêu phân tích và bài toán khai phá.
- [x] Cập nhật hướng dẫn chạy pipeline, API, Streamlit và database.
- [x] Thêm `.env.example` để cấu hình PostgreSQL/SQL Server.

### 4.2. Mô tả đầy đủ bộ dữ liệu

- [x] Mô tả business context: marketplace Olist kết nối seller với customer tại Brazil.
- [x] Liệt kê 9 bảng dữ liệu, số dòng, số cột và vai trò từng bảng.
- [x] Xác định quan hệ khóa giữa các bảng:
  - `orders.customer_id` -> `customers.customer_id`
  - `order_items.order_id` -> `orders.order_id`
  - `order_items.product_id` -> `products.product_id`
  - `order_items.seller_id` -> `sellers.seller_id`
  - `payments.order_id` -> `orders.order_id`
  - `reviews.order_id` -> `orders.order_id`
  - `products.product_category_name` -> `product_category_name_translation.product_category_name`
- [x] Ghi rõ các vấn đề dữ liệu: missing timestamp, missing product category, missing review comment, một order có thể có nhiều item/payment.

### 4.3. EDA

Notebook chính: `notebooks/01_EDA.ipynb`.

- [x] Thống kê tổng quan từng bảng: shape, columns, missing, duplicate.
- [x] Phân tích đơn hàng theo thời gian.
- [x] Phân tích trạng thái đơn hàng.
- [x] Phân tích doanh thu theo tháng/category/state.
- [x] Phân tích payment type và installments.
- [x] Phân tích delivery days, delay days và delay rate.
- [x] Phân tích review score và bad review.
- [x] Tạo các bảng tổng hợp để đưa vào report và dashboard.

### 4.4. Tiền xử lý và feature engineering

Notebook chính: `notebooks/02_Preprocessing.ipynb`.
Code chính: `src/etl/transform.py`.

- [x] Chuyển timestamp sang datetime.
- [x] Chuyển tiền, số lượng, kích thước sang numeric.
- [x] Xử lý missing product category bằng `unknown`.
- [x] Điền missing product dimension bằng median.
- [x] Join category translation để có tên category tiếng Anh.
- [x] Tạo bảng order-level cho EDA, ML và dashboard.
- [x] Tạo feature:
  - `delivery_days`
  - `approval_hours`
  - `carrier_days`
  - `delay_days`
  - `is_delayed`
  - `order_year_month`
  - `order_month`
  - `order_day_of_week`
  - `item_count`
  - `total_price`
  - `total_freight`
  - `freight_ratio`
  - `payment_type`
  - `max_installments`
  - `customer_state`
  - `seller_state`
  - `product_category_name_english`
- [x] Tạo target `bad_review`: 1 nếu `review_score <= 2`, 0 nếu `review_score >= 4`.
- [x] Lưu output vào `data/processed/`.

### 4.5. Data warehouse

Notebook chính: `notebooks/03_DWH_and_Iceberg_Cube.ipynb`.
Code chính: `src/etl/load.py`.

- [x] Không dùng SQLite.
- [x] Hỗ trợ PostgreSQL và SQL Server qua SQLAlchemy.
- [x] Tạo star schema:
  - `fact_order_items`
  - `dim_date`
  - `dim_customer`
  - `dim_seller`
  - `dim_product`
  - `dim_payment`
  - `dim_order_status`
- [x] Fact table có grain: 1 dòng = 1 item trong 1 order.
- [x] Measures chính: `price`, `freight_value`, `review_score`, `delivery_days`, `delay_days`, `is_delayed`, `bad_review`.
- [x] Viết script `scripts/load_warehouse.py` để load warehouse vào database.
- [x] Đã load thành công vào PostgreSQL `olist_dwh`.

### 4.6. Iceberg Cube

Code chính: `src/olap/iceberg_cube.py`.

- [x] Thay placeholder bằng thuật toán thật.
- [x] Hỗ trợ nhiều dimension và tính cube cho mọi tổ hợp dimension không rỗng.
- [x] Hỗ trợ các measure:
  - `count_orders`
  - `sum_revenue`
  - `avg_review_score`
  - `avg_delivery_days`
  - `delay_rate`
  - `bad_review_rate`
- [x] Có threshold iceberg:
  - `count_orders >= min_count`
  - hoặc `sum_revenue >= min_revenue`
  - hoặc `bad_review_rate >= high_bad_review_rate` với support đủ lớn.
- [x] Tính cube theo 4 chủ đề:
  - doanh thu theo thời gian/category/state;
  - chất lượng giao hàng theo seller state/category/delay;
  - mức độ hài lòng theo payment/installments/review group;
  - trade lane theo customer state/seller state/review group.
- [x] Lưu kết quả vào `data/warehouse/iceberg_cube_results.csv`.

### 4.7. Khai phá dữ liệu: Classification

Notebook chính: `notebooks/04_Classification_Model.ipynb`.
Code chính: `src/models/train.py` và `src/models/predict.py`.

Bài toán: **dự đoán đơn hàng có review xấu hay không**.

- [x] Target: `bad_review`.
- [x] Feature gồm giá trị đơn hàng, phí ship, payment, category, state, delivery delay và thời gian mua hàng.
- [x] Có preprocessing pipeline cho numeric/categorical features.
- [x] Có Logistic Regression, Random Forest và HistGradientBoosting.
- [x] Model mặc định: Random Forest.
- [x] Metrics:
  - accuracy;
  - precision;
  - recall;
  - F1-score;
  - ROC-AUC;
  - confusion matrix.
- [x] Lưu model vào `models/bad_review_classifier.pkl`.

Kết quả đã train:

- Accuracy: `0.8814`
- Precision lớp bad review: `0.6799`
- Recall lớp bad review: `0.4865`
- F1 lớp bad review: `0.5672`
- ROC-AUC: `0.7953`

### 4.8. Ứng dụng web

Code chính: `app/Home.py`.

- [x] Trang overview: orders, revenue, average review, delay rate, bad review rate.
- [x] Trang EDA: doanh thu theo tháng, order status, review distribution, category, payment, state.
- [x] Trang Iceberg Cube: xem các pattern theo cube theme.
- [x] Trang Prediction: nhập thông tin đơn hàng và dự đoán xác suất review xấu.

### 4.9. API

Code chính: `api/main.py`.

- [x] `/health`
- [x] `/summary`
- [x] `/metrics`
- [x] `/cube`
- [x] `/predict`

### 4.10. Báo cáo và tài liệu

- [x] README mới.
- [x] Database setup guide.
- [x] Report khung.
- [x] Notebook cho EDA, preprocessing, DWH/Iceberg Cube và classification.
- [x] Checklist công việc.

## 5. Thứ tự chạy lại toàn bộ dự án

```powershell
.\.venv312\Scripts\Activate.ps1
python scripts/build_processed.py
python scripts/load_warehouse.py
python scripts/run_iceberg_cube.py
python scripts/train_bad_review_model.py
streamlit run app/Home.py
```

API:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Tiêu chí hoàn thành

Dự án hiện đã có:

- [x] Dataset kinh tế/thương mại điện tử rõ ràng.
- [x] Mô tả dataset đầy đủ.
- [x] EDA notebook.
- [x] Preprocessing pipeline.
- [x] Data warehouse PostgreSQL/SQL Server.
- [x] Iceberg Cube.
- [x] Classification model.
- [x] Streamlit web app.
- [x] FastAPI backend.
- [x] Report và tài liệu hướng dẫn.
- [x] Không còn `NotImplementedError` trong các module chính.
