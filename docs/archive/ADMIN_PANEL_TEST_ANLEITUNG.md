# Admin Panel - Test Anleitung

**URL:** https://www.dabrock.info/admin/

---

## 🔑 Test-User Credentials

### **Test User 1:**
```
Email:    test@dabrock.info
Password: Test123Secure
```

### **Test User 2** (Erstellen Sie selbst):
Registrieren Sie sich mit beliebiger Email über das Admin Panel.

---

## 🧪 Test-Szenarien

### **1. Login testen**

1. Öffnen Sie: https://www.dabrock.info/admin/
2. Geben Sie ein:
   - Email: `test@dabrock.info`
   - Password: `Test123Secure`
3. Klicken Sie auf **"Login"**

**Erwartet:**
- ✅ Dashboard lädt
- ✅ Sie sehen Statistiken
- ✅ Navigation funktioniert

**Falls Fehler:**
- ⚠️ CORS Error → Railway CORS Update noch nicht durch (warten Sie weitere 5-10 Min)
- ⚠️ "Invalid credentials" → Passwort falsch getippt
- ⚠️ Weiße Seite → Browser Cache leeren (Strg+Shift+R)

---

### **2. Dashboard testen**

Nach dem Login sollten Sie sehen:
- **System Stats:**
  - Total Users
  - Total Projects
  - Total Documents
  - Total Chats

**Test:**
- ✅ Zahlen werden angezeigt
- ✅ Keine Error Messages

---

### **3. User Management testen**

1. Klicken Sie im Menü auf **"Users"** oder **"User Management"**
2. Sie sollten eine Liste aller User sehen

**Test:**
- ✅ User-Liste lädt
- ✅ Ihr Test-User ist in der Liste
- ✅ Email-Adressen sind sichtbar

---

### **4. LLM Configuration testen**

1. Klicken Sie im Menü auf **"LLM"** oder **"LLM Config"**
2. Wählen Sie ein Model aus (z.B. "qwen3-coder:30b")
3. Geben Sie einen Test-Prompt ein: "Write hello world in Python"
4. Klicken Sie auf **"Generate"**

**Test:**
- ✅ Model-Liste lädt
- ✅ Generation startet (Loading...)
- ✅ Antwort wird angezeigt
- ⚠️ Bei CPU kann es 30-60 Sekunden dauern!

---

### **5. Logout testen**

1. Klicken Sie auf **"Logout"** Button
2. Sie werden zum Login zurückgeleitet

**Test:**
- ✅ Logout funktioniert
- ✅ Dashboard nicht mehr erreichbar (ohne Login)
- ✅ Re-Login funktioniert

---

## 🐛 Troubleshooting

### **Problem: "Failed to fetch" Error**

**Ursache:** Backend nicht erreichbar oder CORS nicht konfiguriert

**Lösung:**
1. Prüfen Sie: https://general-backend-production-a734.up.railway.app/health
   - Sollte `{"status":"healthy"}` zurückgeben
2. Railway CORS Update durchführen (siehe RAILWAY_CORS_UPDATE.md)
3. Warten Sie 12 Minuten nach CORS Update
4. Browser Cache leeren

---

### **Problem: "Unauthorized" / "401"**

**Ursache:** Token ungültig oder abgelaufen

**Lösung:**
1. Logout und erneut Login
2. Oder: Browser Cache leeren (Strg+Shift+R)

---

### **Problem: Weiße Seite / Nichts lädt**

**Ursache:** JavaScript Error oder Assets nicht geladen

**Lösung:**
1. Browser Console öffnen (F12)
2. Tab "Console" prüfen auf Errors
3. Tab "Network" prüfen ob Assets (CSS/JS) laden
4. Falls 404 Errors: Dateien wurden nicht richtig hochgeladen

**Dateien nochmal deployen:**
```bash
cd /mnt/e/CodelocalLLM/GeneralBackend/admin-frontend
npm run build
# Upload erneut
```

---

### **Problem: LLM Generation timeout**

**Ursache:** CPU-basierte Inferenz ist langsam (qwen3-coder:30b)

**Lösung:**
- Warten Sie bis zu 60 Sekunden
- Oder: Nutzen Sie Claude/Grok (wenn API Keys konfiguriert)

---

## ✅ Erfolgs-Checkliste

Testen Sie alle Features:

- [ ] Login funktioniert
- [ ] Dashboard zeigt Stats
- [ ] User Management zeigt User-Liste
- [ ] LLM Config lädt Models
- [ ] LLM Generation funktioniert (auch wenn langsam)
- [ ] Logout funktioniert
- [ ] Re-Login funktioniert
- [ ] Keine CORS Errors in Browser Console

---

## 🎯 Nach erfolgreichem Test

**Nächste Schritte:**
1. ✅ Admin Panel funktioniert
2. ✅ Backend ist ready
3. ✅ CV Matcher kann deployed werden

**CV Matcher deployen:**
```bash
cd /mnt/e/CodelocalLLM/CV_Matcher
npm run build
# Upload nach /dabrock-info/cv-matcher/
```

---

**Erstellt:** 22. Dezember 2025
**Status:** Ready for Testing

**Bei Problemen:**
- Prüfen Sie RAILWAY_CORS_UPDATE.md
- Prüfen Sie Browser Console (F12)
- Warten Sie 12 Min nach CORS Update
