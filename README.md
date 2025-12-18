# QA Site Check 

QA Site Check is a full-stack web application that analyzes websites from a Quality Assurance (QA) perspective.

It provides automated checks for:
- Performance
- Security
- Accessibility (WCAG)
- HTML & Code Quality
- Basic SEO

The backend performs the analysis and the frontend displays a visual QA report.

---

## Tech Stack

### Backend
- FastAPI
- Playwright 
- BeautifulSoup
- Google PageSpeed Insights API
- VirusTotal API
- AI feedback (Anthropic)

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS 
- lucide-react (icons)

---

## Run Locally

### Backend Setup

cd backend  
python -m venv .venv  
source .venv/bin/activate   (Windows: .venv\Scripts\activate)  
pip install -r requirements.txt  
playwright install  
uvicorn app.main:app 

Backend runs on: http://localhost:8000

---

### Frontend Setup

cd frontend  
npm install  
npm run dev  

Frontend runs on: http://localhost:5173

---

## Environment Variables (Backend)

Create a `.env` file in `backend/` from `.env.example`:

GOOGLE_PAGESPEED_API_KEY=  
VIRUSTOTAL_API_KEY=  
ANTHROPIC_API_KEY=  

---

## Environment Variables (Frontend)

Create a `.env` file in `frontend/` from `.env.example` if you need to override the API base URL:

VITE_API_BASE=http://localhost:8000
