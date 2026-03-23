# DEPLOYMENT_TARGET_STATE – Capsule

## 1. Zielentscheidung

Der empfohlene Zielzustand ist:

- **Capsule läuft zentral auf einem Windows-VPS**
- **ngrok läuft ebenfalls auf dem VPS**
- **Karen hostet nichts lokal**
- Karen nutzt Capsule über:
  - ChatGPT Custom GPT
  - und/oder Website im Browser

## 2. Warum dieser Zielzustand sinnvoll ist

### 2.1 Betriebsvereinfachung

Wenn Karen keinen lokalen Server mehr betreiben muss, entfallen typische Probleme:

- Laptop muss laufen
- lokale Pfad-/Port-/Firewall-Probleme
- Versionsdrift zwischen mehreren Geräten
- fragile Tunnel von einem Privatgerät

### 2.2 Gleiche Wahrheit für alle Clients

Der VPS wird zum zentralen Ort für:

- API
- Weboberfläche
- Run Registry
- Doku-/Ops-nahe Standardpfade

### 2.3 Sicherere OpenAI-Integration

Falls die Website mit OpenAI API arbeitet, kann das serverseitig geschehen.  
So bleiben Secrets auf dem Server und nicht im Browser.

## 3. Empfohlene Architektur

### 3.1 Komponenten

1. **Windows-VPS**
   - Repo
   - Python / `.venv`
   - Daten / DB / Bilder / Runtime-Dateien
   - Capsule-App

2. **Tunnel / öffentlicher Zugang**
   - kurzfristig: ngrok auf dem VPS
   - später optional: Reverse Proxy / fester Host

3. **ChatGPT Custom GPT**
   - spricht über Actions mit der öffentlichen Capsule-API

4. **Website / Browser**
   - spricht gegen denselben Backend-Stand
   - optional zusätzliche serverseitige OpenAI-Funktionen

### 3.2 Architekturregel

Custom GPT und Website sollen nicht gegen unterschiedliche Backends oder Datenstände laufen.

## 4. Klare Empfehlung zu ngrok

**Kurzfristig: ja, ngrok auf dem Windows-VPS ist sinnvoll.**

Warum:

- maximale Parität zu eurer aktuellen Windows-Entwicklung
- schneller Weg zu einem stabilen öffentlichen Endpoint
- Karens Laptop wird aus dem Hosting entfernt

**Nicht empfohlen:**  
ngrok dauerhaft auf Karens Laptop als Produktionsersatz.

## 5. Übergangszustand vs. Zielzustand

### Übergang
- lokaler Entwickler-Laptop
- Tests lokal
- optional lokales ngrok

### Ziel
- VPS hostet App
- VPS hostet Tunnel
- Karen konsumiert nur noch

## 6. Noch offene Architekturentscheidung

Ihr müsst bewusst festlegen, wie die Nutzungswege gewichtet werden:

### Option A – Custom GPT first
- Karen arbeitet primär in ChatGPT
- Website eher als Admin-/Review-Oberfläche

### Option B – Website first
- Karen arbeitet primär im Browser
- GPT ergänzt bestimmte Flows

### Option C – Hybrid
- GPT für dialogische / schnelle Aufgaben
- Website für Review, Kuration, Operations, Admin

**Meine Empfehlung aktuell:**  
**Hybrid**, aber mit einem einzigen kanonischen Backend und serverseitiger OpenAI-Kommunikation für Web-Use-Cases.
