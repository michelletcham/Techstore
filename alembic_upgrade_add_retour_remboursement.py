import sqlite3

conn = sqlite3.connect("techstore.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE orders ADD COLUMN retour_statut TEXT;")
cursor.execute("ALTER TABLE orders ADD COLUMN remboursement_statut TEXT;")
conn.commit()
conn.close()
print("Colonnes 'retour_statut' et 'remboursement_statut' ajoutées à la table orders.")
