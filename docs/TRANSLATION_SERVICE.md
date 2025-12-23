# Translation Service Documentation

## Overview

The Translation Service provides centralized multi-language support for all frontend applications. Currently supports **German (DE)**, **English (EN)**, and **Spanish (ES)**.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Frontend Applications                │
│          (CV Matcher, PrivateGPT, etc.)             │
│                                                      │
│  GET /translations/{language}                       │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Translation API Router                  │
│          backend/api/translations.py                 │
│                                                      │
│  - GET /translations/{language}                     │
│  - GET /translations/key/{key}                      │
│  - GET /translations/languages                      │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            Translation Service                       │
│      backend/services/translation_service.py         │
│                                                      │
│  - UI_TRANSLATIONS: Dict[str, Dict[Language, str]]  │
│  - LLM_PROMPTS: Dict[str, Dict[Language, str]]      │
│  - translate(key, lang, **kwargs) -> str            │
│  - get_all_translations(lang) -> Dict               │
│  - get_llm_prompt(key, lang, **kwargs) -> str       │
└─────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL
**Production**: `https://general-backend-production-a734.up.railway.app`
**Local**: `http://localhost:8000`

All endpoints are under the `/translations` prefix.

---

### 1. Get All Translations

**Endpoint**: `GET /translations/{language}`

**Description**: Retrieves all UI translations for the specified language.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `language` | path | Yes | Language code: `de`, `en`, or `es` |

**Response**:
```json
{
  "language": "en",
  "translations": {
    "app_title": "CV Matcher",
    "match_button": "Start Match",
    "analyzing": "Analyzing...",
    "strengths_title": "Strengths",
    "gaps_title": "Gaps",
    "recommendations_title": "Recommendations",
    ...
  }
}
```

**Status Codes**:
- `200 OK`: Translations retrieved successfully
- `422 Unprocessable Entity`: Invalid language code
- `500 Internal Server Error`: Server error

**Example Request**:
```bash
curl https://general-backend-production-a734.up.railway.app/translations/en
```

**Example Response**:
```json
{
  "language": "en",
  "translations": {
    "app_title": "CV Matcher",
    "llm_toggle_local": "🏠 Local (GDPR)",
    "llm_toggle_grok": "⚡ GROK (non-GDPR)",
    "match_button": "Start Match",
    "analyzing": "Analyzing...",
    "progress_loading_docs": "Loading documents...",
    "progress_analyzing_employer": "Analyzing employer requirements...",
    "progress_analyzing_applicant": "Analyzing applicant profile...",
    "progress_llm_running": "LLM analysis running...",
    "progress_generating_results": "Generating results...",
    "progress_finalizing": "Finalizing...",
    "progress_completed": "Completed!",
    "match_high": "Excellent Match",
    "match_medium": "Moderate Match",
    "match_low": "Low Match",
    "strengths_title": "Strengths",
    "gaps_title": "Gaps",
    "recommendations_title": "Recommendations",
    "detailed_analysis_title": "Detailed Analysis",
    "comparison_title": "Detailed Comparison",
    "comparison_requirement": "Requirement",
    "comparison_applicant_match": "Applicant Match",
    "comparison_details": "Details",
    "comparison_level": "Level",
    "comparison_confidence": "Confidence",
    "match_level_full": "Full",
    "match_level_partial": "Partial",
    "match_level_missing": "Missing",
    "pdf_download_button": "Download PDF Report",
    "pdf_generating": "Generating PDF...",
    "pdf_with_chat": "with {count} chat messages",
    "chat_title": "💬 Interactive Chat",
    "chat_clear_button": "Clear History",
    "chat_empty_message": "Ask questions about the analysis or uploaded documents.",
    "chat_examples": "Examples:",
    "chat_example_1": "Why is the match score 75%?",
    "chat_example_2": "Which skills are missing?",
    "chat_example_3": "Does the applicant have AWS experience?",
    "chat_input_placeholder": "Enter question...",
    "chat_send_button": "Send",
    "chat_user_label": "You",
    "chat_assistant_label": "Assistant",
    "chat_sources_label": "Sources:",
    "error_upload_failed": "Upload failed: {error}",
    "error_analysis_failed": "Analysis error. Please try again.",
    "error_need_documents": "Please add documents for both sides",
    "error_pdf_failed": "PDF download failed: {error}",
    "error_chat_failed": "Error: {error}"
  }
}
```

