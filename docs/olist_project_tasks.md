# Ke hoach hoan thien do an voi Olist Brazilian E-Commerce Dataset

## 1. Muc tieu chuyen huong de tai

De tai moi nen trinh bay theo huong:

**Xay dung data warehouse va khai pha du lieu thuong mai dien tu tren bo du lieu Olist Brazilian E-Commerce, ket hop Iceberg Cube va mo hinh du doan muc do hai long cua khach hang.**

Bo du lieu moi phu hop hon chu de kinh te/kinh doanh vi mo ta qua trinh van hanh san thuong mai dien tu: don hang, khach hang, nguoi ban, san pham, thanh toan, van chuyen, review va vi tri dia ly.

## 2. Tong quan dataset da doc trong thu muc `dataset/`

Dataset hien co gom 9 file CSV:

| File | So dong | So cot | Vai tro |
|---|---:|---:|---|
| `olist_orders_dataset.csv` | 99,441 | 8 | Bang don hang, trang thai va cac moc thoi gian xu ly/giao hang |
| `olist_customers_dataset.csv` | 99,441 | 5 | Thong tin khach hang, city/state/zip prefix |
| `olist_order_items_dataset.csv` | 112,650 | 7 | Chi tiet san pham trong don hang, seller, gia va phi van chuyen |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Phuong thuc thanh toan, so lan tra gop, gia tri thanh toan |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Diem danh gia va noi dung review |
| `olist_products_dataset.csv` | 32,951 | 9 | Thong tin san pham, danh muc, kich thuoc, khoi luong |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Thong tin nguoi ban, city/state/zip prefix |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | Vi do/kinh do theo zip code prefix |
| `product_category_name_translation.csv` | 71 | 2 | Dich ten danh muc san pham tu tieng Bo Dao Nha sang tieng Anh |

Mot so thong tin nen dua vao bao cao:

- Khoang thoi gian don hang: tu `2016-09-04 21:15:19` den `2018-10-17 17:30:18`.
- Phan bo trang thai don hang:
  - delivered: 96,478
  - shipped: 1,107
  - canceled: 625
  - unavailable: 609
  - invoiced: 314
  - processing: 301
  - created: 5
  - approved: 2
- Phan bo thanh toan:
  - credit_card: 76,795
  - boleto: 19,784
  - voucher: 5,775
  - debit_card: 1,529
  - not_defined: 3
- Phan bo review score:
  - 5 sao: 57,328
  - 4 sao: 19,142
  - 3 sao: 8,179
  - 2 sao: 3,151
  - 1 sao: 11,424
- Bang `orders` co missing o cac cot thoi gian:
  - `order_approved_at`: 160
  - `order_delivered_carrier_date`: 1,783
  - `order_delivered_customer_date`: 2,965
- Bang `products` co 610 san pham thieu category/name/description/photo, va 2 san pham thieu thong tin kich thuoc/khoi luong.
- Bang `reviews` thieu nhieu comment text, nhung `review_score` van du de lam bai toan classification.

## 3. Cac loi/thieu sot cua phien ban Reddit can khac phuc

Repo hien tai moi co khung, can khac phuc cac diem sau:

- README dang bi loi encoding tieng Viet va noi dung van theo de tai Reddit.
- `data/raw`, `data/processed`, `data/warehouse` chua co du lieu dau ra.
- Notebook `01_EDA.ipynb` chi co tieu de/import, chua co phan tich.
- Notebook `02_Preprocessing.ipynb`, `03_DWH_and_Iceberg_Cube.ipynb`, `04_Classification_Model.ipynb` chi co markdown placeholder.
- `src/olap/iceberg_cube.py` chua cai dat thuat toan, dang `NotImplementedError`.
- `src/models/train.py` chua huan luyen model, dang `NotImplementedError`.
- Streamlit app moi co title placeholder.
- FastAPI moi co endpoint `/health`.

## 4. Cong viec can lam de dap ung day du yeu cau cua thay

### 4.1. Cap nhat cau truc va README

