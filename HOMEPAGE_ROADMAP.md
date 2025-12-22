# Homepage & CV Matcher Roadmap

**Ziel:** www.dabrock.info mit CV Matcher als erste Showcase-Subpage

---

## 🏗️ Website-Struktur

```
www.dabrock.info/
├── /                           # Homepage (Landing Page)
├── /about                      # Über mich (CV, Technische Topics)
├── /showcases                  # Showcase-Übersicht
│
├── /cvmatcher                  # 🎯 CV Matcher Showcase
├── /privategpt                 # PrivateGPT Showcase (später)
└── /tellmelife                 # TellMeLife Showcase (später)
```

---

## 📄 Seiten-Aufbau

### **1. Homepage (/) - Landing Page**

**Content aus:** `Homepage.md` (544 Zeilen)

**Sections:**
```
┌─────────────────────────────────────┐
│         HERO SECTION                │
│  Michael Dabrock                    │
│  Enterprise Architect & AI Innovator│
│  TOGAF & IBM Certified              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    PROFESSIONAL SUMMARY             │
│  20+ Jahre Enterprise Experience    │
│  Enterprise-Grade AI Solutions      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    SHOWCASES (3 Cards)              │
│  [CV Matcher] [PrivateGPT] [Tell..]│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    WHY ENTERPRISE-GRADE?            │
│  Vergleichstabelle                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    TECHNOLOGY STACK                 │
│  FastAPI, PostgreSQL, AI/LLM        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CREDENTIALS                      │
│  TOGAF, IBM, Stanford Certifications│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CONTACT                          │
│  Email, Phone, Barcelona            │
└─────────────────────────────────────┘
```

---

### **2. About (/about) - Über Mich**

**Content aus:** `CV Technische Topics.md` (730 Zeilen)

**Sections:**
```
┌─────────────────────────────────────┐
│    PROFESSIONAL SUMMARY             │
│  Enterprise Architect Profile       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CORE COMPETENCIES                │
│  - Enterprise Architecture          │
│  - AI/ML Development                │
│  - Database Technologies            │
│  - Cloud & DevOps                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CAREER HIGHLIGHTS                │
│  - 380-person SAP Teams             │
│  - Global Code Red Projects         │
│  - Mercedes Benz, Deutsche Telekom  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    CERTIFICATIONS                   │
│  TOGAF, IBM, Stanford               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    TECHNICAL PHILOSOPHY             │
│  "Boring Technology is Best"        │
└─────────────────────────────────────┘
```

---

### **3. Showcases (/showcases) - Übersicht**

**Content aus:** `Homepage.md` Use Cases Section

**Layout:**
```
┌─────────────────────────────────────────────────┐
│        ENTERPRISE-GRADE AI SHOWCASES            │
│  Production-ready platforms built on proven     │
│  enterprise architecture patterns (TOGAF)       │
└─────────────────────────────────────────────────┘

┌───────────────┬───────────────┬───────────────┐
│               │               │               │
│  CV MATCHER   │  PRIVATEGPT   │  TELLMELIFE   │
│               │               │               │
│  🎯 Status:   │  🔨 Status:   │  📅 Status:   │
│  ✅ LIVE      │  Coming Q1    │  Coming Q2    │
│               │               │               │
│  [Try Demo]   │  [Learn More] │  [Learn More] │
│               │               │               │
└───────────────┴───────────────┴───────────────┘

┌─────────────────────────────────────────────────┐
│    UNIFIED SERVICE-BAUKASTEN                    │
│  All showcases powered by one enterprise backend│
│  - Authentication Service                       │
│  - LLM Gateway (Ollama/Claude/Grok)            │
│  - Document Management                          │
│  - Vector Search (pgvector)                     │
│  - Project Management                           │
└─────────────────────────────────────────────────┘
```

---

### **4. CV Matcher (/cvmatcher) - 🎯 ERSTE SHOWCASE SUBPAGE**

**Full-Featured React Application**

#### **Landing Section:**
```
┌─────────────────────────────────────────────────┐
│         CV MATCHER - Enterprise Recruiting      │
│         Intelligence powered by AI              │
│                                                 │
│  Semantic CV-to-Job Matching | Skill Analysis  │
│  Batch Processing | GDPR-Compliant            │
│                                                 │
│         [Start Matching] [View Demo]           │
└─────────────────────────────────────────────────┘
```

#### **Features Section:**
```
┌───────────────┬───────────────┬───────────────┐
│ 🎯 Semantic   │ 🤖 AI-Powered │ 🔒 GDPR       │
│    Matching   │    Analysis   │    Compliant  │
│               │               │               │
│ Vector search │ Claude/Grok   │ EU hosting    │
│ pgvector      │ integration   │ Local LLM     │
└───────────────┴───────────────┴───────────────┘
```

#### **Application Interface:**

