# Bao cao do an: Olist E-Commerce Analytics

## 1. Gioi thieu bai toan

Do an phan tich du lieu thuong mai dien tu Olist de hieu hanh vi mua hang, doanh thu, van chuyen, thanh toan va muc do hai long cua khach hang. He thong ket hop data warehouse, Iceberg Cube va classification model de ho tro phan tich kinh doanh va canh bao nguy co review xau.

## 2. Mo ta dataset

Dataset gom 9 bang CSV:

- `orders`: thong tin don hang va cac moc thoi gian.
- `customers`: thong tin vi tri khach hang.
- `order_items`: chi tiet san pham trong tung don hang.
- `order_payments`: thanh toan.
- `order_reviews`: diem review va comment.
- `products`: san pham va category.
- `sellers`: nguoi ban.
- `geolocation`: toa do theo zip code prefix.
- `product_category_name_translation`: dich category sang tieng Anh.

Quan he chinh:

- `orders.customer_id` -> `customers.customer_id`
- `order_items.order_id` -> `orders.order_id`
- `order_items.product_id` -> `products.product_id`
- `order_items.seller_id` -> `sellers.seller_id`
- `order_payments.order_id` -> `orders.order_id`
- `order_reviews.order_id` -> `orders.order_id`
- `products.product_category_name` -> `product_category_name_translation.product_category_name`

## 3. EDA

Can trinh bay cac nhom phan tich:

- Don hang theo thoi gian.
- Doanh thu theo thang, category, state va seller.
- Phan bo order status.
- Phan bo payment type va installments.
- Delivery days, delay days va delay rate.
- Review score va lien he giua delivery delay voi review xau.

## 4. Tien xu ly

Cac thao tac da thiet ke trong pipeline:

- Chuyen timestamp sang datetime.
- Chuyen cot tien va so luong sang numeric.
- Xu ly missing product category bang `unknown`.
- Dien missing product dimension bang median.
- Tong hop item/payment/review ve muc order-level.
- Tao feature: `delivery_days`, `delay_days`, `is_delayed`, `freight_ratio`, `item_count`, `order_month`, `order_day_of_week`.
- Tao target `bad_review` tu `review_score`.

## 5. Data Warehouse

Warehouse dung PostgreSQL hoac SQL Server, khong dung SQLite.

Star schema:

- Fact: `fact_order_items`
- Dimensions: `dim_date`, `dim_customer`, `dim_seller`, `dim_product`, `dim_payment`, `dim_order_status`

Grain cua fact table: 1 dong = 1 item trong 1 order.

Measures:

- `price`
- `freight_value`
- `review_score`
- `delivery_days`
- `delay_days`
- `is_delayed`
- `bad_review`

## 6. Iceberg Cube

Iceberg Cube giu lai cac nhom tong hop co y nghia theo threshold:

- `count_orders >= 100`
- hoac `sum_revenue >= 10000/15000`
- hoac `bad_review_rate >= 0.25` voi support du lon

Cac chu de cube:

- Doanh thu theo thoi gian, category, state.
- Chat luong giao hang theo seller state, category, delay.
- Muc do hai long theo payment type va installments.
- Trade lane theo customer state va seller state.

## 7. Classification

Bai toan: du doan don hang co review xau hay khong.

Target:

- `bad_review = 1` neu `review_score <= 2`.
- `bad_review = 0` neu `review_score >= 4`.
- Loai review 3 sao khi train.

Model:

- Logistic Regression baseline.
- Random Forest model mac dinh.
- Co the thu HistGradientBoosting.

Metrics:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

## 8. Ung dung

Streamlit app gom:

- Overview dashboard.
- EDA dashboard.
- Iceberg Cube explorer.
- Prediction form cho bad review risk.

FastAPI gom:

- `/health`
- `/summary`
- `/metrics`
- `/cube`
- `/predict`

## 9. Ket luan

Do an da chuyen tu scaffold Reddit sang mot pipeline phan tich Olist day du hon, bam sat yeu cau mon hoc: dataset kinh te, EDA, preprocessing, data warehouse, Iceberg Cube, classification va web app.
