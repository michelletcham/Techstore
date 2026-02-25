import sqlite3

conn = sqlite3.connect("techstore.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS product_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    user_id INTEGER,
    rating INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")
conn.commit()
conn.close()
print("Table 'product_ratings' créée.")