**Logged-Out Users:**
```
┌─────────────────────────────────────────────────┐
│  Try CV Matcher                                 │
│                                                 │
│  [Login] [Register] [View Demo]                │
└─────────────────────────────────────────────────┘
```

**Logged-In Users:**
```
┌─────────────────────────────────────────────────┐
│  HEADER: CV Matcher Dashboard                   │
│  User: michael@dabrock.eu | [Logout]           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  SIDEBAR                                        │
│  - 📊 Dashboard                                 │
│  - 📁 My Projects                               │
│  - 📄 Upload CVs                                │
│  - 🎯 Job Descriptions                          │
│  - 📈 Results                                   │
│  - ⚙️ Settings                                  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  MAIN CONTENT AREA                              │
│                                                 │
│  Current Project: Q1 2025 Hiring               │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Job Description                         │   │
│  │ [Upload PDF/DOCX] or [Paste Text]      │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Candidate CVs                           │   │
│  │ [Upload Multiple] or [Drag & Drop]     │   │
│  │                                         │   │
│  │ 📄 John_Doe_CV.pdf          [Uploaded] │   │
│  │ 📄 Jane_Smith_CV.pdf        [Uploaded] │   │
│  │ 📄 Mike_Johnson_CV.docx     [Uploaded] │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [🚀 Start Matching]                           │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  RESULTS                                        │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ 🥇 #1: Jane Smith (92% Match)          │   │
│  │ ✅ Python, FastAPI, PostgreSQL          │   │
│  │ ⚠️ Gaps: Kubernetes, Docker             │   │
│  │ [View Details] [AI Analysis]           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ 🥈 #2: John Doe (87% Match)            │   │
│  │ ✅ React, TypeScript, Node.js           │   │
│  │ ⚠️ Gaps: Backend experience             │   │
│  │ [View Details] [AI Analysis]           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Design System

### **Farben (Professional + Modern):**

```css
/* Primary Colors */
--primary-blue: #2563eb;      /* Trust, Professional */
--primary-dark: #1e40af;      /* Darker blue */
--primary-light: #60a5fa;     /* Lighter blue */

/* Accent Colors */
--accent-green: #10b981;      /* Success, Match */
--accent-orange: #f59e0b;     /* Warning, Gaps */
--accent-red: #ef4444;        /* Error, Low match */

/* Neutral Colors */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-700: #374151;
--gray-900: #111827;

/* Backgrounds */
--bg-primary: #ffffff;
--bg-secondary: #f9fafb;
--bg-dark: #111827;
```

### **Typography:**

```css
/* Font Family */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Headings */
h1: 3rem (48px) - Bold
h2: 2.25rem (36px) - Semibold
h3: 1.875rem (30px) - Semibold
h4: 1.5rem (24px) - Medium

/* Body */
body: 1rem (16px) - Regular
small: 0.875rem (14px) - Regular
```

### **Components:**

**Buttons:**
```css
.btn-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
}

.btn-secondary {
  background: white;
  color: #2563eb;
  border: 2px solid #2563eb;
}
```

**Cards:**
```css
.card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
}
```

---

## 🗂️ Projekt-Struktur

```
/mnt/e/Project20250615/portfolio-website/michael-homepage/
├── public/
│   ├── index.html
│   └── assets/
│       ├── images/
│       └── cv/
│           └── Michael_Dabrock_CV.pdf
│
├── src/
│   ├── App.tsx                    # Main App
│   ├── main.tsx                   # Entry Point
│   │
│   ├── pages/
│   │   ├── Home.tsx               # Landing Page (/)
│   │   ├── About.tsx              # About Page (/about)
│   │   ├── Showcases.tsx          # Showcases Overview (/showcases)
│   │   │
│   │   └── cvmatcher/             # CV Matcher App
│   │       ├── CVMatcherHome.tsx  # CV Matcher Landing
│   │       ├── Dashboard.tsx      # Main Dashboard
│   │       ├── Login.tsx          # Login Page
│   │       ├── Register.tsx       # Registration
│   │       ├── Projects.tsx       # Projects List
│   │       ├── Upload.tsx         # Document Upload
│   │       ├── Results.tsx        # Matching Results
│   │       └── Analysis.tsx       # AI Analysis View
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx         # Site Header
│   │   │   ├── Footer.tsx         # Site Footer
│   │   │   ├── Sidebar.tsx        # CV Matcher Sidebar
│   │   │   └── Navigation.tsx     # Main Navigation
│   │   │
│   │   ├── sections/
│   │   │   ├── Hero.tsx           # Hero Section
│   │   │   ├── Features.tsx       # Features Grid
│   │   │   ├── TechStack.tsx      # Technology Stack
│   │   │   ├── Credentials.tsx    # Certifications
│   │   │   └── Contact.tsx        # Contact Section
│   │   │
│   │   ├── cvmatcher/
│   │   │   ├── FileUpload.tsx     # Drag & Drop Upload
│   │   │   ├── MatchCard.tsx      # Match Result Card
│   │   │   ├── ProjectCard.tsx    # Project Card
│   │   │   ├── SkillsList.tsx     # Skills Display
│   │   │   └── GapsAnalysis.tsx   # Skill Gaps
│   │   │
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       ├── Loading.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── services/
│   │   ├── api.ts                 # API Client (from ARCHITECTURE.md)
│   │   ├── auth.ts                # Auth Service
│   │   ├── projects.ts            # Projects Service
│   │   ├── documents.ts           # Documents Service
│   │   └── llm.ts                 # LLM Service
│   │
│   ├── hooks/
│   │   ├── useAuth.ts             # Authentication Hook
│   │   ├── useProjects.ts         # Projects Hook
│   │   ├── useDocuments.ts        # Documents Hook
│   │   └── useLLM.ts              # LLM Hook
│   │
│   ├── types/
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── document.ts
│   │   └── llm.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   └── styles/
│       ├── globals.css
│       └── tailwind.css
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

