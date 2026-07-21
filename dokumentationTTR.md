Table Tennis Referee
 
Inhaltsverzeichnis
1	Einleitung	3
1.1	Beschreibung	3
1.2	Motivation	3
1.3	Zielsetzung	4
2	Projektplanung	5
2.1	Muss/Kann-Ziele	5
2.2	Zeitplanung	6
2.3	Meilensteine	7
2.4	Benötigte Ressourcen	7
2.4.1	Personal	7
2.4.2	Hardware	7
2.4.3	Physische Anforderungen	7
2.5	Eingesetzte Tools und Technologien	8
2.5.1	Software-Stack	8
2.5.2	Entwicklungswerkzeuge	8
3	Umsetzung	9
3.1	Material Zusammenbau	9
3.2	Betriebssystem (OS) aufsetzen	9
3.3	Grundkonfiguration	10
3.4	Ständer 3D Drucken	11
3.5	MariaDB	12
3.5.1	Spieler-Datenbank (player)	12
3.5.2	Spiele-Datenbank (match)	13

 


1	Einleitung
1.1	Beschreibung
Das Projekt „Table Tennis Referee“ (TTR) befasst sich mit der Entwicklung eines intelligenten, modularen Systems, das als digitaler Schiedsrichter für Tischtennisspiele fungiert. Ziel ist es, die herkömmliche manuelle Zählweise durch eine moderne, automatisierte IoT-Lösung zu ersetzen, die den gesamten Umfang eines vernetzten Produkts abbildet.
Im Kern besteht das System aus einer Plattform, die Spielergebnisse, Statistiken und Turnierdaten zentral erfasst, speichert und auf einem dedizierten Smartdisplay visualisiert. Die technische Umsetzung basiert auf einem Raspberry Pi 5, der in einem massgefertigten Holzrahmen untergebracht ist und über ein 7-Zoll-Touchdisplay bedient wird.
Die Entwicklung ist in mehrere Phasen unterteilt:
-	Basis-System: Implementierung der Datenbank und eines Interfaces zur manuellen Ergebniserfassung.

-	Fernsteuerung: Zudem wird in eine Fernsteuerung eingearbeitet um auch ohne Sensorik den TTR während dem Spiel angenehm zu bedienen.

-	Sensorik-Integration: Erweiterung um Piezo-Sensoren zur Aufprallregistrierung sowie ein Kamerasystem zur Echtzeit-Ballüberwachung.

Durch die Verknüpfung von Hardware (Sensoren, Kamera) und Software (Datenbank, UI) bietet das TTR-System eine umfassende Lösung zur präzisen Verwaltung und Überwachung von Tischtennis-Wettkämpfen.
1.2	Motivation
Die Motivation für dieses Projekt ist tief in meinem Alltag verwurzelt. Da ich sowohl in meiner Freizeit regelmässig als auch hier bei der Arbeit täglich Tischtennis spiele, kenne ich die Herausforderungen der manuellen Zählung aus erster Hand. Besonders unser betriebsinternes Langzeit-Turnier zwischen meinem Arbeitskollegen Florin und mir gab den entscheidenden Anstoss: Ich möchte am Ende meines ersten Lehrjahres zweifelsfrei in der Datenbank nachschlagen können, wer von uns beiden das Turnier gewonnen hat und wer dementsprechend wem ein Essen im „Hans im Glück“ schuldet.
Darüber hinaus reizt mich die technische Komponente: Das Projekt bietet die ideale Gelegenheit, die Lücke zwischen traditionellem Sport und moderner IoT-Technologie zu schliessen. Als Plattform-Entwickler möchte ich ein tiefes Verständnis für die gesamte Kette eines vernetzten Produkts erlangen von der physischen Hardware und Sensorik bis hin zur Datenverarbeitung im Backend. Die Herausforderung besteht darin, ein System zu schaffen, das nicht nur funktional ist, sondern durch ein durchdachtes UI/UX-Design einen echten Mehrwert für uns Spieler bietet.

1.3	Zielsetzung
Das Hauptziel dieses Projekts ist die Entwicklung eines digitalen Schiedsrichters für Tischtennis, der das mühsame manuelle Zählen ersetzt. Das System soll modular aufgebaut sein und die gesamte Kette eines IoT-Produkts abdecken: von der Hardware über die Sensoren bis hin zur Datenbank.
Es geht darum, eine zuverlässige Lösung zu schaffen, die Spielergebnisse präzise erfasst und speichert. So soll es am Ende möglich sein, Statistiken über einen längeren Zeitraum zu führen und klare Fakten über Gewinne und Verluste bei unseren täglichen Matches zu haben. Das System muss so einfach zu bedienen sein, dass der Spielfluss nicht unterbrochen wird, egal ob man die Eingaben direkt am Gerät oder über die Fernsteuerung macht.

