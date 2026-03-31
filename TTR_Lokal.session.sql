CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spieler1_id INT,
    spieler2_id INT,
    satz_score_s1 INT,
    satz_score_s2 INT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (spieler1_id) REFERENCES spieler(id),
    FOREIGN KEY (spieler2_id) REFERENCES spieler(id)
)