- [ ] Doi ten/mo ta du an tu Reddit sang Olist E-Commerce Analytics.
- [ ] Sua loi encoding tieng Viet trong README.
- [ ] Bo sung mo ta day du dataset:
  - nguon dataset Kaggle;
  - chu de kinh te/thuong mai dien tu;
  - so file, so dong, so cot;
  - y nghia tung bang;
  - khoa chinh/khoa ngoai;
  - khoang thoi gian;
  - cac bien quan trong;
  - muc tieu phan tich va bai toan khai pha.
- [ ] Cap nhat huong dan chay pipeline, notebook, API va Streamlit app.
- [ ] Dua cac file CSV vao dung quy uoc `data/raw/` hoac cap nhat code de dung thu muc `dataset/` hien tai.

### 4.2. Mo ta day du bo du lieu

Can tao phan rieng trong report/notebook:

- [ ] Mo ta business context: marketplace Olist ket noi seller voi customer tai Brazil.
- [ ] Ve ERD quan he giua cac bang:
  - `orders.customer_id` -> `customers.customer_id`
  - `order_items.order_id` -> `orders.order_id`
  - `order_items.product_id` -> `products.product_id`
  - `order_items.seller_id` -> `sellers.seller_id`
  - `payments.order_id` -> `orders.order_id`
  - `reviews.order_id` -> `orders.order_id`
  - customer/seller zip prefix -> geolocation zip prefix
  - `products.product_category_name` -> translation table
- [ ] Lap data dictionary cho tung bang.
- [ ] Ghi ro cac van de du lieu:
  - missing delivery timestamps;
  - missing product category;
  - review comments thieu nhieu;
  - mot order co the co nhieu item;
  - mot order co the co nhieu payment records;
  - review co the duplicate theo order va can xu ly.

### 4.3. EDA can thuc hien

Notebook chinh: `notebooks/01_EDA.ipynb`.

- [ ] Thong ke tong quan tung bang: shape, columns, missing, duplicate, unique keys.
- [ ] Phan tich don hang theo thoi gian:
  - so don theo thang;
  - doanh thu theo thang;
  - xu huong tang/giam theo nam 2016-2018.
- [ ] Phan tich trang thai don hang:
  - ti le delivered/canceled/shipped/unavailable;
  - so sanh doanh thu theo status.
- [ ] Phan tich doanh thu:
  - tong `price`, `freight_value`, `payment_value`;
  - top category theo doanh thu;
  - top seller theo doanh thu;
  - top state theo doanh thu.
- [ ] Phan tich thanh toan:
  - phan bo `payment_type`;
  - so lan tra gop `payment_installments`;
  - gia tri thanh toan trung binh theo payment type.
- [ ] Phan tich van chuyen:
  - delivery duration = delivered_customer_date - purchase_timestamp;
  - estimated delivery duration = estimated_delivery_date - purchase_timestamp;
  - delay_days = delivered_customer_date - estimated_delivery_date;
  - delayed_flag = delay_days > 0;
  - delay rate theo state/category/seller.
- [ ] Phan tich review:
  - phan bo review score;
  - review score theo category;
  - review score theo delivery delay;
  - review score theo payment type/freight/price.
- [ ] Phan tich dia ly:
  - top customer states/cities;
  - top seller states/cities;
  - ban do hoac chart phan bo doanh thu theo state.
- [ ] Ket luan EDA bang cac insight ro rang, khong chi hien chart.

### 4.4. Tien xu ly va feature engineering

Notebook chinh: `notebooks/02_Preprocessing.ipynb`.
Code nen dua vao `src/etl/transform.py`.

- [ ] Chuyen cac cot timestamp sang datetime.
- [ ] Chuyen cac cot tien/so luong/kich thuoc sang numeric.
- [ ] Xu ly missing:
  - product category thieu -> `unknown`;
  - product dimension thieu -> median theo category hoac median toan bo;
  - delivery timestamp thieu -> giu lai cho EDA status, nhung loai khoi model neu khong delivered;
  - review comment missing -> khong dung text trong model ban dau.
- [ ] Join category translation de co category tieng Anh.
- [ ] Tao bang order-level da flatten cho ML:
  - moi dong la 1 order;
  - aggregate item count, total price, total freight;
  - aggregate payment value, payment type chinh, installments;
  - join customer/seller/product/category/review.
