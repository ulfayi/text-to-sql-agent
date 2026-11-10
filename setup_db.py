import sqlite3

def create_database():
    conn = sqlite3.connect("sayad_parfum.db")
    cursor = conn.cursor()

    # Köhnə cədvəllər varsa təmizləyək (təkrar işlədəndə xəta verməsin)
    cursor.executescript("""
        DROP TABLE IF EXISTS sale_items;
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS perfumes;
    """)

    # 1. Ətirlər (Məhsullar) cədvəli
    cursor.execute("""
    CREATE TABLE perfumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,           -- Ətirin adı (məs: Kirke, Sauvage)
        brand TEXT NOT NULL,          -- Brend (məs: Tiziana Terenzi, Dior)
        category TEXT NOT NULL,       -- Kişi, Qadın, Unisex
        cost_per_gram REAL NOT NULL,  -- 1 qram yağın maya dəyəri (AZN)
        price_per_gram REAL NOT NULL, -- 1 qram yağın satış qiyməti (AZN)
        stock_grams REAL NOT NULL     -- Anbarda qalan yağ miqdarı (qramla)
    );
    """)

    # 2. Müştərilər cədvəli
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT,
        created_at DATE NOT NULL
    );
    """)

    # 3. Satışlar (Qəbzlər) cədvəli
    cursor.execute("""
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,          -- Qeydiyyatsız müştəridirsə NULL ola bilər
        sale_date DATETIME NOT NULL,  -- Satış tarixi (YYYY-MM-DD HH:MM:SS)
        payment_method TEXT NOT NULL, -- 'Nağd' və ya 'Kart'
        discount_azn REAL DEFAULT 0,  -- Ümumi qəbzə edilən endirim (AZN)
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """)

    # 4. Satış Detalları (Qəbzdəki məhsullar) cədvəli
    cursor.execute("""
    CREATE TABLE sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        perfume_id INTEGER NOT NULL,
        grams_sold REAL NOT NULL,     -- Satılan yağ miqdarı (qramla)
        bottle_size_ml INTEGER,       -- Flakon ölçüsü (15, 30, 50 ml)
        item_total_azn REAL NOT NULL, -- Bu sətir üzrə yekun qiymət (qram * qiymət)
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (perfume_id) REFERENCES perfumes(id)
    );
    """)

    # Nümunə Məlumatlar (Sample Data)
    cursor.executemany("""
        INSERT INTO perfumes (name, brand, category, cost_per_gram, price_per_gram, stock_grams)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("Kirke", "Tiziana Terenzi", "Unisex", 0.80, 2.50, 450.0),
        ("Baccarat Rouge 540", "Maison Francis Kurkdjian", "Unisex", 1.20, 3.50, 280.0),
        ("Sauvage", "Dior", "Kişi", 0.60, 1.80, 620.0),
        ("Black Afgano", "Nasomatto", "Unisex", 1.10, 3.00, 150.0),
        ("Good Girl", "Carolina Herrera", "Qadın", 0.55, 1.60, 390.0),
        ("Aventus", "Creed", "Kişi", 0.95, 2.80, 95.0)
    ])

    cursor.executemany("""
        INSERT INTO customers (full_name, phone, created_at)
        VALUES (?, ?, ?)
    """, [
        ("Elvin Məmmədov", "050-111-22-33", "2026-09-10"),
        ("Aysel Həsənova", "055-444-55-66", "2026-10-01"),
        ("Rəşad Quliyev", "070-777-88-99", "2026-10-15")
    ])

    cursor.executemany("""
        INSERT INTO sales (customer_id, sale_date, payment_method, discount_azn)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "2026-11-01 14:20:00", "Nağd", 2.0),
        (2, "2026-11-03 18:10:00", "Kart", 0.0),
        (None, "2026-11-05 11:45:00", "Nağd", 0.0),
        (1, "2026-11-08 16:30:00", "Kart", 5.0),
        (3, "2026-11-09 13:00:00", "Nağd", 0.0)
    ])

    cursor.executemany("""
        INSERT INTO sale_items (sale_id, perfume_id, grams_sold, bottle_size_ml, item_total_azn)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 1, 10.0, 30, 25.0),  # 10qr Kirke = 25 AZN
        (1, 3, 5.0, 15, 9.0),    # 5qr Sauvage = 9 AZN
        (2, 2, 10.0, 30, 35.0),  # 10qr Baccarat = 35 AZN
        (3, 5, 15.0, 30, 24.0),  # 15qr Good Girl = 24 AZN
        (4, 4, 20.0, 50, 60.0),  # 20qr Black Afgano = 60 AZN
        (5, 6, 10.0, 30, 28.0)   # 10qr Aventus = 28 AZN
    ])

    conn.commit()
    conn.close()
    print("✅ sayad_parfum.db uğurla yaradıldı və məlumatlarla dolduruldu!")

if __name__ == "__main__":
    create_database()