2	Projektplanung
2.1	Muss/Kann-Ziele
In dieser Tabelle sind die fest geplanten Aufgaben (Muss-Ziele) und die optionalen Erweiterungen (Kann-Ziele) aufgelistet, die wir für das TTR-System definiert haben.
Kategorie	Ziel	Beschreibung
Muss-Ziel	Datenbank	Aufbau einer MariaDB zur sicheren Speicherung von Spielerprofilen und Match-Resultaten.
Muss-Ziel	Benutzeroberfläche	Erstellung eines Touch-Interfaces für das 7-Zoll-Display zur manuellen Dateneingabe.
Muss-Ziel	Fernsteuerung	Einbau einer Steuerung, damit man den Spielstand, während dem Match bequem anpassen kann.
Muss-Ziel	Hardware-Gehäuse	Bau eines passgenauen Holzrahmens für den Raspberry Pi 5 und den Monitor.
Muss-Ziel	Abschluss	Erstellung der Dokumentation, der Bedienungsanleitung und Durchführung einer Live-Demo.
Muss-Ziel	Turniersystem	Automatisierte Auswertung von Langzeit-Turnieren inklusive Statistik-Anzeige.
Kann-Ziel	Piezo-Sensorik	Test und Integration von Sensoren zur automatischen Erkennung des Ballaufpralls.
Kann-Ziel	Kamerasystem	Aufbau einer Echtzeit-Überwachung des Balls mit einer Webcam (120fps).

 
2.2	Zeitplanung
Phase	Aufwand (ca.)	Beschreibung
Hardware und Basis Setup	15 Stunden	Zusammenbau vom Raspberry Pi 5, Installation der Kühlung, Konfiguration vom Betriebssystem und Bau vom Holzrahmen.
UI-Layout und Basis-Funktionen	15 Stunden	Erstellung vom Grund-Layout im Querformat, Integration von Standard-Infos (z.B. Uhrzeit, Status) und Design der Buttons.
Datenbank und Backend	20 Stunden	Aufbau der MariaDB Infrastruktur, Erstellung der Tabellen für Spieler- und Matchdaten sowie die API-Anbindung.
Kern-Entwicklung TTR-Logic	55 Stunden	Programmierung der Zähl-Logik für die Punkte, Verwaltung der Sätze und Entwicklung der Fernsteuerung.
Interaktivität und Optimierung	20 Stunden	Optimierung der Touch-Unterstützung auf dem Display und Feinjustierung der Fernsteuerung für flüssige Bedienung während dem Spiel.
Sensorik und Design	15 Stunden	Test und Integration der Piezo-Sensoren sowie der Kamera zur Ballüberwachung und optisches CSS-Feintuning.
Abschluss und Dokumentation	10 Stunden	Durchführung finaler Tests (Alpha/Beta), Erstellung der Bedienungsanleitung und Abschluss der Projektdokumentation.

 
2.3	Meilensteine
Die Meilensteine markieren die wichtigsten Etappen in der Entwicklung des TTR-Systems und stellen sicher, dass die Ziele schrittweise erreicht werden.
M1: 	Grundsystem & Datenbank: Das Fundament steht. Die MariaDB-Datenbank ist aufgesetzt und die manuelle Erfassung der Resultate über das System funktioniert einwandfrei.
M2: 	Hardware & Display: Der Raspberry Pi 5 ist im massgefertigten Holzrahmen verbaut und das Interface auf dem Touch-Display ist für die Benutzer bereit.
M3: 	Interaktivität & Fernsteuerung: Die Fernsteuerung ist implementiert, damit der Spielstand bequem, während dem Match angepasst werden kann, ohne das Gerät direkt berühren zu müssen.
M4:	Sensorik & Ballüberwachung: Die Piezo-Sensoren und die Kamera sind installiert und kalibriert. Die Testphase für die Ballüberwachung ist abgeschlossen, wobei eine Genauigkeit von 95 % bei den Sensoren angestrebt wird.
M5:		Projektabschluss: Die Dokumentation und die Bedienungsanleitung sind fertiggestellt. Das System wurde in der Beta-Phase getestet und ist bereit für die Live-Demo.

