import mysql.connector

print("Versuche Verbindung herzustellen...")

try:
    # Verbindung zur Datenbank aufbauen
    verbindung = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pat@3400Roy",
        database="ttr_db"
    )

    cursor = verbindung.cursor()
    cursor.execute("SELECT * FROM spieler")
    alle_spieler = cursor.fetchall()

    print("--- ERFOLG! ---")
    for spieler in alle_spieler:
        print(f"Spieler gefunden: {spieler[1]} {spieler[2]}")

except Exception as fehler:
    print(f"Fehler: {fehler}")