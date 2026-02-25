import sqlite3

conn = sqlite3.connect("techstore.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE product_ratings ADD COLUMN comment TEXT;")
conn.commit()
conn.close()
print("Colonne 'comment' ajoutée à la table product_ratings.")
