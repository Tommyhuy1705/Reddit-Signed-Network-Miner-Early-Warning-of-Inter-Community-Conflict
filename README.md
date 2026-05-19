# Reddit-Signed-Network-Miner-Early-Warning-of-Inter-Community-Conflict

## 1. Giới thiệu

Dự án này nhằm phát triển một hệ thống khai phá dữ liệu trên nền tảng Reddit để phát hiện và cảnh báo sớm khả năng xung đột giữa các cộng đồng (inter-community conflict) bằng cách xây dựng mạng có dấu (signed network), tính toán Iceberg Cube để trích xuất các mẫu trọng yếu, và huấn luyện mô hình phân loại để dự đoán rủi ro.

## 2. Thành viên nhóm

| STT | Họ và Tên | Lớp | MSSV | GitHub Account |
| :--: | :-------- | :--: | :--: | :------------- |
| 1 | Trần Viết Gia Huy | CS0001 | 31231027056 | [@Tommyhuy1705](https://github.com/Tommyhuy1705) |
| 2 | Nguyễn Minh Nhựt | CS0001 | 31231022656 | [@Sura3607](https://github.com/Sura3607) |
| 3 | Nguyễn Trọng Hưởng | CS0001 | 31231023691 | [@trongjhuongwr](https://github.com/trongjhuongwr) |
| 4 | Tô Xuân Đông | CS0001 | 31231025345 | [@xuandongg1801](https://github.com/xuandongg1801) |

_(Sửa lại tên/MSSV theo nhóm của bạn)_

## 3. Cấu trúc dự án

Thư mục chính (mô tả ngắn):

```
.
├── data/
│   ├── raw/                  # Put the downloaded Reddit .tsv files here
│   ├── processed/            # Cleaned data ready for DWH/Modeling
│   └── warehouse/            # SQLite DB or exported DWH tables
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Preprocessing.ipynb
│   ├── 03_DWH_and_Iceberg_Cube.ipynb
│   └── 04_Classification_Model.ipynb
├── src/
│   ├── etl/                  # extract.py, transform.py, load.py
│   ├── olap/                 # iceberg_cube.py
│   ├── models/               # train.py, predict.py
│   └── utils/                # helpers
├── api/                      # FastAPI backend (api/main.py)
├── app/                      # Streamlit frontend (app/Home.py)
├── docs/                     # report and images
├── .gitignore
├── requirements.txt
└── README.md
```

## 4. Datasets

- Đặt tất cả file dữ liệu raw (ví dụ file .tsv từ Reddit export) vào `data/raw/`.
- Sau khi tiền xử lý, các file sạch sẽ được lưu vào `data/processed/`.
- Cơ sở dữ liệu DWH (nếu dùng SQLite) lưu trong `data/warehouse/` (ví dụ `warehouse.db`).

Ghi chú: không commit dữ liệu thô lên Git; `.gitignore` đã loại trừ `data/raw/` và `data/processed/`.

## 5. Hướng dẫn sử dụng repo

1) Tạo/ kích hoạt virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Hoặc trên macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

3) Chạy API (FastAPI):

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Kiểm tra health: truy cập `http://localhost:8000/health`.

4) Chạy Frontend (Streamlit):

```bash
streamlit run app/Home.py
```

5) Notebook & pipeline:

- Mở các notebook trong `notebooks/` theo thứ tự: EDA → Preprocessing → DWH & Iceberg → Modeling.
- Sử dụng `src/etl` để load/transform dữ liệu, `src/olap/iceberg_cube.py` để triển khai thuật toán OLAP, và `src/models` để huấn luyện/ dự đoán.

6) Lưu ý phát triển:

- Thêm file dữ liệu chỉ trong `data/raw/` và `data/processed/` chứ không commit lên Git.
- Cập nhật `requirements.txt` khi thêm thư viện mới.

---

Nếu muốn, tôi có thể:
- Cài phụ thuộc ngay vào `.venv` (chạy `pip install -r requirements.txt`).
- Khởi động server FastAPI hoặc Streamlit để kiểm thử.