---

### 2. Get Single Translation

**Endpoint**: `GET /translations/key/{key}`

**Description**: Retrieves a single translation by key.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | path | Yes | Translation key (e.g., `app_title`) |
| `language` | query | No | Language code (default: `de`) |

**Response**:
```json
{
  "key": "app_title",
  "value": "CV Matcher",
  "language": "en"
}
```

**Example Request**:
```bash
curl "https://general-backend-production-a734.up.railway.app/translations/key/match_button?language=es"
```

**Example Response**:
```json
{
  "key": "match_button",
  "value": "Iniciar Match",
  "language": "es"
}
```

---

### 3. Get Supported Languages

**Endpoint**: `GET /translations/languages`

**Description**: Returns list of all supported languages.

**Parameters**: None

**Response**:
```json
{
  "languages": [
    {
      "code": "de",
      "name": "Deutsch",
      "flag": "🇩🇪"
    },
    {
      "code": "en",
      "name": "English",
      "flag": "🇬🇧"
    },
    {
      "code": "es",
      "name": "Español",
      "flag": "🇪🇸"
    }
  ]
}
```

**Example Request**:
```bash
curl https://general-backend-production-a734.up.railway.app/translations/languages
```

---

## Translation Service API

### Python API (Backend Usage)

```python
from backend.services.translation_service import translation_service

# Get single translation
title = translation_service.translate("app_title", "en")
# Returns: "CV Matcher"

# Translation with variable interpolation
message = translation_service.translate(
    "pdf_with_chat",
    "de",
    count=5
)
# Returns: "mit 5 Chat-Nachrichten"

# Get all translations for a language
translations = translation_service.get_all_translations("es")
# Returns: Dict[str, str] with all Spanish translations

# Get LLM prompt template
prompt = translation_service.get_llm_prompt(
    "match_analysis",
    "en",
    cv_text="John Doe, 5 years Python...",
    job_description="Looking for Senior Python Developer..."
)
# Returns: Formatted English prompt for match analysis
```

---

## Translation Keys Reference

### Header & Navigation
- `app_title`: Application title
- `llm_toggle_local`: Local LLM toggle label
- `llm_toggle_grok`: Grok API toggle label

### Progress Messages
- `progress_loading_docs`: Loading documents message
- `progress_analyzing_employer`: Analyzing employer requirements
- `progress_analyzing_applicant`: Analyzing applicant profile
- `progress_llm_running`: LLM analysis running
- `progress_generating_results`: Generating results
- `progress_finalizing`: Finalizing
- `progress_completed`: Completed

### Match Results
- `match_button`: Start match button
- `analyzing`: Analyzing state
- `match_high`: High match score label (≥70%)
- `match_medium`: Medium match score label (40-69%)
- `match_low`: Low match score label (<40%)
- `strengths_title`: Strengths section title
- `gaps_title`: Gaps section title
- `recommendations_title`: Recommendations section title
- `detailed_analysis_title`: Detailed analysis section title

### Comparison Table
- `comparison_title`: Comparison table title
- `comparison_requirement`: Requirement column header
- `comparison_applicant_match`: Applicant match column header
- `comparison_details`: Details column header
- `comparison_level`: Level column header
- `comparison_confidence`: Confidence column header
- `match_level_full`: Full match label
- `match_level_partial`: Partial match label
- `match_level_missing`: Missing match label

### PDF Generation
- `pdf_download_button`: PDF download button text
- `pdf_generating`: PDF generation in progress
- `pdf_with_chat`: PDF with chat messages label (uses `{count}` variable)