2.4	Benötigte Ressourcen
2.4.1	Personal
-	Projektleitung und Umsetzung: Florian Kessi 
-	Unterstützung: Mitlernende 
-	Externe Beratung: Nicolai-Alexander Gerencer, Noa De Paola und Lionel Verdegal 

2.4.2	Hardware
-	Raspberry Pi 5: Die Recheneinheit für die Logik. 
-	7-Zoll-Touchdisplay: Für die Anzeige und Eingabe am Gerät. 
-	Piezo-Sensoren: Zur Erkennung der Ballaufpralle. 
-	High-Speed Webcam: Für die Ballüberwachung. 
-	Zubehör: Netzteil, Micro-SD-Karte und Material für den Holzrahmen.

2.4.3	Physische Anforderungen
-	Stromversorgung: Anschluss für den Dauerbetrieb an der Platte.
-	WLAN-Verbindung: Für Updates und Cloud-Zugriff.
-	Werkstattzugang: Für den Bau des massgefertigten Rahmens. 

2.5	Eingesetzte Tools und Technologien
2.5.1	Software-Stack
-	Raspberry Pi OS: Das Betriebssystem, auf dem alles läuft. 
-	MariaDB (SQL): Die Datenbank zum Speichern der Spieler- und Matchdaten. 
-	QT: Das Framework, mit dem ich die Benutzeroberfläche (UI) programmiere. 

2.5.2	Entwicklungswerkzeuge
-	Visual Studio Code: Der Editor für das Schreiben des Codes. 
-	GitHub: Zur Sicherung und Versionierung des Quellcodes. 
-	Gemini-Pro: Als KI-Unterstützung für komplexe Logikfragen. 

3	Umsetzung
3.1	Material Zusammenbau
Die Montage der physischen Komponenten war der erste Schritt, um das System betriebsbereit zu machen. Dabei wurden die im Projektantrag definierten Teile verwendet.
-	Vorbereitung: Alle gelieferten Komponenten wurden ausgepackt und auf Vollständigkeit geprüft.
-	Gehäuse & Kühlung: Der Raspberry Pi 5 wurde für die ersten Tests vorbereitet.
-	Verkabelung: Der Monitor und der Raspberry Pi wurden an die Stromversorgung angeschlossen.
-	Verbindung: Der 7-Zoll-Touch-Monitor wurde über ein Micro-HDMI-Kabel und das Touchscreen-Datenkabel mit dem Raspberry Pi verbunden.

Erkenntnis aus der Montage: 
Beim Zusammenbau habe ich bemerkt, dass das ursprünglich geplante Gehäuse nicht optimal an die Haltevorrichtung des Bildschirms passt. Um die Entwicklung nicht zu verzögern, habe ich einen separaten Kühler bestellt, den ich während der Test- und Programmierphase nutze. Sobald die Software-Basis stabil läuft, werde ich mit dem 3D-Drucker ein massgeschneidertes Gehäuse erstellen, das perfekt mit dem Monitor und dem Holzrahmen harmoniert.
3.2	Betriebssystem (OS) aufsetzen
Damit der Raspberry Pi als digitaler Schiedsrichter fungieren kann, musste zuerst das Betriebssystem installiert werden.
1.	Software: Den «Raspberry Pi Imager» auf dem Laptop installieren.
2.	Medium: Die Micro-SD-Karte mit dem Laptop verbinden.
3.	Konfiguration: Im Imager das richtige Modell (Pi 5), das OS-System sowie die SD-Karte wählen. In den erweiterten Einstellungen habe ich den User und das WLAN direkt vorkonfiguriert.
4.	Flashing: Die Karte flashen, vom Laptop trennen und in den Kartenslot des Raspberry Pi stecken.
 
