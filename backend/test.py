import os
from sqlalchemy import create_engine, text

def quick_check():
    db_url = None
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DATABASE_URL="):
                    db_url = line.strip().split("DATABASE_URL=")[1]
                    break

    if not db_url:
        db_url = "mssql+pyodbc://sa:123@MSI/QlyTTTM?driver=ODBC+Driver+17+for+SQL+Server"

    print(f" Chuỗi kết nối đang thử: {db_url}")
    print("-" * 50)
    print(" Đang gọi kết nối trực tiếp xuống SQL Server...")
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            # Đã bọc text() ở đây
            result = connection.execute(text("SELECT @@VERSION")).fetchone()
            print("\n KẾT NỐI THÀNH CÔNG RỒI!")
            print(f"Phiên bản SQL Server đang chạy: {result[0]}")
    except Exception as e:
        print("\n KẾT NỐI THẤT BẠI!")
        print(f"Lỗi kết nối chi tiết: {e}")

if __name__ == "__main__":
    quick_check()