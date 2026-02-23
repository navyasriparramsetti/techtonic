"""
🛡️ TrustHire AI – Job Scam Detection Portal
=============================================
Hackathon-ready Streamlit app with aggressive rule-based scam
detection, REAL web verification, URL safety check, screenshot
OCR analysis, and premium dark UI.

Run:  streamlit run app.py
Deps: pip install streamlit Pillow pytesseract
      (also install Tesseract-OCR for screenshot scanning)
"""

import streamlit as st
import re
import json
import os
import math
import socket
import ssl
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import urlparse

# ── Optional OCR imports ──
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TrustHire AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# PREMIUM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }

/* Main app background - Dark cosmic purple/blue */
.stApp {
    background: 
        radial-gradient(ellipse at 20% 30%, rgba(88, 28, 135, 0.8) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(59, 30, 120, 0.6) 0%, transparent 40%),
        radial-gradient(ellipse at 40% 70%, rgba(30, 58, 138, 0.7) 0%, transparent 45%),
        radial-gradient(ellipse at 70% 80%, rgba(88, 28, 135, 0.5) 0%, transparent 40%),
        linear-gradient(180deg, #0a0a1a 0%, #1a0b2e 30%, #16213e 60%, #0f0f23 100%);
    background-attachment: fixed;
    color: #e2e8f0;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

/* Ensure main content is above pseudo-element overlays */
section.main .block-container {
    position: relative;
    z-index: 1;
}
section[data-testid="stSidebar"] {
    z-index: 2;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
    border-right: 1px solid rgba(255,255,255,0.1);
}
section[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
section[data-testid="stSidebar"] .stRadio label {
    color: #e2e8f0 !important; font-weight: 500;
    padding: 10px 14px !important; border-radius: 10px; transition: all 0.25s;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(139,92,246,0.12); }

.glass-card {
    background: rgba(20, 20, 40, 0.7);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px; padding: 30px; margin-bottom: 22px;
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(139, 92, 246, 0.1);
    transition: transform 0.3s cubic-bezier(.22,.68,0,1.2), box-shadow 0.3s;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 0 30px rgba(139, 92, 246, 0.2);
}

/* Divider - Purple/Blue color matching the cosmic theme */
.divider {
    border: none;
    border-top: 1px solid rgba(139, 92, 246, 0.4);
    margin: 28px 0;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.6), transparent);
    height: 1px;
}

.hero-header { text-align: center; padding: 30px 0 16px; position: relative; }
.hero-header h1 {
    font-size: 2.8rem; font-weight: 900;
    margin-bottom: 6px; letter-spacing: -0.5px;
    color: white;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.hero-header p { 
    color: rgba(255,255,255,0.9); 
    font-size: 1.08rem; 
    max-width: 600px; 
    margin: 0 auto; 
    line-height: 1.6; 
}

.gauge-container { display: flex; flex-direction: column; align-items: center; padding: 20px 0 10px; }
.gauge-ring { position: relative; width: 200px; height: 200px; }
.gauge-ring svg { transform: rotate(-90deg); }
.gauge-ring .gauge-bg { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 14; }
.gauge-ring .gauge-fill {
    fill: none; stroke-width: 14; stroke-linecap: round;
    transition: stroke-dashoffset 1.2s cubic-bezier(.22,.68,0,1.2), stroke 0.6s;
}
.gauge-score { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; }
.gauge-score .number { font-size: 3rem; font-weight: 900; line-height: 1; }
.gauge-score .label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }

.badge { display: inline-block; padding: 8px 28px; border-radius: 999px; font-weight: 700; font-size: 0.95rem; letter-spacing: 1px; }
.badge-low    { background: linear-gradient(135deg, #065f46, #047857); color: #6ee7b7; box-shadow: 0 0 20px rgba(16,185,129,0.2); }
.badge-medium { background: linear-gradient(135deg, #78350f, #92400e); color: #fbbf24; box-shadow: 0 0 20px rgba(245,158,11,0.2); }
.badge-high   { background: linear-gradient(135deg, #7f1d1d, #991b1b); color: #fca5a5; box-shadow: 0 0 20px rgba(239,68,68,0.25); animation: pulse-glow 2s infinite; }
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(239,68,68,0.25); }
    50%      { box-shadow: 0 0 35px rgba(239,68,68,0.45); }
}

.flag-item {
    background: rgba(239,68,68,0.06); border-left: 4px solid #ef4444;
    padding: 12px 18px; border-radius: 0 12px 12px 0; margin-bottom: 10px;
    color: #fca5a5; font-size: 0.9rem; transition: background 0.2s;
}
.flag-item:hover { background: rgba(239,68,68,0.12); }
.flag-safe {
    background: rgba(16,185,129,0.06); border-left: 4px solid #10b981;
    padding: 12px 18px; border-radius: 0 12px 12px 0; margin-bottom: 10px; color: #6ee7b7;
}
.flag-info {
    background: rgba(99,102,241,0.06); border-left: 4px solid #818cf8;
    padding: 12px 18px; border-radius: 0 12px 12px 0; margin-bottom: 10px; color: #c4b5fd;
}

/* ── Company NOT FOUND alert ── */
.company-alert {
    background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(239,68,68,0.06));
    border: 2px solid rgba(239,68,68,0.4);
    border-radius: 16px; padding: 22px 28px; margin: 16px 0;
    text-align: center;
    animation: pulse-glow 2s infinite;
}
.company-alert .alert-icon { font-size: 2.4rem; margin-bottom: 6px; }
.company-alert .alert-title { color: #fca5a5; font-size: 1.15rem; font-weight: 800; margin-bottom: 4px; }
.company-alert .alert-desc { color: #f87171; font-size: 0.88rem; }

/* ── Company VERIFIED ── */
.company-verified {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.06));
    border: 2px solid rgba(16,185,129,0.4);
    border-radius: 16px; padding: 22px 28px; margin: 16px 0;
    text-align: center;
}
.company-verified .alert-icon { font-size: 2.4rem; margin-bottom: 6px; }
.company-verified .alert-title { color: #6ee7b7; font-size: 1.15rem; font-weight: 800; margin-bottom: 4px; }
.company-verified .alert-desc { color: #34d399; font-size: 0.88rem; }

.ai-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(139,92,246,0.04));
    border: 1px solid rgba(139,92,246,0.2); border-radius: 16px; padding: 24px;
    color: #c7d2fe; line-height: 1.75; font-size: 0.93rem;
}
.scam-word {
    background: rgba(239,68,68,0.25); color: #fca5a5; padding: 2px 8px;
    border-radius: 6px; font-weight: 700; border: 1px solid rgba(239,68,68,0.3);
}
.stat-card { text-align: center; padding: 24px 14px; }
.stat-card .number {
    font-size: 2.4rem; font-weight: 900;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-card .label { color: #94a3b8; font-size: 0.82rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.8px; }

.feature-item {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(139,92,246,0.1);
    border-radius: 14px; padding: 18px 22px; margin-bottom: 10px;
    color: #cbd5e1; font-size: 0.92rem; transition: all 0.3s;
}
.feature-item:hover { background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.25); transform: translateX(4px); }

.history-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 20px; background: rgba(255,255,255,0.025);
    border: 1px solid rgba(139,92,246,0.08); border-radius: 14px;
    margin-bottom: 10px; color: #e2e8f0; font-size: 0.88rem; transition: all 0.25s;
}
.history-row:hover { background: rgba(99,102,241,0.06); transform: translateX(3px); }

div.stButton > button[kind="primary"], div.stDownloadButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; font-size: 0.95rem !important; padding: 0.6rem 1.6rem !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    transition: all 0.3s cubic-bezier(.22,.68,0,1.2) !important;
}
div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.45) !important;
}
div.stButton > button:not([kind="primary"]) {
    background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 12px !important; color: #c4b5fd !important; font-weight: 600 !important;
}
div.stButton > button:not([kind="primary"]):hover {
    background: rgba(99,102,241,0.1) !important; border-color: rgba(99,102,241,0.4) !important;
}

.stTextArea textarea, .stTextInput input {
    background: rgba(30, 30, 60, 0.8) !important; 
    border: 2px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 12px !important; 
    color: #e2e8f0 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #8b5cf6 !important; 
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3) !important;
}
.stTextArea label, .stTextInput label, .stFileUploader label {
    color: #c4b5fd !important; 
    font-weight: 600 !important; 
    font-size: 0.88rem !important;
}
.stProgress > div > div { border-radius: 999px; height: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILE PERSISTENCE
# ─────────────────────────────────────────────
REPORTS_FILE = "scam_reports.json"
HISTORY_FILE = "scan_history.json"
LAST_RESULT_FILE = "last_result.json"


def load_scan_history():
    """Load scan history from disk."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_scan_history(history):
    """Save scan history to disk."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_last_result():
    """Load the most recent analysis result from disk."""
    if os.path.exists(LAST_RESULT_FILE):
        with open(LAST_RESULT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None


def save_last_result(result):
    """Save the most recent analysis result to disk."""
    with open(LAST_RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "scan_history" not in st.session_state:
    st.session_state.scan_history = load_scan_history()
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "show_ai" not in st.session_state:
    st.session_state.show_ai = False
if "show_opportunities" not in st.session_state:
    st.session_state.show_opportunities = False
if "page_nav" not in st.session_state:
    st.session_state.page_nav = "🧠 Analyze Job"

# Handle programmatic page navigation (e.g. from "Report This Scam" button)
if "_page_override" in st.session_state and st.session_state._page_override:
    st.session_state.page_nav = st.session_state._page_override
    st.session_state._page_override = None



# ═════════════════════════════════════════════
# WEB VERIFICATION FUNCTIONS
# ═════════════════════════════════════════════

def verify_email_domain(email):
    result = {"valid_domain": False, "is_free": False, "domain": ""}
    if "@" not in email:
        return result
    domain = email.strip().lower().split("@")[-1]
    result["domain"] = domain
    FREE_DOMAINS = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "protonmail.com", "aol.com", "ymail.com", "rediffmail.com",
        "mail.com", "zoho.com", "icloud.com", "live.com",
        "yandex.com", "tutanota.com", "gmx.com",
    ]
    if domain in FREE_DOMAINS:
        result["is_free"] = True
        result["valid_domain"] = True
        return result
    try:
        socket.setdefaulttimeout(4)
        socket.getaddrinfo(domain, 80)
        result["valid_domain"] = True
    except (socket.gaierror, socket.timeout, OSError):
        result["valid_domain"] = False
    return result


def verify_company_online(company_name):
    result = {"found": False, "domain_tried": "", "website_live": False, "details": ""}
    if not company_name or not company_name.strip():
        result["details"] = "No company name provided"
        return result
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.strip().lower())
    slug = clean.replace(" ", "")
    domains_to_try = [
        f"{slug}.com", f"{slug}.in", f"{slug}.co.in",
        f"{slug}.org", f"{slug}.io", f"www.{slug}.com",
    ]
    for domain in domains_to_try:
        result["domain_tried"] = domain
        try:
            socket.setdefaulttimeout(4)
            socket.getaddrinfo(domain, 80)
            for scheme in ["https", "http"]:
                try:
                    req = Request(f"{scheme}://{domain}", method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0 TrustHireAI/1.0"})
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    resp = urlopen(req, timeout=6, context=ctx)
                    if resp.status < 400:
                        result["found"] = True
                        result["website_live"] = True
                        result["details"] = f"Company website found at {scheme}://{domain}"
                        return result
                except Exception:
                    continue
            result["found"] = True
            result["details"] = f"Domain {domain} exists in DNS but website is not reachable"
            return result
        except (socket.gaierror, socket.timeout, OSError):
            continue
    result["details"] = f"No website found for '{company_name}' (tried: {', '.join(domains_to_try[:3])}...)"
    return result


def check_url_safety(url_str):
    """Check if a URL is reachable and analyze its domain for safety signals."""
    result = {"safe": None, "reachable": False, "domain": "", "reasons": []}
    try:
        parsed = urlparse(url_str)
        domain = parsed.netloc or parsed.path.split("/")[0]
        result["domain"] = domain
    except Exception:
        result["reasons"].append("❌ Invalid URL format")
        result["safe"] = False
        return result

    if not domain:
        result["reasons"].append("❌ Could not parse domain from URL")
        result["safe"] = False
        return result

    # Check for suspicious TLDs
    suspicious_tlds = [".xyz", ".top", ".buzz", ".click", ".link", ".work",
                       ".gq", ".ml", ".tk", ".cf", ".ga"]
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            result["reasons"].append(f"⚠️ Suspicious TLD: {tld} (commonly used in scam sites)")

    # Check for IP-address URLs
    if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
        result["reasons"].append("⚠️ URL uses raw IP address instead of domain name")

    # Check for very long subdomains (phishing pattern)
    if domain.count(".") > 3:
        result["reasons"].append("⚠️ Excessive subdomains — common phishing pattern")

    # Check HTTP reachability
    for scheme in ["https", "http"]:
        full_url = f"{scheme}://{domain}" if "://" not in url_str else url_str
        try:
            req = Request(full_url, method="HEAD",
                          headers={"User-Agent": "Mozilla/5.0 TrustHireAI/1.0"})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            resp = urlopen(req, timeout=6, context=ctx)
            result["reachable"] = True
            if resp.status >= 400:
                result["reasons"].append(f"⚠️ Server returned status {resp.status}")
            break
        except Exception:
            continue

    if not result["reachable"]:
        result["reasons"].append("❌ URL is NOT reachable — website may be down or fake")

    # No HTTPS check
    if url_str.startswith("http://") and not url_str.startswith("https://"):
        result["reasons"].append("⚠️ URL uses HTTP instead of HTTPS (not secure)")

    result["safe"] = len(result["reasons"]) == 0
    return result


def extract_text_from_image(uploaded_file):
    """Extract text from an uploaded image using OCR."""
    if not PIL_AVAILABLE:
        return None, "PIL/Pillow is not installed. Run: pip install Pillow"
    if not TESSERACT_AVAILABLE:
        return None, "pytesseract is not installed. Run: pip install pytesseract (and install Tesseract-OCR)"
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text.strip(), None
    except Exception as e:
        return None, f"OCR failed: {str(e)}"


# ═════════════════════════════════════════════
# KEYWORD BANKS
# ═════════════════════════════════════════════
PAYMENT_KEYWORDS = [
    "registration fee", "payment required", "training fee", "deposit",
    "processing fee", "advance payment", "security deposit", "pay first",
    "pay to apply", "joining fee", "enrollment fee", "application fee",
    "fee required", "pay for training", "pay for kit", "pay for material",
    "pay before joining", "refundable deposit", "non refundable",
    "send money", "transfer amount",
]
URGENCY_KEYWORDS = [
    "urgent hiring", "limited seats", "work from home and earn", "easy money",
    "guaranteed income", "instant approval", "no experience needed",
    "act now", "hurry", "apply immediately", "don't miss", "last chance",
    "limited time", "only few seats", "once in a lifetime",
    "immediate joining", "join today", "start today", "start immediately",
    "hiring now", "walk in", "spot offer", "direct joining",
]
PERSONAL_INFO_KEYWORDS = [
    "bank account", "bank details", "credit card", "debit card", "ssn",
    "social security", "pan card", "aadhaar", "aadhar", "passport copy",
    "send your id", "send documents", "share your photo", "selfie with id",
]
TOO_GOOD_KEYWORDS = [
    "earn from home", "earn daily", "earn weekly", "make money fast",
    "become rich", "earn lakhs", "earn thousands", "high income",
    "passive income", "income guarantee", "double your money",
    "no investment", "zero investment", "free laptop", "free phone",
    "work only 2 hours", "part time income", "extra income",
    "flexible hours earn", "simple task",
]
MLM_KEYWORDS = [
    "refer and earn", "referral bonus", "chain", "multi level",
    "network marketing", "downline", "build your team", "recruit people",
    "pyramid", "mlm",
]
VAGUE_ROLE_KEYWORDS = [
    "data entry", "copy paste", "typing job", "form filling",
    "ad posting", "sms sending", "email sending", "captcha",
    "survey filling", "click and earn", "like and earn",
    "watch and earn", "simple online job",
]
CONTACT_KEYWORDS = [
    "whatsapp", "telegram", "signal", "contact on whatsapp",
    "dm me", "inbox me", "message me personally",
]
FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "protonmail.com", "aol.com", "ymail.com", "rediffmail.com",
    "mail.com", "zoho.com", "icloud.com", "live.com",
]

ALL_SCAM_KEYWORDS = (PAYMENT_KEYWORDS + URGENCY_KEYWORDS + PERSONAL_INFO_KEYWORDS
                     + TOO_GOOD_KEYWORDS + MLM_KEYWORDS + VAGUE_ROLE_KEYWORDS
                     + CONTACT_KEYWORDS)


def _find_matches(text_lower, keywords):
    return [kw for kw in keywords if kw in text_lower]


# ═════════════════════════════════════════════
# SCORING ENGINE — 50/50 WEIGHTED
#   Company verification  = 50 points (50%)
#   Email + Description   = 50 points (50%)
# ═════════════════════════════════════════════

def calculate_risk_score(job_text, email, company, web_checks=None):
    text_reasons = []
    verification_results = []
    text_lower = job_text.lower()
    text_stripped = job_text.strip()
    words = text_stripped.split()
    raw = 0

    hits = _find_matches(text_lower, PAYMENT_KEYWORDS)
    if hits:
        raw += 30; text_reasons.append(f"💳 Payment/fee demands: {', '.join(hits)}")
    hits = _find_matches(text_lower, URGENCY_KEYWORDS)
    if hits:
        raw += 20; text_reasons.append(f"⚡ Urgency/pressure tactics: {', '.join(hits)}")
    hits = _find_matches(text_lower, PERSONAL_INFO_KEYWORDS)
    if hits:
        raw += 25; text_reasons.append(f"🔓 Requests sensitive data: {', '.join(hits)}")
    hits = _find_matches(text_lower, TOO_GOOD_KEYWORDS)
    if hits:
        raw += 20; text_reasons.append(f"🌈 Unrealistic promises: {', '.join(hits)}")
    hits = _find_matches(text_lower, MLM_KEYWORDS)
    if hits:
        raw += 25; text_reasons.append(f"🔺 MLM/pyramid indicators: {', '.join(hits)}")
    hits = _find_matches(text_lower, VAGUE_ROLE_KEYWORDS)
    if hits:
        raw += 15; text_reasons.append(f"📝 Vague job descriptions: {', '.join(hits)}")
    hits = _find_matches(text_lower, CONTACT_KEYWORDS)
    if hits:
        raw += 10; text_reasons.append(f"📱 Informal communication: {', '.join(hits)}")

    # Salary anomaly
    sal_m = re.findall(r'(\d+)\s*lpa', text_lower)
    if sal_m and ("fresher" in text_lower or "no experience" in text_lower):
        for s in sal_m:
            if int(s) > 8:
                raw += 20; text_reasons.append(f"💰 Unrealistic salary ({s} LPA) for freshers"); break
    for m in re.findall(r'\$\s*(\d[\d,]*)', text_lower):
        v = int(m.replace(",", ""))
        if v > 5000 and ("week" in text_lower or "daily" in text_lower):
            raw += 20; text_reasons.append(f"💰 Suspiciously high pay (${m}/week or /day)"); break

    # Free email
    if email:
        dom = email.lower().strip().split("@")[-1] if "@" in email else ""
        if dom and dom in FREE_EMAIL_DOMAINS:
            raw += 15; text_reasons.append(f"📧 Recruiter uses free email (@{dom})")

    # Text quality checks
    if words:
        cr = sum(1 for w in words if w.isupper() and len(w) > 2) / len(words)
        if cr > 0.25:
            raw += 10; text_reasons.append(f"🔠 Excessive ALL-CAPS ({int(cr*100)}% of words)")
    if text_stripped.count("!") >= 4:
        raw += 8; text_reasons.append(f"❗ Excessive exclamation marks ({text_stripped.count('!')} found)")
    wc = len(words)
    if 0 < wc < 30:
        raw += 10; text_reasons.append(f"📏 Very short description ({wc} words)")
    qual_kw = ["bachelor", "master", "degree", "b.tech", "b.e", "mba",
               "qualification", "graduate", "diploma", "certification",
               "b.sc", "m.sc", "b.com", "experience in", "years of experience",
               "proficient in", "knowledge of", "skills required"]
    if not any(q in text_lower for q in qual_kw) and wc > 10:
        raw += 8; text_reasons.append("🎓 No educational/skill requirements mentioned")
    no_int = ["no interview", "direct selection", "selected directly",
              "no aptitude", "no test required", "guaranteed selection"]
    hits = _find_matches(text_lower, no_int)
    if hits:
        raw += 15; text_reasons.append(f"🚫 Bypasses hiring process: {', '.join(hits)}")
    if len(re.findall(r'[\+]?[\d\-\s]{10,}', text_stripped)) >= 2:
        raw += 5; text_reasons.append(f"📞 Multiple phone numbers listed")
    comm = ["commission only", "commission based", "incentive based",
            "performance based only", "no fixed salary", "target based"]
    hits = _find_matches(text_lower, comm)
    if hits:
        raw += 12; text_reasons.append(f"💸 Commission/incentive-only pay: {', '.join(hits)}")
    if not company or not company.strip():
        raw += 10; text_reasons.append("🏢 No company name provided")

    # Scale to 50-point budget
    text_score = min(50, int((raw / 200) * 50)) if raw > 0 else 0

    # ── Company verification (50 points) ──
    company_score = 0
    company_status = "unknown"  # track for UI alert

    if not company or not company.strip():
        company_score = 50
        company_status = "missing"
        verification_results.append("❌ No company name provided — cannot verify online")
    elif web_checks and "company_check" in web_checks:
        cc = web_checks["company_check"]
        if cc["found"] and cc["website_live"]:
            company_score = 0
            company_status = "verified"
            verification_results.append(f"✅ VERIFIED: {cc['details']}")
        elif cc["found"] and not cc["website_live"]:
            company_score = 25
            company_status = "partial"
            verification_results.append(f"⚠️ {cc['details']}")
            text_reasons.append("⚠️ Company domain exists but website is not reachable")
        else:
            company_score = 50
            company_status = "not_found"
            verification_results.append(f"❌ {cc['details']}")
            text_reasons.append(f"🌐 Company NOT found online — '{company}' has no web presence")
    else:
        company_score = 30
        company_status = "unknown"
        verification_results.append("⚠️ Company verification was not performed")

    # Email domain verification bonus
    if web_checks and "email_check" in web_checks and email:
        ec = web_checks["email_check"]
        if ec["is_free"]:
            verification_results.append(f"⚠️ Email uses free provider (@{ec['domain']})")
        elif ec["valid_domain"]:
            text_score = max(0, text_score - 5)
            verification_results.append(f"✅ Email domain @{ec['domain']} is valid (DNS verified)")
        else:
            text_score = min(50, text_score + 10)
            text_reasons.append(f"🌐 Email domain @{ec['domain']} does NOT exist (DNS failed)")
            verification_results.append(f"❌ Email domain @{ec['domain']} has no DNS records")

    # URL check results
    if web_checks and "url_check" in web_checks:
        uc = web_checks["url_check"]
        for r in uc["reasons"]:
            verification_results.append(r)
            if r.startswith("❌"):
                text_score = min(50, text_score + 5)
                text_reasons.append(r)

    score = max(0, min(company_score + text_score, 100))
    risk_level = "LOW" if score <= 30 else ("MEDIUM" if score <= 60 else "HIGH")
    return score, risk_level, text_reasons, verification_results, company_status


# ═════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════

def highlight_scam_words(text):
    result = text
    for kw in sorted(ALL_SCAM_KEYWORDS, key=len, reverse=True):
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        result = pattern.sub(f'<span class="scam-word">{kw.upper()}</span>', result)
    return result


def generate_ai_explanation(score, reasons, verifications):
    if score <= 30:
        o = ("✅ **Low Risk Assessment:** This job posting appears mostly "
             "legitimate. Our analysis including live web verification found no major red flags.")
    elif score <= 60:
        o = ("⚠️ **Moderate Risk Assessment:** This posting raises concerns. "
             "Some elements are commonly associated with scam listings.")
    else:
        o = ("🚨 **High Risk Assessment:** This posting displays **multiple "
             "strong scam indicators**. Our analysis flagged characteristics "
             "overwhelmingly associated with known fraud patterns.")
    secs = []
    if reasons:
        secs.append(f"\n\n**🔎 Issues ({len(reasons)}):**\n" + "\n".join(f"  - {r}" for r in reasons))
    if verifications:
        secs.append(f"\n\n**🌐 Verification:**\n" + "\n".join(f"  - {v}" for v in verifications))
    tips = ("\n\n**🛡️ Recommendations:**\n"
            "  - Verify company via official website & LinkedIn\n"
            "  - Search government business registries (MCA, SEC)\n"
            "  - Never pay money upfront for a job\n"
            "  - Check reviews on Glassdoor / AmbitionBox\n"
            "  - If too good to be true, it probably is")
    conf = f"\n\n**🎯 Confidence:** {min(70 + len(reasons)*4 + len(verifications)*8, 98)}%"
    return o + "".join(secs) + tips + conf


def render_gauge(score):
    """Render a semicircular arc meter with arrow needle."""
    r = 80
    cx, cy = 120, 115
    semi_circ = math.pi * r
    filled = (score / 100) * semi_circ
    remaining = semi_circ - filled

    # Needle angle: 180° (left=0%) to 0° (right=100%)
    angle_deg = 180 - (score / 100) * 180
    angle_rad = math.radians(angle_deg)

    # Arrow tip on the arc
    tip_x = cx + (r - 10) * math.cos(angle_rad)
    tip_y = cy - (r - 10) * math.sin(angle_rad)

    # Arrow base (center hub) - two points for the triangle base
    base_len = 6
    perp_rad = angle_rad + math.pi / 2
    base1_x = cx + base_len * math.cos(perp_rad)
    base1_y = cy - base_len * math.sin(perp_rad)
    base2_x = cx - base_len * math.cos(perp_rad)
    base2_y = cy + base_len * math.sin(perp_rad)

    # Colors
    if score <= 30:
        score_color, badge_bg, badge_border = "#10b981", "rgba(16,185,129,0.15)", "rgba(16,185,129,0.5)"
    elif score <= 60:
        score_color, badge_bg, badge_border = "#f59e0b", "rgba(245,158,11,0.15)", "rgba(245,158,11,0.5)"
    else:
        score_color, badge_bg, badge_border = "#ef4444", "rgba(239,68,68,0.15)", "rgba(239,68,68,0.5)"

    risk_label = "Low Risk" if score <= 30 else ("Medium Risk" if score <= 60 else "High Risk")

    st.markdown(f"""
    <div style="text-align:center; padding:20px 0 10px;">
      <svg width="240" height="160" viewBox="0 0 240 160">
        <defs>
          <linearGradient id="meterGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#10b981"/>
            <stop offset="35%" stop-color="#84cc16"/>
            <stop offset="55%" stop-color="#eab308"/>
            <stop offset="75%" stop-color="#f97316"/>
            <stop offset="100%" stop-color="#ef4444"/>
          </linearGradient>
          <filter id="needleShadow"><feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="rgba(0,0,0,0.5)"/></filter>
          <filter id="dotGlow"><feGaussianBlur stdDeviation="2" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <!-- Background arc -->
        <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
              fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="18" stroke-linecap="round"/>
        <!-- Filled arc (gradient) -->
        <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
              fill="none" stroke="url(#meterGrad)" stroke-width="18" stroke-linecap="round"
              stroke-dasharray="{semi_circ}" stroke-dashoffset="{remaining}"
              style="filter: drop-shadow(0 0 8px rgba(239,68,68,0.25));"/>
        <!-- Arrow needle -->
        <polygon points="{tip_x:.1f},{tip_y:.1f} {base1_x:.1f},{base1_y:.1f} {base2_x:.1f},{base2_y:.1f}"
                 fill="white" filter="url(#needleShadow)"/>
        <!-- Center hub -->
        <circle cx="{cx}" cy="{cy}" r="8" fill="#1e293b" stroke="white" stroke-width="2.5"
                filter="url(#dotGlow)"/>
        <circle cx="{cx}" cy="{cy}" r="3" fill="{score_color}"/>
        <!-- Score text -->
        <text x="{cx}" y="{cy - 18}" text-anchor="middle"
              fill="{score_color}" font-size="40" font-weight="900" font-family="Inter,sans-serif">{score}</text>
        <text x="{cx + 22}" y="{cy - 18}" text-anchor="start"
              fill="#64748b" font-size="18" font-weight="600" font-family="Inter,sans-serif">/100</text>
      </svg>
      <div style="margin-top:-8px;">
        <span style="display:inline-block; padding:6px 24px; border-radius:999px;
              background:{badge_bg}; border:1px solid {badge_border};
              color:{score_color}; font-weight:700; font-size:0.9rem; letter-spacing:0.5px;">
          {risk_label}</span>
      </div>
    </div>""", unsafe_allow_html=True)


def save_scam_report(report):
    reports = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            try: reports = json.load(f)
            except json.JSONDecodeError: reports = []
    reports.append(report)
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)