### Chat Interface
- `chat_title`: Chat section title
- `chat_clear_button`: Clear chat history button
- `chat_empty_message`: Empty chat placeholder
- `chat_examples`: Examples header
- `chat_example_1`: Example question 1
- `chat_example_2`: Example question 2
- `chat_example_3`: Example question 3
- `chat_input_placeholder`: Chat input placeholder
- `chat_send_button`: Send button text
- `chat_user_label`: User label
- `chat_assistant_label`: Assistant label
- `chat_sources_label`: Sources label

### Error Messages
- `error_upload_failed`: Upload failure (uses `{error}` variable)
- `error_analysis_failed`: Analysis failure
- `error_need_documents`: Missing documents error
- `error_pdf_failed`: PDF download failure (uses `{error}` variable)
- `error_chat_failed`: Chat error (uses `{error}` variable)

### Homepage (dabrock.info)
#### Navigation
- `nav_about`: About navigation link
- `nav_showcases`: Showcases/Projects navigation link
- `nav_services`: Services navigation link
- `nav_contact`: Contact navigation link

#### Hero Section
- `hero_title`: Main headline (e.g., "AI Expert & Full-Stack Developer")
- `hero_subtitle`: Subtitle tagline

#### About Section
- `about_title`: About section title
- `about_p1`: About paragraph 1
- `about_p2`: About paragraph 2
- `about_p3`: About paragraph 3

#### Showcases Section
- `showcases_title`: Showcases section title
- `cv_matcher_tagline`: CV Matcher short description
- `live_demo`: Live demo button text
- `cv_matcher_functional_title`: Functional description section title
- `cv_matcher_functional_desc`: CV Matcher functional description
- `cv_matcher_feature_1`: Feature 1 - AI matching analysis
- `cv_matcher_feature_2`: Feature 2 - RAG chat
- `cv_matcher_feature_3`: Feature 3 - Multilingual support
- `cv_matcher_feature_4`: Feature 4 - PDF & URL processing
- `cv_matcher_feature_5`: Feature 5 - Detailed reports
- `cv_matcher_technical_title`: Technical description section title
- `cv_matcher_technical_desc`: CV Matcher technical overview
- `cv_matcher_tech_frontend`: Frontend tech stack label
- `cv_matcher_tech_backend`: Backend tech stack label
- `cv_matcher_tech_ai`: AI & ML stack label
- `cv_matcher_tech_features`: Features label
- `general_backend_desc`: General Backend project description
- `audiobook_desc`: Audiobook project description
- `tellmelife_desc`: TellmeLife project description
- `privatechatgxt_desc`: PrivateChatGxT project description

#### Services Section
- `services_title`: Services section title
- `service_1_title`: Service 1 title (LLM Integration)
- `service_1_desc`: Service 1 description
- `service_2_title`: Service 2 title (RAG Systems)
- `service_2_desc`: Service 2 description
- `service_3_title`: Service 3 title (API Development)
- `service_3_desc`: Service 3 description

#### Contact Section
- `contact_title`: Contact section title
- `contact_email`: Email label
- `contact_location`: Location label

#### Footer
- `footer_rights`: Copyright/rights reserved text

**Total**: ~110 translation keys (70 CV Matcher + 40 Homepage)

---

## Variable Interpolation

Some translations support variable substitution using `{variable_name}` syntax:

| Key | Variables | Example |
|-----|-----------|---------|
| `pdf_with_chat` | `{count}` | `"with 5 chat messages"` |
| `error_upload_failed` | `{error}` | `"Upload failed: Network timeout"` |
| `error_pdf_failed` | `{error}` | `"PDF download failed: Server error"` |
| `error_chat_failed` | `{error}` | `"Error: Connection refused"` |

**Frontend Usage**:
```typescript
const { t } = useLanguage();
const message = t('pdf_with_chat', { count: chatMessages.length });
// Returns: "mit 5 Chat-Nachrichten" (DE)
// Returns: "with 5 chat messages" (EN)
// Returns: "con 5 mensajes de chat" (ES)
```

