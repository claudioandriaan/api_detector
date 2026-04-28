# 🔍 API Detector for Web Scraping

A developer tool that automatically detects potential APIs (REST, GraphQL, JSON endpoints) from any website using Playwright and network inspection.

This tool helps web scraping developers quickly decide whether to:
- Use an API directly (fast & stable)
- Or fallback to HTML scraping

---

## 🚀 Features

- 🔎 Automatically captures network requests using Playwright
- 📦 Detects JSON-based API endpoints
- 🧠 Classifies API types:
  - REST APIs
  - GraphQL endpoints
  - POST-based APIs
- 📄 Validates if endpoints return usable JSON
- 🔁 Detects pagination patterns (page, offset, cursor, limit)
- 🌐 Streamlit UI for easy interaction
- 📊 Displays structured API results in browser

---

## 🏗️ Project Structure
```
api_detector/
│
├── app.py # Streamlit UI
├── core/
│ ├── browser.py # Playwright network capture
│ ├── analyzer.py # API filtering & classification
│ ├── validator.py # Endpoint validation
│ └── utils.py # Helper functions
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the project

```bash
git clone https://github.com/claudioandriaan/api_detector.git
cd api-detector

2. Create virtual environment (Python 3.11 recommended)

py -3.11 -m venv venv
Activate:
Windows (CMD): venv\Scripts\activate

Git Bash: source venv/Scripts/activate

3. Install dependencies
pip install -r requirements.txt

4. Install Playwright browsers
playwright install

▶️ Run the app
streamlit run app.py

Then open:
http://localhost:8501
```
🧪 How it works


User enters a website URL in Streamlit

Playwright opens the page in headless mode

All network responses are captured
JSON responses are filtered as API candidates

Each endpoint is:

Classified (REST / GraphQL / POST API)

Validated (real JSON response check)

Analyzed for pagination patterns

Results are displayed in the UI



📦 Example Output
```JSON
{  "endpoint": "https://example.com/api/products?page=1",  "type": "REST_GET",  "method": "GET",  "reusable": true,  "pagination": true}
```

🧠 Use Cases

Web scraping optimization (API vs HTML decision)

Reverse engineering frontend APIs

Finding hidden endpoints in SPA applications

Improving scraping performance and stability


⚠️ Limitations
Cannot detect fully private APIs 
requiring authentication

WebSocket-based APIs require extension

Some APIs may require session headers/cookies to replay


🔧 Tech Stack
Python 3.11+
Playwright
Streamlit
Requests


🚀 Future Improvements
Proxy support (residential / rotating IPs)
Request replay generator (convert API → Python code)
Export results (JSON / CSV)
Authentication session capture
Queue system for bulk URL scanning


👨‍💻 Author
Built by a web scraping developer focused on automation, data extraction, and reverse engineering web systems.

📜 License
MIT License
---If you want next step, I can also help you:
- turn this into a **GitHub-ready professional repo (badges + CI + docker)**- or add a **“copy scraping script” button inside Streamlit** (very powerful for your workflow)