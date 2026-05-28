# Phân chia file theo GitHub Project tasks

Mục tiêu hiện tại: GitHub chỉ giữ phần nền tảng và các file thuộc task của Tommyhuy1705. Các folder của task thành viên khác vẫn được giữ bằng `.gitkeep` để từng bạn tự thêm/push code của mình và close issue tương ứng.

## Tommyhuy1705

### #1 Setup Repository & Môi trường

- `README.md`
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `src/config.py`
- cấu trúc thư mục project

### #2 Khám phá dữ liệu (EDA)

- `notebooks/01_EDA.ipynb`

### #3 Tiền xử lý & Feature Engineering

- `notebooks/02_Preprocessing.ipynb`
- `src/etl/transform.py`

### #4 Thiết kế Lược đồ DWH (Star Schema)

- `src/etl/transform.py`, hàm `build_star_schema`
- `src/etl/load.py`
- `docs/database_setup.md`
- `notebooks/03_DWH_and_Iceberg_Cube.ipynb` phần DWH

### #5 Viết script ETL & Load data

- `src/etl/extract.py`
- `src/etl/load.py`
- `scripts/build_processed.py`
- `scripts/load_warehouse.py`

## Sura3607

### #6 Tính toán Iceberg Cube

Folder/file sẽ tự thêm lại:

- `src/olap/iceberg_cube.py`
- `src/olap/__init__.py`
- `scripts/run_iceberg_cube.py`
- phần Iceberg Cube trong notebook DWH/cube nếu cần

Commit/PR nên ghi:

```text
Closes #6
```

### #7 Huấn luyện Baseline Model

Folder/file sẽ tự thêm lại:

- `src/models/train.py`
- `src/models/__init__.py`
- `notebooks/04_Classification_Model.ipynb`

Commit/PR nên ghi:

```text
Closes #7
```

## trongjhuongwr

### #8 Tối ưu hóa mô hình

Folder/file sẽ tự thêm lại hoặc chỉnh sau task baseline:

- `src/models/train.py`
- `notebooks/04_Classification_Model.ipynb`

Commit/PR nên ghi:

```text
Closes #8
```

### #9 Đóng gói mô hình (API)

Folder/file sẽ tự thêm lại:

- `api/main.py`
- `api/requirements.txt`
- `src/models/predict.py`

Commit/PR nên ghi:

```text
Closes #9
```

## xuandongg1801

### #10 Làm website

Folder/file sẽ tự thêm lại:

- `app/Home.py`
- `app/requirements.txt`

Commit/PR nên ghi:

```text
Closes #10
```

## Task chung

### #11 Viết báo cáo luận

- `docs/report/olist_report.md`
- `docs/images/`

Commit/PR nên ghi:

```text
Closes #11
```

### #12 Slide

- `docs/slides/`

Commit/PR nên ghi:

```text
Closes #12
```

## Lưu ý workflow

Nếu các item trong GitHub Project là Issue thật, GitHub sẽ tự close khi commit/PR merge có cú pháp `Closes #<issue_number>`. Nếu đó là draft item, cần convert thành Issue trước.

Khuyến nghị mỗi bạn làm trên một branch riêng:

- `task/06-iceberg-cube`
- `task/07-baseline-model`
- `task/08-model-optimization`
- `task/09-api`
- `task/10-streamlit-app`
- `task/11-report`
- `task/12-slides`