---

## 🚀 Deployment Strategie

### **Strato Hosting Setup:**

**Ziel-URLs:**
- `www.dabrock.info/` → Homepage
- `www.dabrock.info/cvmatcher` → CV Matcher App
- `www.dabrock.info/about` → About Page
- `www.dabrock.info/showcases` → Showcases Overview

**Deployment via SFTP:**
```bash
# Build
npm run build

# Upload via lftp
lftp -c "open -u $SFTP_USER,$SFTP_PASSWORD sftp://$SFTP_HOST; \
  mirror -R --delete --verbose dist /htdocs"
```

**Server-Side Configuration (.htaccess):**
```apache
# Single Page Application Routing
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /

  # Don't rewrite files or directories
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d

  # Rewrite everything else to index.html
  RewriteRule ^ index.html [L]
</IfModule>

# Enable GZIP Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/css text/javascript application/javascript
</IfModule>

# Browser Caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

---

## 📋 Development Timeline

### **Phase 1: Homepage Foundation (Tag 1-2)**

**Tag 1 Vormittag: Backend Fix**
- [ ] Document Routes korrigieren (1-2h)
- [ ] LLM Default Model anpassen (5 Min)
- [ ] Tests auf 17/17 bringen
- [ ] Railway Deploy verifizieren

**Tag 1 Nachmittag: React Setup**
- [ ] Vite + React + TypeScript initialisieren
- [ ] TailwindCSS konfigurieren
- [ ] Router Setup (React Router)
- [ ] API Client implementieren (aus ARCHITECTURE.md)
- [ ] Auth Context/Provider
- [ ] Layout Components (Header, Footer)

**Tag 2: Homepage Content**
- [ ] Hero Section
- [ ] Professional Summary
- [ ] Showcases Grid (3 Cards)
- [ ] Technology Stack Section
- [ ] Credentials Section
- [ ] Contact Section
- [ ] About Page (CV, Technical Topics)

---

### **Phase 2: CV Matcher MVP (Tag 3-5)**

**Tag 3: Authentication & Projects**
- [ ] Login Page
- [ ] Registration Page
- [ ] Dashboard Layout
- [ ] Sidebar Navigation
- [ ] Projects List
- [ ] Create Project
- [ ] Project Selection

**Tag 4: Document Upload & Management**
- [ ] File Upload Component (Drag & Drop)
- [ ] PDF/DOCX Upload to Backend
- [ ] Document List View
- [ ] Job Description Input
- [ ] Upload Progress Indicator
- [ ] Error Handling

**Tag 5: Matching & Results**
- [ ] Start Matching Button
- [ ] LLM Integration (Backend API)
- [ ] Results Display (Match Cards)
- [ ] Ranking by Match Score
- [ ] Skills List Component
- [ ] Gaps Analysis Display
- [ ] AI Analysis Detail View

---

### **Phase 3: Polish & Deploy (Tag 6-7)**

**Tag 6: UI/UX Polish**
- [ ] Responsive Design (Mobile, Tablet, Desktop)
- [ ] Loading States
- [ ] Error States
- [ ] Empty States
- [ ] Animations & Transitions
- [ ] Accessibility (ARIA labels, keyboard navigation)

**Tag 7: Testing & Deployment**
- [ ] Manual Testing (alle Flows)
- [ ] Cross-browser Testing
- [ ] Performance Optimization
- [ ] Build Optimization
- [ ] Deploy to Strato (SFTP)
- [ ] SSL Certificate Verification
- [ ] Final Testing on Production

---

## 🎯 MVP Features (Minimal Viable Product)

### **Must-Have für Launch:**

**Homepage:**
- ✅ Hero mit CTA
- ✅ Showcases Overview
- ✅ Contact Information
- ✅ About Page (CV)

**CV Matcher:**
- ✅ User Registration/Login
- ✅ Create Project
- ✅ Upload Job Description (Text)
- ✅ Upload CVs (PDF/DOCX)
- ✅ Run Matching (LLM)
- ✅ Display Results (Top 5 Matches)
- ✅ Match Score & Skills
- ✅ Logout

### **Nice-to-Have (Post-MVP):**

- 🔲 Batch Processing (>10 CVs)
- 🔲 Export Results (PDF Report)
- 🔲 Advanced Filters
- 🔲 Candidate Comparison View
- 🔲 Email Notifications
- 🔲 Team Collaboration
- 🔲 Historical Projects Archive

---

## 🔗 API Integration

**API Base URL:**
```typescript
const API_URL = "https://general-backend-production-a734.up.railway.app";
```

**API Client (from ARCHITECTURE.md):**
```typescript
export class APIClient {
  private token: string | null = null;
  private baseURL = API_URL;