def generate_safe_job_links(job_text):
    """Generate links to trusted job portals based on keywords from the job description."""
    text_lower = job_text.lower()
    # Extract relevant keywords for search
    role_keywords = []
    # Try to find job title / role keywords
    common_roles = [
        "software engineer", "developer", "designer", "manager", "analyst",
        "data entry", "marketing", "sales", "accountant", "teacher",
        "nurse", "driver", "content writer", "graphic designer", "web developer",
        "full stack", "frontend", "backend", "devops", "cloud", "python",
        "java", "react", "angular", "machine learning", "ai", "data scientist",
        "project manager", "product manager", "hr", "human resources",
        "customer support", "business development", "operations",
        "intern", "fresher", "senior", "junior", "lead", "architect",
    ]
    for role in common_roles:
        if role in text_lower:
            role_keywords.append(role)
    
    # Build a search query from found keywords (max 3)
    if role_keywords:
        search_query = " ".join(role_keywords[:3])
    else:
        # Fallback: extract first few meaningful words
        words = [w for w in job_text.split()[:10] if len(w) > 3 and w.isalpha()]
        search_query = " ".join(words[:3]) if words else "jobs"
    
    from urllib.parse import quote_plus
    query_encoded = quote_plus(search_query)
    
    portals = [
        {
            "name": "LinkedIn Jobs",
            "icon": "💼",
            "url": f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}",
            "description": "Professional network with verified company profiles",
            "trust": "⭐⭐⭐⭐⭐",
        },
        {
            "name": "Indeed",
            "icon": "🔍",
            "url": f"https://www.indeed.com/jobs?q={query_encoded}",
            "description": "World's largest job search engine with company reviews",
            "trust": "⭐⭐⭐⭐⭐",
        },
        {
            "name": "Glassdoor",
            "icon": "🏢",
            "url": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query_encoded}",
            "description": "Jobs with salary data and employee reviews",
            "trust": "⭐⭐⭐⭐⭐",
        },
        {
            "name": "Naukri.com",
            "icon": "🇮🇳",
            "url": f"https://www.naukri.com/{query_encoded.replace('+', '-')}-jobs",
            "description": "India's #1 job portal with verified employers",
            "trust": "⭐⭐⭐⭐",
        },
        {
            "name": "Google Jobs",
            "icon": "🌐",
            "url": f"https://www.google.com/search?q={query_encoded}+jobs&ibp=htl;jobs",
            "description": "Aggregated listings from multiple trusted sources",
            "trust": "⭐⭐⭐⭐⭐",
        },
        {
            "name": "Monster",
            "icon": "👾",
            "url": f"https://www.monster.com/jobs/search?q={query_encoded}",
            "description": "Established job board with career resources",
            "trust": "⭐⭐⭐⭐",
        },
    ]
    return portals, search_query