- [ ] Tao feature:
  - `delivery_days`;
  - `approval_hours`;
  - `carrier_days`;
  - `delay_days`;
  - `is_delayed`;
  - `order_month`, `order_year`, `order_day_of_week`;
  - `item_count`;
  - `total_price`;
  - `total_freight`;
  - `freight_ratio`;
  - `payment_installments`;
  - `customer_state`;
  - `seller_state`;
  - `product_category_name_english`.
- [ ] Tao target classification:
  - khuyen nghi: `bad_review = 1` neu `review_score <= 2`, `bad_review = 0` neu `review_score >= 4`;
  - co the bo `review_score = 3` de target ro hon.
- [ ] Luu output:
  - `data/processed/orders_clean.csv`;
  - `data/processed/order_features.csv`;
  - `data/processed/model_dataset.csv`.

### 4.5. Xay dung data warehouse

Notebook chinh: `notebooks/03_DWH_and_Iceberg_Cube.ipynb`.
Code nen dua vao `src/etl/load.py`.

Thiet ke star schema de thay ro phan DWH:

- [ ] `fact_order_items`
  - grain: 1 dong = 1 item trong 1 order;
  - measures: `price`, `freight_value`, `payment_value_allocated`, `delivery_days`, `delay_days`, `review_score`;
  - keys: `order_key`, `date_key`, `customer_key`, `seller_key`, `product_key`, `payment_key`, `status_key`.
- [ ] `dim_date`
  - date, year, quarter, month, day, day_of_week.
- [ ] `dim_customer`
  - customer_id, customer_unique_id, zip_prefix, city, state, lat/lng neu aggregate geolocation.
- [ ] `dim_seller`
  - seller_id, zip_prefix, city, state, lat/lng neu aggregate geolocation.
- [ ] `dim_product`
  - product_id, category_name, category_english, weight, length, height, width.
- [ ] `dim_payment`
  - payment_type, installments_group.
- [ ] `dim_order_status`
  - order_status.
- [ ] Luu warehouse vao SQLite:
  - `data/warehouse/olist_warehouse.db`.
- [ ] Viet SQL kiem tra:
  - tong doanh thu theo thang;
  - doanh thu theo category/state;
  - delay rate theo seller_state;
  - review trung binh theo category;
  - top seller/category/customer_state.

### 4.6. Cai dat Iceberg Cube

Code chinh: `src/olap/iceberg_cube.py`.

Can thay placeholder bang ham that:

- [ ] Input:
  - DataFrame hoac bang tu warehouse;
  - danh sach dimensions;
  - measure;
  - aggregate functions;
  - support threshold.
- [ ] Output:
  - DataFrame gom cac cuboid thoa dieu kien iceberg.
- [ ] Ho tro cac aggregate:
  - `count_orders`;
  - `sum_revenue`;
  - `avg_review_score`;
  - `avg_delivery_days`;
  - `delay_rate`;
  - `bad_review_rate`.
- [ ] Chay cube theo cac chu de:
  - `month x category x customer_state`;
  - `seller_state x category x delayed_flag`;
  - `payment_type x installments_group x review_group`;
  - `customer_state x seller_state x delivery_status`.
- [ ] Dieu kien iceberg:
  - `count_orders >= 100`, hoac
  - `sum_revenue >= 10000`, hoac
  - `bad_review_rate >= 0.25` voi `count_orders >= 50`.
- [ ] Luu ket qua:
  - `data/warehouse/iceberg_cube_results.csv`;
  - hoac table `iceberg_cube_results` trong SQLite.
- [ ] Trinh bay trong notebook:
  - giai thich concept iceberg cube;
  - so sanh cube day du voi cube da loc threshold;
  - liet ke top pattern kinh doanh dang chu y.

### 4.7. Khai pha du lieu: Classification

Notebook chinh: `notebooks/04_Classification_Model.ipynb`.
Code nen dua vao `src/models/train.py` va `src/models/predict.py`.

Bai toan khuyen nghi:

**Du doan don hang co review xau hay khong.**

Target:

- `bad_review = 1` neu `review_score <= 2`.
- `bad_review = 0` neu `review_score >= 4`.
- Loai `review_score = 3` khoi tap train/evaluate de tranh nhan trung tinh.

Feature nen dung:

