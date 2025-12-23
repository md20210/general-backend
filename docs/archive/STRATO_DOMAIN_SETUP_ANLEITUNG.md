# Strato Domain-Zuordnung Anleitung

**Ziel:** `www.dabrock.info` auf eigenes Verzeichnis `/dabrock-info/` umstellen

---

## 📍 Schritt-für-Schritt Anleitung

### **1. Strato Login**

Öffnen Sie im Browser:
```
https://www.strato.de/apps/CustomerService
```

Login mit:
- **Kundennummer** oder **Email**
- **Passwort**

---

### **2. Domain-Verwaltung finden**

Nach dem Login:

**Option A: Über Hauptmenü**
1. Klicken Sie links im Menü auf **"Domains"**
2. Oder suchen Sie nach **"Domain-Verwaltung"**

**Option B: Über Pakete**
1. Klicken Sie auf **"Meine Produkte"** oder **"Pakete & Domains"**
2. Suchen Sie nach **"dabrock.info"**

---

### **3. Domain dabrock.info auswählen**

In der Domain-Liste:
1. Finden Sie **"dabrock.info"** (ohne www)
2. Klicken Sie auf die Domain oder auf **"Verwalten"** / **"Einstellungen"**

**Möglicherweise heißt der Button:**
- "Einstellungen"
- "Domain verwalten"
- "Bearbeiten"
- Zahnrad-Symbol ⚙️

---

### **4. Zielverzeichnis / DocumentRoot ändern**

Jetzt sollten Sie die Domain-Einstellungen sehen.

**Suchen Sie nach einem dieser Begriffe:**
- **"Zielverzeichnis"**
- **"DocumentRoot"**
- **"Webspace-Verzeichnis"**
- **"Verzeichniszuordnung"**
- **"Pfad"**

**Das sieht ungefähr so aus:**

```
┌─────────────────────────────────────────┐
│ Domain: dabrock.info                    │
├─────────────────────────────────────────┤
│ Zielverzeichnis: /htdocs/          [✎] │
│                                         │
│ [Ändern] [Speichern]                   │
└─────────────────────────────────────────┘
```

---

### **5. Verzeichnis ändern**

**AKTUELL:** `/htdocs/` oder `/htdocs` (Standard)

**ÄNDERN ZU:** `/dabrock-info/` oder `/dabrock-info`

**Wichtig:**
- Mit oder ohne `/` am Ende ist egal
- NICHT `/htdocs/dabrock-info/` (das wäre falsch!)
- NUR `/dabrock-info/`

---

### **6. Speichern**

Klicken Sie auf:
- **"Speichern"**
- **"Übernehmen"**
- **"Änderungen speichern"**

---

### **7. Warten auf DNS-Propagation**

Nach dem Speichern:
- **Änderung dauert:** 5 Minuten bis 24 Stunden
- **Meist:** 30-60 Minuten
- **Sie sehen:** "Änderungen werden übernommen" oder ähnlich

---

## 🔍 Alternative: Falls Sie die Option nicht finden

### **Möglichkeit 1: Strato FTP/Webspace Einstellungen**

```
Strato Admin → Webspace → Einstellungen
```

Suchen Sie nach:
- **"Mehrere Domains"**
- **"Domain-Mapping"**
- **"Subdomain-Verwaltung"**

### **Möglichkeit 2: .htaccess Redirect (Workaround)**

Falls Strato KEINE separate Verzeichniszuordnung erlaubt:

**Erstellen Sie `/htdocs/.htaccess`:**

```apache
RewriteEngine On
RewriteCond %{HTTP_HOST} ^(www\.)?dabrock\.info$ [NC]
RewriteCond %{REQUEST_URI} !^/dabrock-info/
RewriteRule ^(.*)$ /dabrock-info/$1 [L]
```

Das leitet alle `dabrock.info` Anfragen nach `/htdocs/dabrock-info/` um.

---

## 📞 Strato Support kontaktieren

Falls Sie es nicht finden:

**Strato Hotline:**
- **Telefon:** 030 300 146 000
- **Email:** support@strato.de
- **Chat:** Im Strato Customer Service verfügbar

**Frage stellen:**
> "Ich möchte die Domain www.dabrock.info auf ein eigenes Verzeichnis
> /dabrock-info/ umleiten, statt auf das Standard /htdocs/ Verzeichnis.
> Wo kann ich das in meinem Account einstellen?"

---

## ✅ Nach erfolgreicher Umstellung

**Testen Sie:**
```
https://www.dabrock.info/
```

**Sollte zeigen:**
- ❌ **NICHT:** Strato "Domain reserved" Seite
- ✅ **SONDERN:** 404 Fehler (weil Verzeichnis leer) oder Ihre Landing Page

**404 ist GUT!** Das bedeutet die Umstellung funktioniert.

---

## 🔄 Nächste Schritte (nach Umstellung)

Sobald die Domain umgestellt ist:

1. ✅ Ich uploade Landing Page
2. ✅ Ich uploade Admin Panel
3. ✅ Ich teste alle URLs

**Melden Sie sich, sobald die Umstellung durch ist!**

---

**Erstellt:** 22. Dezember 2025
**Status:** Wartet auf Strato Domain-Umstellung