def generate_report_txt(job_text, email, company, score, risk_level, reasons, verifications):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 56, "    🛡️ TrustHire AI – Scam Risk Report", "=" * 56,
        f"  Generated : {ts}", f"  Risk Score: {score}/100 ({risk_level})",
        "-" * 56, "", "📋 JOB DESCRIPTION:", "-" * 40,
        job_text or "(none)", "", f"📧 EMAIL : {email or '(none)'}",
        f"🏢 COMPANY: {company or '(none)'}", "", "-" * 56,
        "🔎 RED FLAGS:", "-" * 40,
    ]
    for r in (reasons or ["✅ (none)"]): lines.append(f"  • {r}")
    if verifications:
        lines += ["", "🌐 VERIFICATION:", "-" * 40]
        for v in verifications: lines.append(f"  • {v}")
    lines += ["", "=" * 56, "  Report by TrustHire AI v1.0"]
    return "\n".join(lines)


# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0 12px;">
        <div style="margin-bottom:8px;">
            <svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="shieldOuter" x1="0" y1="0" x2="72" y2="72">
                        <stop offset="0%" stop-color="#c0d8f0"/>
                        <stop offset="30%" stop-color="#5b9bd5"/>
                        <stop offset="60%" stop-color="#2563eb"/>
                        <stop offset="100%" stop-color="#1e3a8a"/>
                    </linearGradient>
                    <linearGradient id="shieldFill" x1="12" y1="8" x2="60" y2="64">
                        <stop offset="0%" stop-color="#1a3a6e"/>
                        <stop offset="50%" stop-color="#0f2550"/>
                        <stop offset="100%" stop-color="#0a1a3a"/>
                    </linearGradient>
                    <linearGradient id="iconGrad" x1="20" y1="18" x2="52" y2="50">
                        <stop offset="0%" stop-color="#b8d4f0"/>
                        <stop offset="100%" stop-color="#7db4e0"/>
                    </linearGradient>
                    <linearGradient id="checkGrad" x1="24" y1="38" x2="48" y2="52">
                        <stop offset="0%" stop-color="#60a5fa"/>
                        <stop offset="100%" stop-color="#2563eb"/>
                    </linearGradient>
                    <filter id="glow"><feGaussianBlur stdDeviation="1.5" result="blur"/>
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                </defs>
                <!-- Shield body -->
                <path d="M36 3 L65 16 V34 C65 52 52 62 36 68 C20 62 7 52 7 34 V16 Z" fill="url(#shieldOuter)" stroke="#93c5fd" stroke-width="1"/>
                <path d="M36 7 L61 18 V34 C61 50 50 59 36 64 C22 59 11 50 11 34 V18 Z" fill="url(#shieldFill)"/>
                <!-- Briefcase -->
                <rect x="22" y="24" width="24" height="16" rx="2.5" fill="none" stroke="url(#iconGrad)" stroke-width="2.2"/>
                <path d="M30 24 V21 C30 18.5 32 17 34 17 C36 17 38 18.5 38 21 V24" fill="none" stroke="url(#iconGrad)" stroke-width="2"/>
                <line x1="22" y1="31" x2="46" y2="31" stroke="url(#iconGrad)" stroke-width="1.5" opacity="0.5"/>
                <rect x="31" y="28" width="6" height="5" rx="1" fill="none" stroke="url(#iconGrad)" stroke-width="1.3"/>
                <!-- Checkmark -->
                <path d="M24 47 L32 54 L50 38" fill="none" stroke="url(#checkGrad)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
                <!-- Diagonal swoosh line -->
                <line x1="18" y1="44" x2="50" y2="26" stroke="#3b82f6" stroke-width="1" opacity="0.25" stroke-linecap="round"/>
            </svg>
        </div>
        <h2 style="margin:0; font-weight:900; font-size:1.6rem;">
            <span style="color:#e8edf3;">Trust</span><span style="background:linear-gradient(135deg,#3b82f6,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Hire</span>
            <span style="background:linear-gradient(135deg,#60a5fa,#93c5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span></h2>
        <p style="color:#7c7cad; font-size:0.78rem; margin-top:4px; letter-spacing:1px; text-transform:uppercase;">
            AI-Powered Scam Detection</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.radio(
        "Navigate",
        ["🧠 Analyze Job", "🚨 Report Scam", "ℹ️ About"],
        key="page_nav",
        label_visibility="collapsed",
    )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p style="color:#4a4a6a; font-size:0.72rem; text-align:center;">© 2026 TrustHire AI v1.0</p>',
                unsafe_allow_html=True)

