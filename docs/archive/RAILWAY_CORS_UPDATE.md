# Railway CORS Update - Anleitung

**Ziel:** Backend erlaubt Anfragen von `www.dabrock.info`

---

## 🎯 Schritt-für-Schritt Anleitung

### **Schritt 1: Railway Login**

Öffnen Sie im Browser:
```
https://railway.app
```

Login mit Ihren Railway-Zugangsdaten.

---

### **Schritt 2: Projekt öffnen**

Nach dem Login:
1. Finden Sie das Projekt **"Generalbackend"**
2. Klicken Sie auf das Projekt

---

### **Schritt 3: Service auswählen**

Im Projekt:
1. Klicken Sie auf den Service **"general-backend"**
2. (NICHT auf "pgVector-Railway" oder "ollama")

---

### **Schritt 4: Variables öffnen**

Im Service:
1. Klicken Sie oben auf den Tab **"Variables"**
2. Sie sehen jetzt alle Environment Variables

---

### **Schritt 5: ALLOWED_ORIGINS ändern**

In der Variable-Liste:
1. Suchen Sie die Variable **"ALLOWED_ORIGINS"**
2. Klicken Sie auf **"Edit"** oder auf die Variable selbst

**AKTUELLER WERT (vermutlich):**
```
https://www.dabrock.eu,http://localhost:5173
```

**ÄNDERN ZU:**
```
https://www.dabrock.info,https://www.dabrock.eu,http://localhost:5173
```

**Wichtig:**
- Kommas ohne Leerzeichen
- Alle URLs mit `https://` (außer localhost)
- Keine Leerzeichen am Anfang/Ende

---

### **Schritt 6: Speichern**

1. Klicken Sie auf **"Save"** oder **"Update"**
2. Railway zeigt: "Redeploying service..."

**⏳ Deployment dauert ~12 Minuten**

---

### **Schritt 7: Warten & Testen**

**Nach ~12 Minuten:**

Testen Sie das Admin Panel:
```
https://www.dabrock.info/admin/
```

**Login sollte funktionieren!**

---

## ✅ Erfolgskriterien

**CORS funktioniert, wenn:**
- ✅ Admin Panel lädt ohne Fehler
- ✅ Login funktioniert
- ✅ Keine "CORS policy" Fehler in Browser Console (F12)

**Falls CORS noch nicht funktioniert:**
- Railway Deployment läuft noch (warten)
- Browser Cache leeren (Strg+Shift+R)
- Variable falsch eingegeben (nochmal prüfen)

---

## 🔍 Debugging

**Falls Login nicht funktioniert:**

1. Browser Console öffnen (F12)
2. Tab "Console" auswählen
3. Suchen Sie nach Fehler wie:
   ```
   Access to fetch at '...' has been blocked by CORS policy
   ```

**Falls dieser Fehler erscheint:**
- CORS Update hat noch nicht gewirkt
- Warten Sie weitere 5 Minuten
- Oder: Variable wurde falsch gesetzt

---

**Erstellt:** 22. Dezember 2025
**Status:** Wartet auf Railway CORS Update
