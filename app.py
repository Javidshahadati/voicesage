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
    font-family: 'Vazirmatn', -apple-system, sans-serif !important;
}
code, pre { font-family: 'Inter', monospace !important; }

/* ============ Hero ============ */
.hero {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
    padding: 3rem 1.5rem;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(30, 64, 175, 0.25);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
    animation: heroFloat 8s ease-in-out infinite;
    pointer-events: none;
}
@keyframes heroFloat {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, -30px); }
}
.hero h1 {
    font-size: 3rem;
    font-weight: 900;
    margin: 0;
    color: white !important;
    position: relative;
    z-index: 1;
    letter-spacing: -1px;
}
.hero .subtitle {
    font-size: 1.35rem;
    opacity: 0.95;
    margin-top: 1rem;
    position: relative;
    z-index: 1;
    font-weight: 400;
    line-height: 1.7;
}
.hero-badges {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}
.hero-badge {
    background: rgba(255, 255, 255, 0.22);
    padding: 0.5rem 1.2rem;
    border-radius: 24px;
    font-size: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.35);
    font-weight: 500;
    transition: all 0.3s;
}
.hero-badge:hover {
    background: rgba(255, 255, 255, 0.35);
    transform: translateY(-2px);
}

/* ============ Section titles ============ */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1e293b;
    margin: 1.75rem 0 1rem 0;
    padding-right: 0.75rem;
    border-right: 4px solid #7c3aed;
}

/* ============ Buttons ============ */
.stButton > button {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.25s !important;
    box-shadow: 0 4px 15px rgba(30, 64, 175, 0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.35) !important;
}

/* ============ Uploader ============ */
div[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1;
    border-radius: 14px;
    padding: 1rem;
    background: #f8fafc;
    transition: all 0.3s;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #7c3aed;
    background: #faf5ff;
}

/* ============ Textarea ============ */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.9 !important;
}

/* ============ Stats cards ============ */
.stat-card {
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
    border: 1px solid #e2e8f0;
    transition: all 0.3s;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.1);
    border-color: #c7d2fe;
}
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #1e40af, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.stat-label-old {
    font-size: 0.95rem;
    color: #64748b;
    margin-top: 0.35rem;
    font-weight: 500;
}

/* ============ Usage info ============ */
.usage-info {
    background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    font-size: 1.05rem;
    color: #3730a3;
    text-align: center;
    margin-bottom: 1.5rem;
    font-weight: 500;
}

/* ============ Pricing cards ============ */
.pricing-card {
    border-radius: 20px;
    padding: 1.75rem 1.5rem;
    text-align: center;
    border: 2px solid #e2e8f0;
    background: white;
    transition: all 0.3s;
    height: 100%;
}
.pricing-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
}
.pricing-card.pro {
    border-color: #7c3aed;
    background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.15);
}
.pricing-title { font-size: 1.3rem; font-weight: 700; color: #1e293b; }
.pricing-price { font-size: 2.4rem; font-weight: 800; color: #1e40af; margin: 0.75rem 0; }
.pricing-price.pro { color: #7c3aed; }
.pricing-features { text-align: right; font-size: 1rem; color: #475569; margin-top: 1rem; list-style: none; padding: 0; line-height: 2; }
.pricing-features li { margin: 0.4rem 0; }

/* ============ Expanders ============ */
div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: white !important;
    margin: 0.5rem 0 !important;
}
div[data-testid="stExpander"] summary {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #1e293b !important;
    padding: 0.85rem 1rem !important;
}
div[data-testid="stExpander"] summary:hover {
    color: #7c3aed !important;
}

/* ============ Mobile ============ */
@media (max-width: 600px) {
    .hero h1 { font-size: 2.2rem; }
    .hero .subtitle { font-size: 1.1rem; }
    .hero { padding: 2rem 1rem; }
    .section-title { font-size: 1.2rem; }
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Hero
# ============================================================
st.markdown("""
<div class="hero">
    <h1>🎙️ VoiceSage</h1>
    <p class="subtitle">صدا را به متن تبدیل کن — دقیق، سریع، حرفه‌ای</p>
    <div class="hero-badges">
        <span class="hero-badge">🎯 دقت بالا</span>
        <span class="hero-badge">🌐 فارسی + انگلیسی</span>
        <span class="hero-badge">🔄 ترجمه</span>
        <span class="hero-badge">📥 دانلود</span>
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
4. نقطه‌گذاری و علائم سجاوندی اضافه کن
5. فقط متن اصلاح‌شده رو برگردون — بدون هیچ توضیح اضافه"""
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
""")

# ============================================================
# شمارنده + دکمه ریست مخفی
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