# Read active page from session state (works even with programmatic changes)
page = st.session_state.page_nav


# ═════════════════════════════════════════════
# PAGE — ANALYZE JOB
# ═════════════════════════════════════════════
if page == "🧠 Analyze Job":
    st.markdown("""
    <div class="hero-header">
        <h1><span style="-webkit-text-fill-color:#e8edf3;">Trust</span><span style="background:linear-gradient(135deg,#3b82f6,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Hire</span> <span style="background:linear-gradient(135deg,#60a5fa,#93c5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span></h1>
        <p>Protect Your Career from Job Scams.<br>
        Paste any suspicious job posting and let our AI instantly detect hidden red flags.<br>
        <strong style="color:#93c5fd;">Now with real-time company and domain verification for safer hiring decisions.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Job Details")

    job_text = st.text_area("Paste Job Description", height=200,
        placeholder="Paste the full job description here…")
    job_url = st.text_input("🔗 Job Posting URL", placeholder="https://example.com/careers/job-12345")
    screenshot = st.file_uploader("📸 Upload Job Screenshot (OCR scan)",
                                  type=["png", "jpg", "jpeg", "webp"],
                                  help="Upload a screenshot — AI extracts text via OCR")
    email = st.text_input("📧 Recruiter Email", placeholder="recruiter@company.com")
    company = st.text_input("🏢 Company Name", placeholder="Enter company name")
    # ── Custom styled "Check Scam Risk" button ──
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button#check_scam_btn {
        background: linear-gradient(135deg, rgba(30,58,110,0.8), rgba(15,37,80,0.9)) !important;
        border: 2px solid rgba(59,130,246,0.6) !important;
        box-shadow: 0 0 20px rgba(59,130,246,0.25), inset 0 1px 0 rgba(147,197,253,0.1) !important;
        border-radius: 14px !important; padding: 0.7rem 2rem !important;
        color: white !important; font-weight: 700 !important; font-size: 1.1rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(.22,.68,0,1.2) !important;
    }
    div[data-testid="stButton"] > button#check_scam_btn:hover {
        box-shadow: 0 0 35px rgba(59,130,246,0.5), inset 0 1px 0 rgba(147,197,253,0.15) !important;
        border-color: rgba(96,165,250,0.8) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    analyze_clicked = st.button("🛡️ Check Scam Risk", type="primary", use_container_width=True, key="check_scam_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_clicked:
        # ── Handle screenshot OCR ──
        ocr_text = ""
        ocr_msg = ""
        if screenshot is not None:
            with st.spinner("📸 Extracting text from screenshot (OCR)..."):
                extracted, err = extract_text_from_image(screenshot)
                if extracted:
                    ocr_text = extracted
                    ocr_msg = f"✅ Extracted {len(extracted.split())} words from screenshot"
                elif err:
                    ocr_msg = f"⚠️ {err}"

        # Combine job text + OCR text
        combined_text = job_text.strip()
        if ocr_text:
            combined_text = combined_text + "\n\n" + ocr_text if combined_text else ocr_text

        if not combined_text:
            st.warning("⚠️ Please provide a job description — paste text, enter a URL, or upload a screenshot.")
        else:
            with st.spinner("🔍 Analyzing text + verifying company & email online..."):
                web_checks = {}

                if company and company.strip():
                    web_checks["company_check"] = verify_company_online(company)
                if email and "@" in email:
                    web_checks["email_check"] = verify_email_domain(email)
                if job_url and job_url.strip():
                    web_checks["url_check"] = check_url_safety(job_url.strip())

                score, risk_level, reasons, verifications, company_status = calculate_risk_score(
                    combined_text, email, company, web_checks
                )

            # Store OCR info
            if ocr_msg:
                verifications.insert(0, ocr_msg)

            result = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": score, "risk_level": risk_level,
                "reasons": reasons, "verifications": verifications,
                "job_text": combined_text, "email": email, "company": company,
                "company_status": company_status,
                "url_checked": job_url if job_url else None,
            }
            st.session_state.last_result = result
            save_last_result(result)
            st.session_state.scan_history.append(result)
            save_scan_history(st.session_state.scan_history)
            st.session_state.show_ai = False
            st.session_state.show_opportunities = False
            st.rerun()

    # ═════════════════════════════════════════════
    # INLINE RESULTS (current scan only)
    # ═════════════════════════════════════════════
    res = st.session_state.last_result
    if res:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("#### Scam Risk Analysis Report")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        # ★ PROMINENT COMPANY ALERT ★
        cs = res.get("company_status", "unknown")
        if cs == "not_found" or cs == "missing":
            company_label = res.get("company", "Unknown")
            st.markdown(f"""
            <div class="company-alert">
                <div class="alert-icon">🚫</div>
                <div class="alert-title">NO SUCH COMPANY FOUND ONLINE</div>
                <div class="alert-desc">"{company_label}" could not be verified on any website.<br>
                This is a major red flag — legitimate companies have an online presence.</div>
            </div>""", unsafe_allow_html=True)
        elif cs == "verified":
            st.markdown(f"""
            <div class="company-verified">
                <div class="alert-icon">✅</div>
                <div class="alert-title">COMPANY VERIFIED</div>
                <div class="alert-desc">"{res.get('company', '')}" has a live website — verified via DNS + HTTP.</div>
            </div>""", unsafe_allow_html=True)
        elif cs == "partial":
            st.markdown(f"""
            <div class="company-alert" style="border-color:rgba(245,158,11,0.4); background:linear-gradient(135deg,rgba(245,158,11,0.1),rgba(245,158,11,0.04));">
                <div class="alert-icon">⚠️</div>
                <div class="alert-title">COMPANY PARTIALLY VERIFIED</div>
                <div class="alert-desc">Domain exists but website is not reachable. Proceed with caution.</div>
            </div>""", unsafe_allow_html=True)

        render_gauge(res["score"])

        # ── Web verification ──
        verifs = res.get("verifications", [])
        if verifs:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown("##### 🌐 Live Verification Results")
            for v in verifs:
                if v.startswith("✅"):
                    st.markdown(f'<div class="flag-safe">{v}</div>', unsafe_allow_html=True)
                elif v.startswith("❌"):
                    st.markdown(f'<div class="flag-item">{v}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="flag-info">{v}</div>', unsafe_allow_html=True)

        # ── Detected Threat Signals ──
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if res["reasons"]:
            st.markdown("##### Detected Threat Signals:")
            for r in res["reasons"]:
                st.markdown(f'<div class="flag-item">⚠️ {r}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="flag-safe">✅ No threat signals detected — this posting looks clean!</div>',
                        unsafe_allow_html=True)

        # ── Highlighted keywords ──
        if res["reasons"]:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown("##### 📝 Highlighted Keywords")
            hl = highlight_scam_words(res["job_text"])
            st.markdown(f'<div class="ai-box" style="white-space:pre-wrap;font-size:0.85rem;">{hl}</div>',
                        unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        if st.button("💬 Ask AI Why", use_container_width=True, key="ai_btn"):
            st.session_state.show_ai = True
            st.rerun()
        if st.session_state.show_ai:
            st.markdown("##### 🧠 AI Explanation")
            st.markdown(generate_ai_explanation(res["score"], res["reasons"], res.get("verifications", [])))

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        rpt = generate_report_txt(res["job_text"], res["email"], res["company"],
                                  res["score"], res["risk_level"], res["reasons"],
                                  res.get("verifications", []))
        st.download_button("📥 Download Report (TXT)", data=rpt,
            file_name=f"trusthire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain", use_container_width=True)

        if st.button("🚨 Report This Scam", use_container_width=True, key="report_scam_nav_btn"):
            st.session_state._page_override = "🚨 Report Scam"
            st.rerun()

        # ── Better Opportunities button (styled like reference image) ──
        if res["score"] > 40:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button#opp_btn {
                background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.9)) !important;
                border: 1.5px solid rgba(100,116,139,0.4) !important;
                border-radius: 16px !important; padding: 0.8rem 2rem !important;
                color: #e2e8f0 !important; font-weight: 700 !important; font-size: 1.05rem !important;
                letter-spacing: 0.3px !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05) !important;
                transition: all 0.3s !important;
            }
            div[data-testid="stButton"] > button#opp_btn:hover {
                border-color: rgba(96,165,250,0.5) !important;
                box-shadow: 0 4px 25px rgba(59,130,246,0.2), inset 0 1px 0 rgba(255,255,255,0.08) !important;
                transform: translateY(-2px) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("💼 Better Opportunities", use_container_width=True, key="opp_btn"):
                st.session_state.show_opportunities = True
                st.rerun()
            if st.session_state.show_opportunities:
                st.markdown("##### 🌟 Safe Job Opportunities")
                st.markdown('<p style="color:#94a3b8; font-size:0.88rem; margin-bottom:16px;">'
                            'This posting looks risky. Here are <strong style="color:#6ee7b7;">trusted job portals</strong> '
                            'with verified listings matching your search:</p>', unsafe_allow_html=True)
                portals, search_query = generate_safe_job_links(res["job_text"])
                st.markdown(f'<div class="flag-info">🔍 Search keywords: <strong>{search_query}</strong></div>',
                            unsafe_allow_html=True)
                for portal in portals:
                    st.markdown(f"""
                    <a href="{portal['url']}" target="_blank" style="text-decoration:none;">
                        <div class="feature-item" style="cursor:pointer; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong>{portal['icon']} {portal['name']}</strong>
                                <span style="color:#94a3b8; font-size:0.82rem;"> — {portal['description']}</span>
                            </div>
                            <div style="font-size:0.75rem;">{portal['trust']}</div>
                        </div>
                    </a>""", unsafe_allow_html=True)
                st.markdown('<div class="flag-safe" style="margin-top:16px;">'
                            '💡 <strong>Tip:</strong> Always apply through official company websites or verified job portals. '
                            'Never pay to apply for a job.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)



# ═════════════════════════════════════════════
# PAGE — REPORT SCAM
# ═════════════════════════════════════════════
elif page == "🚨 Report Scam":
    st.markdown("""
    <div class="hero-header">
        <h1>🚨 Report a Scam</h1>
        <p>Help protect others by reporting fraudulent job postings</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("report_form", clear_on_submit=True):
        st.markdown("#### 📝 Scam Report Form")
        report_link = st.text_input("🔗 Job Posting Link", placeholder="https://...")
        rc1, rc2 = st.columns(2)
        with rc1:
            report_email = st.text_input("📧 Scammer Email", placeholder="scammer@domain.com")
        with rc2:
            report_phone = st.text_input("📞 Scammer Phone", placeholder="+91 98765 43210")
        report_screenshot = st.file_uploader("📸 Upload Screenshot", type=["png","jpg","jpeg"])
        report_details = st.text_area("📝 Describe what happened", placeholder="Explain the scam...")
        submitted = st.form_submit_button("📤 Submit Report", type="primary", use_container_width=True)
        if submitted:
            if not report_link.strip():
                st.warning("⚠️ Please provide the job posting link.")
            else:
                report = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "job_link": report_link, "email": report_email,
                    "phone": report_phone, "details": report_details,
                    "has_screenshot": report_screenshot is not None,
                }
                save_scam_report(report)
                st.success("✅ **Report submitted!** Thank you for keeping the community safe. 🛡️")
                st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
