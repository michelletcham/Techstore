import sqlite3

conn = sqlite3.connect("techstore.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE products ADD COLUMN rating FLOAT;")
conn.commit()
conn.close()
print("Colonne 'rating' ajoutée à la table products.")
