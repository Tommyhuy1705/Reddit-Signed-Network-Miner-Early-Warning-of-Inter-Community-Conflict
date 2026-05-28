# Báo cáo đồ án: Olist E-Commerce Analytics

## 1. Giới thiệu bài toán

Đồ án phân tích dữ liệu thương mại điện tử Olist để hiểu hành vi mua hàng, doanh thu, vận chuyển, thanh toán và mức độ hài lòng của khách hàng. Hệ thống kết hợp data warehouse, Iceberg Cube và classification model để hỗ trợ phân tích kinh doanh và cảnh báo nguy cơ review xấu.

## 2. Mô tả dataset

Dataset gồm 9 bảng CSV:

- `orders`: thông tin đơn hàng và các mốc thời gian.
- `customers`: thông tin vị trí khách hàng.
- `order_items`: chi tiết sản phẩm trong từng đơn hàng.
- `order_payments`: thanh toán.
- `order_reviews`: điểm review và comment.
- `products`: sản phẩm và category.
- `sellers`: người bán.
- `geolocation`: tọa độ theo zip code prefix.
- `product_category_name_translation`: dịch category sang tiếng Anh.

Quan hệ chính:

- `orders.customer_id` -> `customers.customer_id`
- `order_items.order_id` -> `orders.order_id`
- `order_items.product_id` -> `products.product_id`
- `order_items.seller_id` -> `sellers.seller_id`
- `order_payments.order_id` -> `orders.order_id`
- `order_reviews.order_id` -> `orders.order_id`
- `products.product_category_name` -> `product_category_name_translation.product_category_name`

## 3. EDA

Các nhóm phân tích chính:

- Đơn hàng theo thời gian.
- Doanh thu theo tháng, category, state và seller.
- Phân bố order status.
- Phân bố payment type và installments.
- Delivery days, delay days và delay rate.
- Review score và liên hệ giữa giao hàng trễ với review xấu.

## 4. Tiền xử lý

Các thao tác đã thiết kế trong pipeline:

- Chuyển timestamp sang datetime.
- Chuyển cột tiền và số lượng sang numeric.
- Xử lý missing product category bằng `unknown`.
- Điền missing product dimension bằng median.
- Tổng hợp item/payment/review về mức order-level.
- Tạo feature: `delivery_days`, `delay_days`, `is_delayed`, `freight_ratio`, `item_count`, `order_month`, `order_day_of_week`.
- Tạo target `bad_review` từ `review_score`.

## 5. Data Warehouse

Warehouse dùng PostgreSQL hoặc SQL Server, không dùng SQLite.

Star schema:

- Fact: `fact_order_items`
- Dimensions: `dim_date`, `dim_customer`, `dim_seller`, `dim_product`, `dim_payment`, `dim_order_status`

Grain của fact table: 1 dòng = 1 item trong 1 order.

Measures:

- `price`
- `freight_value`
- `review_score`
- `delivery_days`
- `delay_days`
- `is_delayed`
- `bad_review`

## 6. Iceberg Cube

Iceberg Cube giữ lại các nhóm tổng hợp có ý nghĩa theo threshold:

- `count_orders >= 100`
- hoặc `sum_revenue >= 10000/15000`
- hoặc `bad_review_rate >= 0.25` với support đủ lớn

Các chủ đề cube:

- Doanh thu theo thời gian, category và state.
- Chất lượng giao hàng theo seller state, category và delay.
- Mức độ hài lòng theo payment type và installments.
- Trade lane theo customer state và seller state.

## 7. Classification

Bài toán: dự đoán đơn hàng có review xấu hay không.

Target:

- `bad_review = 1` nếu `review_score <= 2`.
- `bad_review = 0` nếu `review_score >= 4`.
- Loại review 3 sao khi train.

Model:

- Logistic Regression baseline.
- Random Forest model mặc định.
- Có thể thử HistGradientBoosting.

Metrics:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

## 8. Ứng dụng

Streamlit app gồm:

- Overview dashboard.
- EDA dashboard.
- Iceberg Cube explorer.
- Prediction form cho bad review risk.

FastAPI gồm:

- `/health`
- `/summary`
- `/metrics`
- `/cube`
- `/predict`

## 9. Kết luận

Đồ án đã chuyển từ scaffold Reddit sang một pipeline phân tích Olist đầy đủ hơn, bám sát yêu cầu môn học: dataset kinh tế, EDA, preprocessing, data warehouse, Iceberg Cube, classification và web app.