- `total_price`
- `total_freight`
- `freight_ratio`
- `payment_type`
- `payment_installments`
- `item_count`
- `product_category_name_english`
- `customer_state`
- `seller_state`
- `delivery_days`
- `delay_days`
- `is_delayed`
- `order_month`
- `order_day_of_week`

Model can thu:

- [ ] Baseline: Logistic Regression.
- [ ] Tree-based: Random Forest.
- [ ] Gradient Boosting hoac HistGradientBoostingClassifier neu muon nang diem.

Danh gia:

- [ ] Train/test split co stratify.
- [ ] Xu ly class imbalance bang `class_weight='balanced'` hoac resampling.
- [ ] Metrics:
  - accuracy;
  - precision;
  - recall;
  - F1-score;
  - ROC-AUC;
  - confusion matrix.
- [ ] Giai thich model:
  - feature importance;
  - nhan xet yeu to nao lam tang nguy co review xau.
- [ ] Luu model:
  - `models/bad_review_classifier.pkl`.

### 4.8. Ung dung web

Khuyen nghi dung Streamlit vi repo da co `app/Home.py`.

Can bien app tu placeholder thanh dashboard that:

- [ ] Trang tong quan:
  - tong so order;
  - tong doanh thu;
  - review trung binh;
  - delay rate;
  - bad review rate.
- [ ] Trang EDA:
  - doanh thu theo thang;
  - don hang theo status;
  - payment type;
  - review distribution;
  - top category/seller/state.
- [ ] Trang warehouse/OLAP:
  - filter theo thoi gian/category/state;
  - hien ket qua Iceberg Cube;
  - bang top pattern can chu y.
- [ ] Trang du doan:
  - form nhap thong tin order;
  - goi model da train;
  - tra ve xac suat `bad_review`;
  - hien giai thich ngan gon.
- [ ] Neu co API:
  - FastAPI endpoint `/predict`;
  - endpoint `/metrics`;
  - endpoint `/cube`.

### 4.9. Bao cao va slide

- [ ] Viet report trong `docs/report.md` hoac file Word/PDF.
- [ ] Noi dung report can co:
  - gioi thieu bai toan;
  - mo ta dataset;
  - EDA va insight;
  - tien xu ly;
  - DWH schema;
  - Iceberg Cube;
  - Classification;
  - Web app;
  - ket luan va huong phat trien.
- [ ] Tao hinh:
  - ERD;
  - star schema;
  - pipeline architecture;
  - bieu do EDA;
  - confusion matrix;
  - screenshot app.
- [ ] Slide seminar nen tap trung vao:
  - vi sao chon dataset kinh te/thuong mai dien tu;
  - thiet ke DWH;
  - co che Iceberg Cube;
  - ket qua model;
  - demo app.

## 5. Thu tu thuc hien khuyen nghi

1. Chuyen repo tu Reddit sang Olist trong README, ten app, API title va notebook title.
2. Dua dataset vao dung thu muc raw va tao script load du lieu.
3. Hoan thien notebook `01_EDA.ipynb`.
4. Hoan thien preprocessing va tao `model_dataset.csv`.
5. Thiet ke va build SQLite data warehouse.
6. Cai dat Iceberg Cube va sinh ket qua cube.
7. Train model classification bad review.
8. Nang cap Streamlit app thanh dashboard + prediction app.
9. Viet report, tao slide va screenshot demo.
10. Chay lai toan bo pipeline de dam bao co output that, khong con placeholder.

## 6. Tieu chi hoan thanh

Do an chi nen xem la dat khi co day du cac artifact sau:

- [ ] README moi khong con noi dung Reddit.
- [ ] Data dictionary va mo ta dataset day du.
- [ ] Notebook EDA co chart, insight va ket luan.
- [ ] Notebook preprocessing co output file trong `data/processed/`.
- [ ] SQLite warehouse trong `data/warehouse/`.
- [ ] Star schema/ERD trong report.
- [ ] Iceberg Cube chay duoc va co ket qua cu the.
- [ ] Model classification co metrics va file model da luu.
- [ ] Streamlit app chay duoc va hien dashboard/prediction.
- [ ] Report/slide co anh minh hoa va ket qua thuc nghiem.
- [ ] Khong con `NotImplementedError` trong cac module chinh.
