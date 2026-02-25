import sqlite3
conn = sqlite3.connect("techstore.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS product_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    media_url TEXT,
    media_type TEXT, -- 'image' ou 'video'
    FOREIGN KEY(product_id) REFERENCES products(id)
);
""")
conn.commit()
conn.close()
print("Table product_media créée.")