---

## Adding New Translations

### Step 1: Add to Backend Service

Edit `backend/services/translation_service.py`:

```python
UI_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
    # ... existing translations ...

    # Add new key
    "new_feature_title": {
        "de": "Neue Funktion",
        "en": "New Feature",
        "es": "Nueva Función"
    },
}
```

### Step 2: Use in Frontend

```typescript
import { useLanguage } from '../contexts/LanguageContext';

function MyComponent() {
  const { t } = useLanguage();

  return (
    <h2>{t('new_feature_title')}</h2>
  );
}
```

### Step 3: Deploy

```bash
# Backend deploys automatically via Railway on push
cd GeneralBackend
git add backend/services/translation_service.py
git commit -m "Add new translation: new_feature_title"
git push

# Frontend
cd CV_Matcher
npm run build
# Upload to Strato via FileZilla or curl
```

---

## LLM Prompt Templates

The service also provides multi-language LLM prompt templates:

### Available Prompts

1. **`match_analysis`**: CV-Job matching analysis prompt
   - Variables: `{cv_text}`, `{job_description}`
   - Available in: DE, EN, ES
   - Use: CV Matcher match analysis

2. **`chat_rag_prompt`**: RAG-based chat prompt
   - Variables: `{system_context}`, `{context}`, `{message}`
   - Available in: DE, EN, ES
   - Use: Interactive chat with document context

### Usage Example

```python
from backend.services.translation_service import translation_service

# Get German match analysis prompt
prompt = translation_service.get_llm_prompt(
    "match_analysis",
    "de",
    cv_text=cv_content,
    job_description=job_content
)

# Generate with LLM
response = llm_gateway.generate(prompt, provider="grok")
```

---

## Testing

### Test Endpoints

```bash
# Test German translations
curl https://general-backend-production-a734.up.railway.app/translations/de | jq .

# Test English translations
curl https://general-backend-production-a734.up.railway.app/translations/en | jq .

# Test Spanish translations
curl https://general-backend-production-a734.up.railway.app/translations/es | jq .

# Test single key
curl "https://general-backend-production-a734.up.railway.app/translations/key/match_button?language=es" | jq .

# Test languages list
curl https://general-backend-production-a734.up.railway.app/translations/languages | jq .
```

### Test Frontend Integration

1. Open https://www.dabrock.info/cv-matcher/
2. Click language toggle: 🇩🇪 🇬🇧 🇪🇸
3. Verify all UI elements translate
4. Check browser console for API calls to `/translations/{lang}`
5. Check localStorage for `cv_matcher_language`

---

## Swagger/OpenAPI Documentation

The Translation API is automatically documented in FastAPI's interactive Swagger UI:

**URL**: https://general-backend-production-a734.up.railway.app/docs

Navigate to the **"translations"** section to see:
- All endpoint schemas
- Request/response models
- Try out endpoints interactively

**Tags**: `translations`

### Swagger Schema

```yaml
openapi: 3.0.0
info:
  title: General Backend
  version: 1.0.0

paths:
  /translations/{language}:
    get:
      tags:
        - translations
      summary: Get Translations
      parameters:
        - name: language
          in: path
          required: true
          schema:
            type: string
            enum: [de, en, es]
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TranslationResponse'

  /translations/key/{key}:
    get:
      tags:
        - translations
      summary: Get Translation Key
      parameters:
        - name: key
          in: path
          required: true
          schema:
            type: string
        - name: language
          in: query
          required: false
          schema:
            type: string
            enum: [de, en, es]
            default: de

  /translations/languages:
    get:
      tags:
        - translations
      summary: Get Supported Languages

components:
  schemas:
    TranslationResponse:
      type: object
      properties:
        language:
          type: string
          enum: [de, en, es]
        translations:
          type: object
          additionalProperties:
            type: string
```