  constructor(token?: string) {
    this.token = token || localStorage.getItem('token');
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async register(email: string, password: string) { ... }
  async login(email: string, password: string) { ... }
  async createProject(name: string, type: string, config = {}) { ... }
  async uploadDocument(file: File, projectId: string) { ... }
  async searchDocuments(query: string, projectId: string, limit = 5) { ... }
  async generateText(prompt: string, model?: string, provider = 'ollama') { ... }
}
```

---

## 📊 Success Metrics

### **Homepage:**
- [ ] Load Time < 3 seconds
- [ ] Mobile Responsive ✓
- [ ] All Sections Visible ✓
- [ ] Contact Form Working ✓

### **CV Matcher:**
- [ ] User can Register/Login
- [ ] User can Create Project
- [ ] User can Upload Documents
- [ ] Matching produces Results
- [ ] Results are ranked correctly
- [ ] AI Analysis is useful

---

## 🎉 Launch Checklist

### **Pre-Launch:**
- [ ] Backend 17/17 Tests passing
- [ ] Frontend builds without errors
- [ ] All pages load correctly
- [ ] Authentication flow works
- [ ] CV Matcher full flow works
- [ ] Mobile responsive tested
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Performance optimized (Lighthouse score >90)

### **Launch Day:**
- [ ] Deploy to Strato
- [ ] Verify SSL Certificate
- [ ] Test all URLs (www.dabrock.info/*)
- [ ] Smoke test all features
- [ ] Monitor error logs
- [ ] Update LinkedIn/social media
- [ ] Send to select beta users

### **Post-Launch:**
- [ ] Collect user feedback
- [ ] Fix critical bugs
- [ ] Add analytics (Google Analytics?)
- [ ] Plan Phase 2 features

---

## 💡 Marketing Copy für CV Matcher

### **Hero:**
> **CV Matcher - Enterprise Recruiting Intelligence**
>
> AI-powered semantic matching that understands context, not just keywords.
> Built with 20+ years enterprise architecture experience.

### **Value Propositions:**

1. **Semantic Understanding**
   - Goes beyond keyword matching
   - Understands context & experience
   - Vector similarity with pgvector

2. **AI-Powered Analysis**
   - Claude/Grok integration
   - Skill gap identification
   - Match explanations

3. **GDPR-Compliant**
   - EU-hosted (Railway EU)
   - Local LLM option (Ollama)
   - Data sovereignty guaranteed

4. **Enterprise-Grade**
   - Built by IBM/PwC architect
   - Scalable to thousands of CVs
   - Production-ready infrastructure

### **CTA:**
- Primary: "Start Matching Now"
- Secondary: "View Demo" / "Learn More"

---

## 🔐 Security Considerations

**Frontend:**
- [ ] JWT Token in localStorage (XSS protection needed)
- [ ] HTTPS only
- [ ] Input validation
- [ ] File upload size limits
- [ ] Sanitize user input

**Backend:**
- ✅ JWT Authentication
- ✅ CORS configured
- ✅ HTTPS/TLS
- ✅ SQL Injection protection (SQLAlchemy)
- ✅ Password hashing (bcrypt)

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md - Tablet */ }
@media (min-width: 1024px) { /* lg - Desktop */ }
@media (min-width: 1280px) { /* xl - Large Desktop */ }
```

---

## 🎯 Next Steps (Tomorrow Morning)

1. ☕ **Kaffee & Backend Fix** (2h)
2. 🚀 **React Project Init** (1h)
3. 💻 **Homepage Skeleton** (2h)
4. 🎨 **CV Matcher UI Start** (Rest of day)

**Bereit für www.dabrock.info/cvmatcher! 🚀**

---

*Erstellt: 21. Dezember 2025, 23:55 Uhr*
*Bereit für Homepage + CV Matcher Development*