3.3	Grundkonfiguration 
Da ich bereits ein Projekt auf dem PI gearbeitet habe habe ich hier genau die Schritte verfolgt die ich bereits damals gemacht und Dokumentiert hatte.
1.	Systemstart: Den Pi mit der geflashten Karte starten und mit dem zuvor definierten Passwort anmelden.
2.	Funktionskontrolle: Das WLAN wurde überprüft und die Touchscreen-Funktion getestet.
3.	Updates: Um das System auf den neuesten Stand zu bringen, habe ich folgende Befehle im Terminal ausgeführt:
-	sudo apt update
-	sudo apt upgrade
4.	Bildschirm-Ausrichtung: Da das Interface im Hochformat (oder Querformat, je nach Wunsch) besser aussieht, habe ich die Anzeige angepasst:
-	Raspberry-Pi-Symbol -> Preferences -> Screen Configuration.
-	Rechtsklick auf den Monitor -> Orientation -> Ausrichtung wählen (z.B. Left/Right für Hochformat).
5.	Abschluss: Jetzt ist die Hardware bereit für die Installation der TTR-Software und der MariaDB-Datenbank.
 
3.4	Ständer 3D Drucken
Schon während der ersten Grundkonfigurationen ist mir ein praktisches Problem aufgefallen: Da der Raspberry Pi und die Kabel direkt auf der Rückseite des Displays montiert sind, lässt sich der Bildschirm weder stabil hinstellen noch flach hinlegen. Das macht die Bedienung und das Programmieren mühsam und birgt das Risiko, dass Kabel beschädigt werden.
Um dieses Problem zu lösen, habe ich mich dazu entschieden, einen passgenauen Ständer zu entwickeln und mit dem 3D-Drucker herzustellen.
•	Recherche & Inspiration: Als Orientierung diente mir das Modell «Raspberry Pi Touch Display 2 Development Stand» von MakerWorld. Dieses Modell ist speziell dafür ausgelegt, das Display in einem angenehmen Winkel zu halten und gleichzeitig Platz für den Raspberry Pi auf der Rückseite zu bieten.
•	Konstruktion in FreeCAD: Da ich eine individuelle Lösung wollte, die exakt auf meine Hardware und die Kabelführung abgestimmt ist, habe ich den Ständer nicht einfach heruntergeladen, sondern komplett selbst in FreeCAD gezeichnet.
•	Nutzen: Durch den selbst gedruckten Ständer ist das System nun deutlich stabiler. Das Display steht fest auf dem Tisch, was besonders für die weiteren Entwicklungsschritte und die spätere Testphase an der Tischtennisplatte ein grosser Vorteil ist. 
3.5	MariaDB
Für das TTR-System habe ich ein relationales Datenbankmodell entworfen, das sicherstellt, dass alle Daten konsistent gespeichert werden und auch nach einem Neustart des Systems wieder zur Verfügung stehen.
3.5.1	Spieler-Datenbank (player)
Die Tabelle player dient dazu, alle Teilnehmer/Spielr der Matches und der Turniere zentral zu erfassen und ihre persönliche Statistik zu führen.







Erklärung der Attribute:
id: Ein eindeutiger Identifikator für jeden Spieler (Primary Key).
name: Der Name des Spielers. Dieser muss laut UNIQUE-Beschränkung einmalig sein, damit es keine Verwechslungen gibt.
wins / losses: Hier werden die Siege und Niederlagen gezählt. Standardmässig starten beide Werte bei 0.
elo_rating: Ein spannendes Zusatzfeature. Jeder Spieler startet mit 1000 Punkten. So können wir später sehen, wer spielerisch wirklich die Nase vorn hat.
 
3.5.2	Spiele-Datenbank (match)
In der Tabelle match werden die einzelnen Partien protokolliert. Hier laufen die Informationen der Spieler zusammen.











Erklärung der Attribute und Verknüpfungen:
player_a_id / player_b_id: Diese Felder sind über Foreign Keys direkt mit der player-Tabelle verknüpft. So wird sichergestellt, dass nur existierende Spieler in ein Match eingetragen werden können.
score_a / score_b: Speichert das exakte Resultat des Spiels.
winner_id: Verweist auf die ID des Gewinners, um die spätere Auswertung für die "Hans im Glück"-Schulden zu erleichtern.
timestamp: Das System setzt automatisch das aktuelle Datum und die Uhrzeit beim Speichern des Spiels (CURRENT_TIMESTAMP).
 
3.6	API-Entwicklung
Nachdem die Datenbank steht, habe ich die API entwickelt. Sie dient als Bindeglied zwischen der Benutzeroberfläche (Frontend) und der MariaDB (Backend). Ich nutze dafür Python, da es perfekt mit dem Raspberry Pi harmoniert und sehr effizient mit Datenbanken kommunizieren kann.
3.6.1	Aufgabe der API
Die API hat im TTR-System zwei Hauptaufgaben:
1.	Daten abrufen: Wenn ich ein Spiel starte, fragt das Frontend bei der API nach: «Gib mir alle Namen aus der Tabelle player».
2.	Daten speichern: Wenn ein Spiel fertig ist, sendet das Frontend das Ergebnis an die API. Diese berechnet den Gewinner und führt die SQL-Befehle aus, um das Match zu speichern und die Statistik (Wins/Losses) der Spieler zu aktualisieren.
3.6.2	Beispiel: Ein Match speichern
 