---

## Performance & Caching

### Backend
- Translations stored in memory (Python dict)
- No database queries needed
- Response time: <10ms

### Frontend
- Translations fetched once per language switch
- Stored in React Context state
- LocalStorage caches language preference
- No re-fetch on component re-renders

### Optimization Recommendations
1. **Service Worker**: Cache `/translations/{lang}` responses
2. **CDN**: Serve translation responses from edge
3. **Bundle Splitting**: Load only active language in build

---

## Troubleshooting

### Issue: Translations not loading

**Symptoms**: UI shows translation keys instead of text (e.g., "match_button" instead of "Start Match")

**Causes**:
1. Backend not deployed
2. CORS blocking requests
3. Network error

**Solution**:
```bash
# Check backend health
curl https://general-backend-production-a734.up.railway.app/health

# Check translations endpoint
curl https://general-backend-production-a734.up.railway.app/translations/en

# Check browser console for errors
# Open DevTools → Console → Look for failed requests
```

---

### Issue: Some texts still in German after switching language

**Symptoms**: Header translates but body stays German

**Cause**: Component not using `useLanguage()` hook

**Solution**: Add translation hook to component:
```typescript
import { useLanguage } from '../contexts/LanguageContext';

function MyComponent() {
  const { t } = useLanguage();  // Add this

  return <button>{t('my_button')}</button>;  // Use t()
}
```

---

### Issue: Variable interpolation not working

**Symptoms**: Text shows `{count}` instead of actual number

**Cause**: Not passing variables to `t()` function

**Solution**:
```typescript
// ❌ Wrong
<span>{t('pdf_with_chat')}</span>

// ✅ Correct
<span>{t('pdf_with_chat', { count: messages.length })}</span>
```

---

## Migration Guide

### Migrating Existing Component to i18n

**Before**:
```typescript
function MyComponent() {
  return (
    <div>
      <h1>CV Matcher</h1>
      <button>Match Starten</button>
      <p>Fehler: Upload fehlgeschlagen</p>
    </div>
  );
}
```

**After**:
```typescript
import { useLanguage } from '../contexts/LanguageContext';

function MyComponent() {
  const { t } = useLanguage();

  return (
    <div>
      <h1>{t('app_title')}</h1>
      <button>{t('match_button')}</button>
      <p>{t('error_upload_failed', { error: 'Network timeout' })}</p>
    </div>
  );
}
```

---

## Future Enhancements

### Planned Features
1. **More Languages**: French (FR), Italian (IT), Portuguese (PT)
2. **Dynamic Translation Loading**: Load translations on-demand per component
3. **Translation Management UI**: Admin interface to edit translations
4. **Pluralization Support**: Handle singular/plural forms
5. **Date/Number Formatting**: Locale-specific formatting
6. **RTL Support**: Right-to-left languages (Arabic, Hebrew)

### LLM Prompt Language Detection
Currently LLM prompts are hardcoded in German. Future enhancement:

```typescript
// Frontend sends language parameter
const result = await llmService.analyzeMatch(
  cvText,
  jobText,
  llmType,
  language  // Pass current language
);

// Backend uses language-specific prompt
prompt = translation_service.get_llm_prompt(
    "match_analysis",
    request.language,  // Use user's language
    cv_text=request.cv_text,
    job_description=request.job_description
)
```

---

## Related Documentation

- [I18N Implementation Guide](../../CV_Matcher/docs/I18N_DOCUMENTATION.md)
- [API Overview](./API.md)
- [Frontend Integration](../../CV_Matcher/README.md)

---

## Support

**Issues**: https://github.com/md20210/general-backend/issues
**Backend URL**: https://general-backend-production-a734.up.railway.app
**Swagger Docs**: https://general-backend-production-a734.up.railway.app/docs

---

**Last Updated**: 2025-12-23
**Version**: 1.0.0
**Supported Languages**: German (DE), English (EN), Spanish (ES)
**Total Translation Keys**: ~70
