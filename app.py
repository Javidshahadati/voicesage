import streamlit as st
import requests
import base64
import re
from datetime import timedelta

st.set_page_config(
    page_title="VoiceSage",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Vazirmatn', sans-serif !important;
    background: #000 !important;
}
.stApp { background: transparent !important; }
.block-container {
    padding-top: 2rem !important;
    max-width: 900px !important;
}

/* شبکه‌ی نئون پس‌زمینه */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(6, 182, 212, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(6, 182, 212, 0.05) 1px, transparent 1px);
    background-size: 50px 50px;
    z-index: 0;
    pointer-events: none;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 40%, black 20%, transparent 80%);
    -webkit-mask-image: radial-gradient(ellipse 80% 60% at 50% 40%, black 20%, transparent 80%);
}

/* Hero */
.neon-hero {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 2rem 1rem 3rem;
}
.neon-line-top {
    width: 100px;
    height: 2px;
    background: #06b6d4;
    margin: 0 auto 2rem;
    box-shadow:
        0 0 10px #06b6d4,
        0 0 25px #06b6d4,
        0 0 50px #06b6d4;
    animation: lineGlow 2s ease-in-out infinite alternate;
}
.neon-hero h1 {
    font-size: 4rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -2px;
    line-height: 1;
    color: #fff;
    text-shadow:
        0 0 10px rgba(236, 72, 153, 0.9),
        0 0 30px rgba(236, 72, 153, 0.7),
        0 0 60px rgba(236, 72, 153, 0.4);
    animation: textPulse 3s ease-in-out infinite alternate;
}
.neon-hero p {
    font-size: 1.5rem;   /* ← فارسی بزرگ‌تر */
    color: #06b6d4;
    margin: 1.5rem 0;
    font-weight: 400;
    line-height: 1.8;
    letter-spacing: 0.5px;
    text-shadow:
        0 0 10px rgba(6, 182, 212, 0.7),
        0 0 25px rgba(6, 182, 212, 0.4);
}
.neon-line-mid {
    width: 100%;
    max-width: 500px;
    height: 1px;
    margin: 0 auto 2rem;
    background: linear-gradient(90deg, transparent, #ec4899, #06b6d4, #a855f7, transparent);
    box-shadow: 0 0 15px rgba(236, 72, 153, 0.5);
}
.neon-badges {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 2rem;
}
.neon-badge {
    padding: 0.7rem 1.4rem;
    background: transparent;
    border: 1px solid #06b6d4;
    border-radius: 6px;
    font-size: 1rem;   /* ← فارسی بزرگ‌تر */
    color: #06b6d4;
    letter-spacing: 1px;
    text-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
    box-shadow:
        0 0 10px rgba(6, 182, 212, 0.2),
        inset 0 0 10px rgba(6, 182, 212, 0.05);
    transition: all 0.3s;
}
.neon-badge:hover {
    background: rgba(6, 182, 212, 0.1);
    box-shadow:
        0 0 20px rgba(6, 182, 212, 0.5),
        inset 0 0 15px rgba(6, 182, 212, 0.1);
}

@keyframes lineGlow {
    from { box-shadow: 0 0 10px #06b6d4, 0 0 25px #06b6d4, 0 0 50px #06b6d4; }
    to { box-shadow: 0 0 15px #06b6d4, 0 0 35px #06b6d4, 0 0 70px #06b6d4; }
}
@keyframes textPulse {
    from { text-shadow: 0 0 10px rgba(236,72,153,0.9), 0 0 30px rgba(236,72,153,0.7), 0 0 60px rgba(236,72,153,0.4); }
    to { text-shadow: 0 0 15px rgba(236,72,153,1), 0 0 40px rgba(236,72,153,0.9), 0 0 80px rgba(236,72,153,0.6); }
}

/* دکمه‌ها */
.stButton > button {
    background: transparent !important;
    color: #06b6d4 !important;
    border: 1.5px solid #06b6d4 !important;
    border-radius: 8px !important;
    padding: 0.8rem 1.6rem !important;   /* ← بزرگ‌تر */
    font-weight: 600 !important;
    font-size: 1.05rem !important;   /* ← فارسی بزرگ‌تر */
    letter-spacing: 0.5px !important;
    text-shadow: 0 0 10px rgba(6, 182, 212, 0.5) !important;
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.2) !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background: rgba(6, 182, 212, 0.1) !important;
    box-shadow: 0 0 25px rgba(6, 182, 212, 0.5) !important;
    color: #67e8f9 !important;
}

/* فایل آپلودر */
div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(6, 182, 212, 0.4);
    border-radius: 16px;
    padding: 1rem;
    background: rgba(6, 182, 212, 0.03);
    box-shadow: inset 0 0 30px rgba(6, 182, 212, 0.05);
}

/* Textarea */
.stTextArea textarea {
    background: rgba(10, 10, 15, 0.9) !important;
    color: #fff !important;
    border-radius: 12px !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 1.05rem !important;   /* ← فارسی بزرگ‌تر */
    line-height: 1.9 !important;
    box-shadow: inset 0 0 20px rgba(6, 182, 212, 0.05) !important;
}

/* عنوان بخش‌ها */
.section-title {
    font-size: 1.5rem;   /* ← فارسی بزرگ‌تر */
    font-weight: 700;
    color: #06b6d4;
    margin: 2rem 0 1rem 0;
    padding-right: 0.75rem;
    border-right: 3px solid #ec4899;
    text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
}

/* کارت آمار */
.stat-card {
    background: rgba(10, 10, 15, 0.8);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    border: 1px solid rgba(6, 182, 212, 0.25);
    box-shadow: inset 0 0 20px rgba(6, 182, 212, 0.05);
}
.stat-value {
    font-size: 2rem;   /* ← بزرگ‌تر */
    font-weight: 800;
    color: #06b6d4;
    text-shadow: 0 0 15px rgba(6, 182, 212, 0.7);
}
.stat-label-old {
    font-size: 0.95rem;   /* ← بزرگ‌تر */
    color: rgba(255, 255, 255, 0.55);
    margin-top: 0.25rem;
}

/* Usage info */
.usage-info {
    background: rgba(236, 72, 153, 0.08);
    border: 1px solid rgba(236, 72, 153, 0.35);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    font-size: 1.05rem;   /* ← بزرگ‌تر */
    color: #fbcfe8;
    text-align: center;
    margin-bottom: 1.5rem;
    text-shadow: 0 0 10px rgba(236, 72, 153, 0.4);
}

/* Pricing cards */
.pricing-card {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid rgba(6, 182, 212, 0.3);
    background: rgba(10, 10, 15, 0.8);
    box-shadow: inset 0 0 30px rgba(6, 182, 212, 0.05);
}
.pricing-card.pro {
    border-color: rgba(236, 72, 153, 0.5);
    background: rgba(236, 72, 153, 0.05);
    box-shadow: 0 0 30px rgba(236, 72, 153, 0.2), inset 0 0 30px rgba(236, 72, 153, 0.05);
}
.pricing-title { font-size: 1.3rem; font-weight: 700; color: #fff; }
.pricing-price { font-size: 2.2rem; font-weight: 800; color: #06b6d4; margin: 0.5rem 0; text-shadow: 0 0 15px rgba(6,182,212,0.5); }
.pricing-price.pro { color: #ec4899; text-shadow: 0 0 15px rgba(236,72,153,0.5); }
.pricing-features { text-align: right; font-size: 1rem; color: rgba(255,255,255,0.75); margin-top: 1rem; list-style: none; padding: 0; line-height: 1.9; }
.pricing-features li { margin: 0.5rem 0; }

/* Mobile */
@media (max-width: 600px) {
    .neon-hero h1 { font-size: 2.6rem; letter-spacing: -1px; }
    .neon-hero p { font-size: 1.15rem; }
    .neon-badge { font-size: 0.9rem; padding: 0.6rem 1.1rem; }
    .neon-line-top { margin-bottom: 1.5rem; }
    .section-title { font-size: 1.3rem; }
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Hero
# ============================================================
st.markdown("""
<div class="neon-hero">
    <div class="neon-line-top"></div>
    <h1>🎙️ VoiceSage</h1>
    <p>صدا را به متن تبدیل کن — دقیق، سریع، حرفه‌ای</p>
    <div class="neon-line-mid"></div>
    <div class="neon-badges">
        <span class="neon-badge">🎯 دقت بالا</span>
        <span class="neon-badge">🌐 فارسی + انگلیسی</span>
        <span class="neon-badge">🔄 ترجمه</span>
        <span class="neon-badge">📥 دانلود</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Session
# ============================================================
FREE_LIMIT = 3
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]
CF_BASE = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
MAX_FILE_MB = 25


def whisper_transcribe(audio_bytes, lang="fa", filename="audio.wav"):
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            files = {"file": (filename, audio_bytes)}
            data = {"model": "whisper-large-v3-turbo", "language": lang, "response_format": "verbose_json"}
            r = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            if r.status_code == 200:
                return r.json().get("text", "").strip(), "Groq (turbo)"
            return None, f"Groq error {r.status_code}"
        except requests.exceptions.Timeout:
            return None, "زمان درخواست به Groq به پایان رسید"
        except requests.exceptions.ConnectionError:
            return None, "اتصال به Groq برقرار نشد"
        except Exception as e:
            return None, f"Groq error: {e}"
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        url = f"{CF_BASE}/run/@cf/openai/whisper-large-v3-turbo"
        headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
        payload = {"audio": audio_b64, "language": lang, "task": "transcribe"}
        r = requests.post(url, headers=headers, json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("result", {}).get("text", "").strip(), "Cloudflare"
    except requests.exceptions.Timeout:
        return None, "زمان درخواست به Cloudflare به پایان رسید"
    except Exception as e:
        return None, f"Cloudflare error: {e}"


def llm_correct(raw_text, lang="fa"):
    url = f"{CF_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}

    if lang == "fa":
        system = """تو یه ویرایشگر حرفه‌ای متن فارسی هستی که متن پیاده‌شده از صوت رو اصلاح می‌کنی.

قوانین:
1. هیچ کلمه یا جمله‌ای رو حذف نکن
2. عددها رو تغییر نده
3. کلمات بی‌معنی یا غیرفارسی رو با نزدیک‌ترین کلمه‌ی منطقی جایگزین کن:
   - «عبداد» → «آب داد»
   - «کوبی» → «خوبی»
   - «حوش مصنعی» → «هوش مصنوعی»
   - «چه خواهد» → «چه خبر»
   - «اهمونی» → «مهمونی»
   - «پی ایس» → «پی اس»
4. فقط اگه کلمه‌ای کاملاً نامفهوم بود و جایگزین منطقی نداشت، همون رو نگه دار
5. نقطه‌گذاری و علائم سجاوندی اضافه کن
6. فقط متن اصلاح‌شده رو برگردون — بدون هیچ توضیح، پرانتز، یا عبارت اضافه
7. هرگز متن اصلی رو کنار جواب ننویس"""
    else:
        system = "Professional text editor. Fix obvious mishearings only. NEVER delete words or change numbers. Add punctuation. Return only corrected text."

    payload = {
        "model": "@cf/meta/llama-3.1-8b-instruct-fast",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"متن خام:\n{raw_text}"},
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def translate_text(text, source_lang):
    target_code = "en" if source_lang == "fa" else "fa"
    url = f"{CF_BASE}/run/@cf/meta/m2m100-1.2b"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    payload = {"text": text, "source_lang": source_lang, "target_lang": target_code}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("result", {}).get("translated_text", "").strip()


def summarize_text(text, lang="fa"):
    url = f"{CF_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    if lang == "fa":
        system = "تو یه خلاصه‌ساز حرفه‌ای فارسی هستی. متن رو در ۲-۳ جمله خلاصه کن. فقط خلاصه رو برگردون."
    else:
        system = "Professional summarizer. Summarize in 2-3 sentences. Return only the summary."
    payload = {
        "model": "@cf/meta/llama-3.1-8b-instruct-fast",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "max_tokens": 400, "temperature": 0.3,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def extract_keywords(text, lang="fa"):
    url = f"{CF_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    if lang == "fa":
        system = "تو یه استخراج‌کننده کلمات کلیدی هستی. ۵-۱۰ کلمه یا عبارت مهم از متن استخراج کن. با کاما جدا کن. فقط لیست رو برگردون."
    else:
        system = "Keyword extractor. Extract 5-10 important keywords/phrases. Comma-separated. Return only the list."
    payload = {
        "model": "@cf/meta/llama-3.1-8b-instruct-fast",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "max_tokens": 200, "temperature": 0.3,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def make_srt(text):
    lines = re.split(r'(?<=[.!?؟])\s+', text.strip())
    srt = ""
    for i, line in enumerate(lines, 1):
        if not line.strip(): continue
        start = timedelta(seconds=(i - 1) * 3)
        end = timedelta(seconds=i * 3)
        def fmt(t):
            s = str(t)
            if "." not in s: s += ".000"
            return s
        srt += f"{i}\n{fmt(start)} --> {fmt(end)}\n{line.strip()}\n\n"
    return srt


def make_vtt(text):
    lines = re.split(r'(?<=[.!?؟])\s+', text.strip())
    vtt = "WEBVTT\n\n"
    for i, line in enumerate(lines, 1):
        if not line.strip(): continue
        start = timedelta(seconds=(i - 1) * 3)
        end = timedelta(seconds=i * 3)
        def fmt(t):
            s = str(t)
            if "." not in s: s += ".000"
            return s.replace(".", ",")
        vtt += f"{fmt(start)} --> {fmt(end)}\n{line.strip()}\n\n"
    return vtt


def word_count(text):
    return len(text.split()) if text else 0


# ============================================================
# قیمت‌ها
# ============================================================
with st.expander("💎 پلن‌ها و قیمت‌ها", expanded=False):
    col_free, col_pro = st.columns(2)
    with col_free:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">🎁 رایگان</div>
            <div class="pricing-price">$۰</div>
            <ul class="pricing-features">
                <li>✅ ۳ فایل در روز</li>
                <li>✅ تا ۲۵ مگابایت</li>
                <li>✅ رونویسی + اصلاح</li>
                <li>✅ ترجمه + خلاصه</li>
                <li>✅ دانلود TXT + SRT + VTT</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_pro:
        st.markdown("""
        <div class="pricing-card pro">
            <div class="pricing-title">💎 حرفه‌ای</div>
            <div class="pricing-price pro">$۹ <span style="font-size:1rem;font-weight:400">/ ماه</span></div>
            <ul class="pricing-features">
                <li>✅ نامحدود</li>
                <li>✅ تا ۱۰۰ مگابایت</li>
                <li>✅ رونویسی + اصلاح</li>
                <li>✅ ترجمه + خلاصه</li>
                <li>✅ پشتیبانی اولویت‌دار</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.caption("⚠️ پرداخت پلن حرفه‌ای به‌زودی فعال می‌شود.")

# ============================================================
# About + FAQ
# ============================================================
with st.expander("ℹ️ درباره VoiceSage", expanded=False):
    st.markdown("""
**VoiceSage** ابزار هوش مصنوعی برای تبدیل صدا به متن است — فارسی و انگلیسی.

### 🎯 چرا VoiceSage؟
- 🎯 **دقت بالا** — مدل Whisper پیشرفته + اصلاح با AI
- 🌐 **دوزبانه** — فارسی و انگلیسی
- 🔄 **ترجمه** — با درک زمینه
- 📝 **خلاصه** — خودکار از متن
- 🏷️ **کلمات کلیدی** — استخراج خودکار
- 📥 **دانلود** — TXT، SRT، VTT

### 👨‍💻 سازنده
Javid Shahadati — RAG Specialist

### 🔗 لینک‌ها
- [LinkedIn](https://www.linkedin.com/in/javid-shahadati-a867a0447/)
- [GitHub](https://github.com/javidshahadati)
""")

with st.expander("❓ سوالات متداول (FAQ)", expanded=False):
    st.markdown("""
**چند فایل رایگان دارم؟**  
۳ فایل در روز. برای استفاده‌ی بیشتر، پلن حرفه‌ای ($۹/ماه) به‌زودی.

**چه فرمت‌هایی پشتیبانی می‌شه؟**  
MP3، WAV، M4A، OGG، WEBM، FLAC. حداکثر ۲۵ مگابایت.

**چقدر طول می‌کشه؟**  
فایل ۱ دقیقه‌ای: ~۱۵ ثانیه. فایل ۱۰ دقیقه‌ای: ~۲ دقیقه.

**آیا امن است؟**  
فایل‌ها فقط برای پردازش استفاده می‌شن، جایی ذخیره نمی‌شن.

**چطور پول بدم؟**  
پلن حرفه‌ای به‌زودی فعال می‌شود. فعلاً از پلن رایگان استفاده کنید.

**چه زبان‌هایی پشتیبانی می‌شه؟**  
فعلاً فارسی و انگلیسی. زبان‌های بیشتر به‌زودی.

**آیا می‌تونم متن رو ویرایش کنم؟**  
بله، بعد از تبدیل، متن نهایی در فیلد قابل ویرایش نمایش داده می‌شه.
""")

# ============================================================
# نمایش مصرف + دکمه ریست مخفی
# ============================================================
remaining = max(0, FREE_LIMIT - st.session_state.usage_count)
st.markdown(f'<div class="usage-info">🎁 استفاده‌ی رایگان امروز: <strong>{remaining} از {FREE_LIMIT}</strong> فایل باقی مانده</div>', unsafe_allow_html=True)

admin_mode = st.query_params.get("admin") == "MY_SECRET_2026"
if admin_mode and st.session_state.usage_count > 0:
    if st.button("🔄 ریست تست (ادمین)", key="reset_usage"):
        st.session_state.usage_count = 0
        st.rerun()

if st.session_state.usage_count >= FREE_LIMIT:
    st.error("🚫 **به محدودیت رایگان رسیدی!**\n\nپلن حرفه‌ای به‌زودی فعال می‌شود.")
    st.stop()

# ============================================================
# آپلود
# ============================================================
st.markdown('<div class="section-title">📤 آپلود فایل صوتی</div>', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    audio = st.file_uploader("فایل صوتی", type=["mp3", "wav", "m4a", "ogg", "webm", "flac"], label_visibility="collapsed")
with col2:
    lang_option = st.selectbox("زبان صدا:", ["fa", "en"], format_func=lambda x: "🇮🇷 فارسی" if x == "fa" else "🇬🇧 English")

if audio and audio.size > MAX_FILE_MB * 1024 * 1024:
    st.error(f"❌ حجم فایل بیشتر از {MAX_FILE_MB} مگابایت است.")
    st.stop()

if audio:
    st.audio(audio, format="audio/mpeg")
    st.caption(f"📁 {audio.name} — {audio.size / 1024:.1f} KB")
    if st.button("🎯 تبدیل به متن", use_container_width=True):
        with st.spinner("🎧 مرحله ۱: رونویسی..."):
            raw_text, provider = whisper_transcribe(audio.getvalue(), lang_option, audio.name)
            if raw_text is None:
                st.error(f"❌ خطا در رونویسی:\n\n{provider}\n\n💡 لطفاً دوباره تلاش کن یا فایل کوتاه‌تری آپلود کن.")
                st.stop()
            st.session_state.raw_text = raw_text
            st.session_state.provider = provider
        with st.spinner("✍️ مرحله ۲: اصلاح با LLM..."):
            try:
                corrected = llm_correct(raw_text, lang_option)
                st.session_state.corrected = corrected
                st.session_state.lang = lang_option
            except Exception as e:
                st.session_state.corrected = raw_text
                st.session_state.lang = lang_option
                st.session_state.llm_error = str(e)
        st.session_state.usage_count += 1
        st.rerun()

# ============================================================
# نمایش نتایج
# ============================================================
if "corrected" in st.session_state:
    corrected = st.session_state.corrected
    raw = st.session_state.get("raw_text", "")
    lang = st.session_state.get("lang", "fa")
    provider = st.session_state.get("provider", "")

    st.markdown(f'<div class="section-title">📊 آمار (منبع: {provider})</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{word_count(corrected)}</div><div class="stat-label-old">کلمه</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{len(corrected)}</div><div class="stat-label-old">کاراکتر</div></div>', unsafe_allow_html=True)
    with c3:
        flag = "🇮🇷" if lang == "fa" else "🇬🇧"
        lang_name = "فارسی" if lang == "fa" else "English"
        st.markdown(f'<div class="stat-card"><div class="stat-value">{flag}</div><div class="stat-label-old">{lang_name}</div></div>', unsafe_allow_html=True)

    if st.session_state.get("llm_error"):
        st.warning(f"⚠️ LLM اصلاح نشد: {st.session_state.llm_error}")

    st.markdown('<div class="section-title">✨ متن نهایی</div>', unsafe_allow_html=True)
    final_text = st.text_area("ویرایش:", corrected, height=200, label_visibility="collapsed")

    col_s, col_k = st.columns(2)
    with col_s:
        if st.button("📝 خلاصه کن", use_container_width=True):
            with st.spinner("در حال خلاصه‌سازی..."):
                try:
                    st.session_state.summary = summarize_text(final_text, lang)
                except Exception as e:
                    st.error(f"خطا: {e}")
    with col_k:
        if st.button("🏷️ کلمات کلیدی", use_container_width=True):
            with st.spinner("در حال استخراج..."):
                try:
                    st.session_state.keywords = extract_keywords(final_text, lang)
                except Exception as e:
                    st.error(f"خطا: {e}")

    if "summary" in st.session_state:
        st.info(f"**📝 خلاصه:** {st.session_state.summary}")
    if "keywords" in st.session_state:
        st.success(f"**🏷️ کلمات کلیدی:** {st.session_state.keywords}")

    with st.expander("📝 متن خام"):
        st.code(raw or "(خالی)", language=None)

    st.markdown('<div class="section-title">📥 دانلود</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("📄 TXT", data=final_text.encode("utf-8"), file_name=f"voicesage_{lang}.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("🎬 SRT", data=make_srt(final_text).encode("utf-8"), file_name=f"voicesage_{lang}.srt", mime="text/plain", use_container_width=True)
    with d3:
        st.download_button("🎞️ VTT", data=make_vtt(final_text).encode("utf-8"), file_name=f"voicesage_{lang}.vtt", mime="text/vtt", use_container_width=True)

    st.markdown('<div class="section-title">🌐 ترجمه</div>', unsafe_allow_html=True)
    target_name = "انگلیسی" if lang == "fa" else "فارسی"
    if st.button(f"🔄 ترجمه به {target_name}"):
        with st.spinner("در حال ترجمه..."):
            try:
                st.session_state.translated = translate_text(final_text, lang)
            except Exception as e:
                st.error(f"خطا: {e}")
    if "translated" in st.session_state:
        st.success(st.session_state.translated)
        st.download_button("📄 دانلود ترجمه", data=st.session_state.translated.encode("utf-8"), file_name=f"translation.txt", mime="text/plain")

    st.markdown("---")
    fb_key = "feedback_state"
    if st.session_state.get(fb_key) == "up":
        st.caption("🙏 ممنون — خوشحالم که کمک کرد")
    elif st.session_state.get(fb_key) == "down":
        st.caption("📝 ثبت شد — ممنون که کمک کردی بهتر بشم")
    else:
        fc1, fc2, fc3 = st.columns([3, 1, 1])
        with fc1:
            st.caption("این نتیجه چطور بود؟")
        with fc2:
            if st.button("👍", key="fb_up"):
                st.session_state[fb_key] = "up"
                st.rerun()
        with fc3:
            if st.button("👎", key="fb_down"):
                st.session_state[fb_key] = "down"
                st.rerun()