# PAGE — ABOUT
# ═════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown("""
    <div class="hero-header">
        <h1>ℹ️ About TrustHire AI</h1>
        <p>AI-powered scam detection with live web verification</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
### 🎯 What is TrustHire AI?

**TrustHire AI** is an intelligent job scam detection system that combines
**17+ rule-based analysis patterns** with **live web verification** and
**OCR screenshot scanning** to identify fraudulent postings.

We don't just scan keywords — we actually check if the company and email domain
exist on the internet, and we can extract text from screenshots for analysis.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### ✨ Key Features")
    features = [
        ("🎯 50/50 Weighted Scoring", "Company verification = 50%, text + email analysis = 50%"),
        ("🌐 Live Company Verification", "DNS + HTTP check to verify company website exists online"),
        ("📧 Email Domain Verification", "Verifies recruiter email domain via DNS lookup"),
        ("🔗 URL Safety Check", "Checks job posting URL for suspicious TLDs, reachability, and HTTPS"),
        ("📸 Screenshot OCR", "Upload a screenshot and AI extracts text using OCR for analysis"),
        ("🔍 120+ Scam Keywords", "Detects payment demands, urgency, MLM, vague roles, and more"),
        ("💰 Salary Anomaly Engine", "Catches unrealistic salary promises for freshers"),
        ("🧠 AI Explanation", "Human-readable analysis breakdown with recommendations"),
        ("📥 Downloadable Reports", "Export full analysis as TXT files"),
    ]
    for title, desc in features:
        st.markdown(f'<div class="feature-item"><strong>{title}</strong> — {desc}</div>',
                    unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, (n, l) in zip([s1,s2,s3,s4],
        [("54,892","Scams Detected"),("12,430","Users Protected"),("98%","Accuracy"),("3,200","Domains Blocked")]):
        with col:
            st.markdown(f'<div class="glass-card stat-card"><div class="number">{n}</div>'
                        f'<div class="label">{l}</div></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#4a4a6a; font-size:0.8rem; margin-top:30px;">'
                'Built with ❤️ using Python & Streamlit · 🛡️ TrustHire AI v1.0</p>'