import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="Pat@3400Roy", database="ttr_db"
    )

def berechne_statistik(spieler_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Zählen, wie oft der Spieler als spieler1 oder spieler2 gewonnen hat
    query = """
    SELECT count(*) FROM matches 
    WHERE (spieler1_id = %s AND satz_score_s1 > satz_score_s2)
       OR (spieler2_id = %s AND satz_score_s2 > satz_score_s1)
    """
    
    cursor.execute(query, (spieler_id, spieler_id))
    gewonnene_spiele = cursor.fetchone()[0]
    
    print(f"Spieler {spieler_id} hat {gewonnene_spiele} Spiele gewonnen.")
    conn.close()

# --- 5. DATEN LADEN (Konsistenz-Check) ---
def alle_spieler_anzeigen():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spieler")
    ergebnisse = cursor.fetchall()
    conn.close()
    
    print("\n--- GESPEICHERTE SPIELER ---")
    for spieler in ergebnisse:
        # spieler ist ein Tupel: (id, vorname, nachname)
        print(f"ID: {spieler[0]} | Name: {spieler[1]} {spieler[2]}")
    return ergebnisse

def turnier_ergebnisse_anzeigen(turnier_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Wir holen uns die Namen der Spieler und das Ergebnis
    sql = """
        SELECT m.id, s1.nachname, s2.nachname, m.satz_score_s1, m.satz_score_s2
        FROM matches m
        JOIN spieler s1 ON m.spieler1_id = s1.id
        JOIN spieler s2 ON m.spieler2_id = s2.id
        WHERE m.turnier_id = %s
    """
    cursor.execute(sql, (turnier_id,))
    matches = cursor.fetchall()
    conn.close()

    print(f"\n--- ERGEBNISSE FÜR TURNIER {turnier_id} ---")
    for m in matches:
        print(f"Match {m[0]}: {m[1]} vs {m[2]} -> {m[3]}:{m[4]}")


# --- 6. SICHERE EINGABE MIT VALIDIERUNG ---
def match_speichern_sicher(turnier_id, s1_id, s2_id, score_s1, score_s2):
    # 1. Validierung: Sind die Punkte Zahlen?
    if not isinstance(score_s1, int) or not isinstance(score_s2, int):
        print(f"[FEHLER] Die Satz-Scores müssen Zahlen sein! Eingabe war: {score_s1}:{score_s2}")
        return # Abbruch
    
    # 2. Validierung: Sind die Punkte positiv?
    if score_s1 < 0 or score_s2 < 0:
        print("[FEHLER] Negative Punkte sind nicht erlaubt.")
        return # Abbruch

    # 3. Wenn alles ok ist -> Speichern
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO matches (turnier_id, spieler1_id, spieler2_id, satz_score_s1, satz_score_s2) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (turnier_id, s1_id, s2_id, score_s1, score_s2))
        conn.commit()
        conn.close()
        print(f"[OK] Match erfolgreich gespeichert.")
        
    except mysql.connector.Error as err:
        print(f"[DATENBANK-FEHLER] Das Match konnte nicht gespeichert werden: {err}")


# --- TESTLAUF FÜR ABSCHLUSSKRITERIEN ---
if __name__ == "__main__":
    print("--- TESTPHASE 1: EINGABE & VALIDIERUNG ---")
    # Wir testen eine FALSCHE Eingabe (Text statt Zahl)
    match_speichern_sicher(1, 1, 2, "Drei", 1) 
    
    # Wir testen eine KORREKTE Eingabe
    # Hinweis: Stellen Sie sicher, dass Turnier ID 1 und Spieler 1 & 2 existieren!
    match_speichern_sicher(1, 1, 2, 3, 0)

    print("\n--- TESTPHASE 2: KONSISTENZ (NEUSTART SIMULATION) ---")
    # Jetzt lesen wir die Daten aus der Datenbank
    alle_spieler_anzeigen()
    turnier_ergebnisse_anzeigen(1)
    
    print("\n--- ALTE STATISTIK-FUNKTION ---")
    berechne_statistik(1)