3.6.3	Fehlerbehandlung
Damit das System stabil läuft, habe ich in der API verschiedene Prüfungen eingebaut:
•	Validierung: Es wird geprüft, ob die Punktzahlen logisch sind (z. B. keine negativen Punkte).
•	Datenbank-Check: Die API stellt sicher, dass die Verbindung zur MariaDB aktiv ist, bevor sie einen Schreibversuch unternimmt.
•	Rückmeldung: Das Frontend erhält von der API immer eine Bestätigung, ob das Speichern geklappt hat oder ob ein Fehler aufgetreten ist.
3.7	Touch Tastatur 
Da man in der Lage ist sein muss der Namen des Gegners, seinen eigenen und Optional auch seinen eigen und Optional beim erstellen des Turniers 

3.8	Fernbedienung 
Damit der Spielfluss nicht unterbrochen wird, kann der TTR über eine Fernsteuerung (z.B. einen handelsüblichen Presenter) bedient werden. Da diese Geräte technisch gesehen Tastaturbefehle emulieren, habe ich eine entsprechende Logik in der Benutzeroberfläche integriert.
3.8.1	Eingabelogik für die Punktevergabe
In der Datei ttr_gui.py fange ich die Signale der Fernsteuerung ab, indem ich die Standard-Methode keyPressEvent von PyQt überschreibe. Dies ermöglicht es dem System, auf Tastendrücke zu reagieren, egal welches Element auf dem Bildschirm gerade fokussiert ist.
Code-Ausschnitt der Eingabe-Verarbeitung:












 
Erklärung zur technischen Umsetzung:
•	Abfangen der Signale: Die Methode keyPressEvent liest den spezifischen Tastencode (event.key()) aus, sobald eine Taste gedrückt wird.
•	Zuweisung Spieler 2: Drückt man auf der Fernsteuerung nach rechts oder die «PageDown»-Taste (typische «Weiter»-Taste), wird die Methode self.add_point(2) aufgerufen.
•	Zuweisung Spieler 1: Die Pfeiltaste nach links oder «PageUp» (typische «Zurück»-Taste) vergibt über self.add_point(1) einen Punkt an Spieler 1.
•	Systemstabilität: Mit super().keyPressEvent(event) stelle ich sicher, dass alle Tasten, die nicht für das Punktezählen definiert sind, weiterhin normal vom Betriebssystem verarbeitet werden.

3.8.2	Eingabelogik für Ok oder Abbrechen
Damit der Schiedsrichter auch bei kritischen Aktionen (wie dem Beenden eines Spiels oder beim Rückgängig-Machen) nicht zum Touchscreen greifen muss, wird die Fernsteuerung auch für Bestätigungsdialoge genutzt. Sobald ein Dialog öffnet, erhält dieser automatisch den Fokus. Dadurch werden die Eingaben der Fernsteuerung genau dort abgefangen und nicht versehentlich als Punktzahl im Hintergrund gezählt.

Steuerung im Dialog:
-	Rechte Taste: Bestätigt die Aktion (entspricht «Ja» oder «OK»).
-	Linke Taste: Bricht die Aktion ab (entspricht «Nein» oder «Abbrechen»).

Code-Integration (Dialog-Handling)
In der Datei ttr_gui.py wird innerhalb der Funktion für den Bestätigungsdialog eine lokale Funktion key_press definiert. Diese überschreibt vorübergehend das Standard-Verhalten des Fensters (dialog):

