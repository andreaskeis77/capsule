# CUSTOM_GPT_FIELD_SPEC.md

**Zweck:** Präzise Soll-Spezifikation aller relevanten Builder-Felder des Custom GPT.

---

## 1. Name

**Feld:** Name  
**Sollwert:** `Capsule Wardrobe Architect`  
**Begründung:** fachlich passend, klar, merkfähig.

---

## 2. Beschreibung

**Feld:** Beschreibung / Description  
**Sollwert:**

> Plant minimalistische Capsule Wardrobes aus dem realen Bestand von Karen oder Andreas und verwaltet Teile bei Bedarf gezielt per API.

**Anforderungen:**
- kurz
- fachlich präzise
- kein Marketing-Sprech
- Planung + API-Verwaltung müssen beide erkennbar sein

---

## 3. Hinweise / Instructions

**Feld:** Hinweise / Instructions  
**Soll-Prinzipien:**
- Builder-Hinweistext bleibt kompakt
- Knowledge wird nicht dupliziert
- Verhalten ist hier führend
- Knowledge darf den Builder-Text nicht widersprechen

**Muss regeln:**
1. Rolle des GPT
2. Karen als Default
3. Missing-Info-Logik
4. Trennung Planung vs. CRUD
5. Delete-Bestätigung
6. Outputformat
7. Magic Link
8. Visualisierung nur nach Textausgabe
9. Tonalität

**Nicht in die Instructions ziehen:**
- vollständige API-Referenz
- redundante CRUD-Details
- langes Domänenwissen
- historische Debug-Hinweise

---

## 4. Conversation Starters

**Feld:** Gesprächsaufhänger / Conversation starters  
**Soll-Anzahl:** 5

**Sollwerte:**
1. `Ich bin Karen und brauche eine Capsule für drei Bürotage und ein Abendessen.`
2. `Hier ist Andreas. Plane mir eine kleine Business-Capsule für zwei Reisetage, ohne bunte Farben.`
3. `Zeig mir bitte, welche Teile aus meinem Bestand für eine Sommer-Capsule am stärksten sind.`
4. `Ich möchte ein neues Teil per Foto anlegen und sauber kategorisieren lassen.`
5. `Ändere bitte die Daten von #CW-123, aber nur die Farbe und den Namen.`

**Begründung:**
- deckt Karen ab
- deckt Andreas ab
- deckt Bestandsauswertung ab
- deckt Create ab
- deckt Update ab

---

## 5. Empfohlenes Modell

**Feld:** Recommended model  
**Soll-Regel:** Nur nach Live-Test mit aktivierten Actions final festlegen.

**Dokuregel:**
- Builder-Anzeige allein reicht nicht als Nachweis
- maßgeblich ist das reale Laufverhalten im Preview mit Action-Aufrufen

**Zu dokumentieren:**
- verwendetes Modell
- funktioniert `listItems`
- funktioniert `getItem`
- funktioniert `updateItem`
- gibt es sichtbare oder stille Fallbacks

---

## 6. Knowledge

**Feld:** Knowledge  
**Aktueller Träger:** `KNOWLEDGE_CapsuleWardrobeArchitect_v6.md`

**Soll-Regel:**
- Knowledge enthält Referenzwissen
- Verhalten bleibt im Builder-Hinweistext
- bei Konflikten gilt: Instructions vor Knowledge

**Mittelfristige Soll-Struktur:**
1. Knowledge-Domain
2. optional Knowledge-Ops
3. kein widersprüchliches Verhaltensprompting

---

## 7. Capabilities / Tools

**Soll-Konfiguration:**
- Web nur falls wirklich benötigt
- Bild-/Vision-Nutzung nur im Rahmen der CRUD-/Visualisierungslogik
- Actions aktiv

**Hinweis:**
Der primäre Mehrwert dieses GPT entsteht nicht durch beliebige Websuche, sondern durch strukturierten Bestand + API-Zugriff.

---

## 8. Actions

**Sollprinzipien:**
- klare Server-URL
- API-Key-Auth
- formal sauberes OpenAPI
- präzise OperationIds
- enum statt Freitext, wo möglich

**Soll-Datei:** siehe `CUSTOM_GPT_ACTIONS_OPENAPI_PROPOSED.yaml`

---

## 9. Sharing / Privacy

**Soll-Regel:**
Wenn der GPT öffentlich geteilt oder veröffentlicht werden soll und öffentliche Actions nutzt, muss eine gültige Privacy Policy URL hinterlegt sein.

**Projektentscheidung offen:**
- nur privat/workspace-intern
- oder perspektivisch teilbar/public

Diese Entscheidung beeinflusst die Builder-/Action-Doku unmittelbar.