4	Anleitung
Herzlich willkommen beim TTR Scoreboard. Diese Anleitung erklärt Ihnen Schritt für Schritt, wie Sie das Programm starten, neue Spiele anlegen und das digitale Scoreboard während des Matches bedienen.
4.1	Programm starten
•	Startvorgang: Starten Sie das Programm über die TTR-Verknüpfung auf Ihrem Desktop oder über den entsprechenden Start-Befehl auf Ihrem Gerät.
•	Anzeige: Das Programm öffnet sich automatisch im Vollbildmodus, damit die Anzeige auch aus grösserer Entfernung (z. B. vom anderen Ende der Tischtennisplatte) gut lesbar ist.
4.2	Spielvorbereitung (Setup)
•	Nach dem Startbildschirm landen Sie in der Spielvorbereitung. Hier legen Sie die Rahmenbedingungen für das nächste Match fest:
•	Spieler auswählen: Wählen Sie für «Spieler 1» (links) und «Spieler 2» (rechts) die jeweiligen Personen aus dem Dropdown-Menü aus. Sie können den Namen auch direkt tippen, um die Liste schnell zu durchsuchen.
•	Match-Typ: Legen Sie fest, ob es sich um ein Trainingsspiel oder ein Turnierspiel handelt. Bei einem Turnier kann das entsprechende Event ausgewählt werden.
•	Gewinnsätze (Sets to win): Bestimmen Sie, wie viele gewonnene Sätze für den Gesamtsieg nötig sind.
•	Beispiel: Bei der Einstellung «3» wird im «Best-of-5»-Modus gespielt (wer zuerst 3 Sätze gewinnt, hat das Match gewonnen).
•	Match starten: Sobald alle Angaben stimmen, klicken oder tippen Sie auf den grossen, blauen Button «Match starten», um zum Scoreboard zu wechseln.
4.3	Das Scoreboard im Spiel bedienen
•	Das Scoreboard ist speziell für Touchscreens und schnelle Eingaben optimiert. Die grossen Zahlen in der Mitte zeigen die aktuellen Punkte, die kleineren Zahlen daneben oder darunter zeigen den Satzstand an.
4.3.1	Punkte zählen
•	Punkt hinzufügen: Um einem Spieler einen Punkt zu geben, tippen Sie einfach auf die grosse Punktezahl oder auf die jeweilige Bildschirmhälfte des Spielers.
•	Punkt abziehen (Korrektur): Haben Sie sich verklickt? Unter oder neben der grossen Punktzahl finden Sie kleine «-1» Buttons. Tippen Sie darauf, um den letzten Punkt wieder abzuziehen.
4.3.2	Aufschlag und Seitenwechsel
•	Aufschlag-Anzeige: Das Programm berechnet automatisch, wer Aufschlag hat. Der aufschlagende Spieler wird durch ein Symbol oder eine farbliche Markierung neben seinem Namen hervorgehoben. Der Wechsel (z. B. alle zwei Punkte oder ab 10:10 nach jedem Punkt) erfolgt vollautomatisch.
•	Seitenwechsel: Wechseln die Spieler die Tischseite (z. B. nach einem Satz oder im Entscheidungssatz), tippen Sie auf den Button «Seitenwechsel». Namen, Punkte und Sätze tauschen dann auf dem Bildschirm die Seiten.
4.3.3	Satzende
•	Das Programm kennt die offiziellen Tischtennis-Regeln: Sobald ein Spieler 11 Punkte erreicht (mit mindestens 2 Punkten Vorsprung), ist der Satz beendet. Der Bildschirm aktualisiert automatisch den Satzstand, und die laufenden Punkte werden für den neuen Satz wieder auf 0 : 0 gesetzt.

4.4	Spielende und Speicherung
•	Sieg: Sobald ein Spieler die erforderliche Anzahl an Gewinnsätzen erreicht hat, ist das Match beendet.
•	Feier-Animation: Zur Bestätigung erscheint eine Konfetti-Animation auf dem Bildschirm, und der Gewinner wird gross angezeigt.
•	Ergebnis speichern: Die Ergebnisse, Sätze und Datumsangaben werden automatisch im Hintergrund in der Datenbank gespeichert. Es ist keine manuelle Sicherung nötig.
•	Neues Spiel: Klicken Sie abschliessend auf «Neues Spiel» oder «Zurück zum Setup», um das nächste Match vorzubereiten.
•	4.5 Tipps für die Bedienung
•	Touch-Bedienung: Falls Ihr Monitor ein Touchscreen ist, können Sie alle Buttons bequem mit den Fingern bedienen. Die Tasten sind extra gross gestaltet, um Fehlklicks zu vermeiden.
•	Programm schliessen: Da das Programm im Vollbildmodus läuft, gibt es kein typisches «X»-Symbol. Nutzen Sie die Taste Escape (ESC) oder die vom Administrator definierte Beenden-Taste, um das Programm zu verlassen.
