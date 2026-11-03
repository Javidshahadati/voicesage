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

# ============================================================
# CSS حرفه‌ای
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Vazirmatn', -apple-system, sans-serif !important;
}
code, pre { font-family: 'Inter', monospace !important; }

.hero {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
    padding: 2.5rem 1.5rem;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(30, 64, 175, 0.3);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    color: white !important;
    position: relative;
    z-index: 1;
}
.hero p {
    font-size: 1.1rem;
    opacity: 0.95;
    margin-top: 0.75rem;
    position: relative;
    z-index: 1;
}
.badges {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1.25rem;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}
.badge {
    background: rgba(255,255,255,0.25);
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
}

.stButton > button {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.5rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.35);
}

div[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 1rem;
    background: #f8fafc;
}

.stChatMessage {
    border-radius: 16px;
    padding: 1.25rem;
    border: 1px solid #e2e8f0;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stTextArea textarea {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 1rem;
    line-height: 1.8;
}

div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1e293b;
    margin: 1.5rem 0 1rem 0;
    padding-right: 0.75rem;
    border-right: 4px solid #7c3aed;
}

.stat-card {
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    border: 1px solid #e2e8f0;
}
.stat-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1e40af;
}
.stat-label {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.25rem;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-weight: 600;
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
    <p>صدا را به متن تبدیل کن — دقیق، سریع، حرفه‌ای</p>
    <div class="badges">
        <span class="badge">🎯 دقت بالا</span>
        <span class="badge">🌐 فارسی + انگلیسی</span>
        <span class="badge">🔄 ترجمه</span>
        <span class="badge">📥 دانلود</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Secrets
# ============================================================
CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]
CF_BASE = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai"

MAX_FILE_MB = 25

# ============================================================
# توابع
# ============================================================
def whisper_transcribe(audio_bytes, lang="fa"):
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    url = f"{CF_BASE}/run/@cf/openai/whisper-large-v3-turbo"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    payload = {"audio": audio_b64, "language": lang, "task": "transcribe"}
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("result", {}).get("text", "").strip()


def llm_correct(raw_text, lang="fa"):
    url = f"{CF_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}

        if lang == "fa":
        system = """تو یه ویرایشگر محافظه‌کار متن فارسی هستی.

قوانین سختگیرانه:
1. هیچ کلمه‌ای رو حذف نکن — هر چیزی که کاربر گفته باید بمونه (مخصوصاً اعداد، «بابا»، «خوبی»، «چه خبر»، ...)
2. عددها رو تغییر نده — «سه چهارتا» رو «۳ تا» نکن، همون رو نگه دار
3. فقط غلط‌های واضح شنیداری رو اصلاح کن (مثلاً «کوبی» → «خوبی»، «چه خواهد» → «چه خبر»)
4. اگه شک داری، متن اصلی رو نگه دار
5. نقطه‌گذاری و علائم سجاوندی اضافه کن
6. فقط متن اصلاح‌شده رو برگردون، بدون توضیح

مثال درست:
ورودی: «سلام کوبی چه خواهد چه کار می‌کنی با دیشب رفتم مهمونی»
خروجی: «سلام، خوبی؟ چه خبر؟ چه کار می‌کنی؟ بابا، دیشب رفتم مهمونی.»

مثال غلط (حذف کردن):
خروجی: «سلام، دیشب رفتم مهمونی.» ← این غلطه چون «بابا» و «خوبی» حذف شدن."""
    else:
        system = "You are a conservative text editor. NEVER delete words or change numbers. Only fix obvious mishearings. Add punctuation. Return only corrected text."
    payload = {
        "model": "@cf/meta/llama-3.1-8b-instruct-fast",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"متن خام:\n{raw_text}"},
        ],
        "max_tokens": 800,
        "temperature": 0.2,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def translate_text(text, source_lang):
    target = "en" if source_lang == "fa" else "fa"
    url = f"{CF_BASE}/run/@cf/meta/m2m100-1.2b"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    payload = {"text": text, "source_lang": source_lang, "target_lang": target}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("result", {}).get("translated_text", "").strip()


def make_srt(text):
    lines = re.split(r'(?<=[.!?؟])\s+', text.strip())
    srt = ""
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        start = timedelta(seconds=(i - 1) * 3)
        end = timedelta(seconds=i * 3)
        fmt = lambda t: str(t).zfill(8) if "." in str(t) else str(t) + ".000"
        srt += f"{i}\n{fmt(start)} --> {fmt(end)}\n{line.strip()}\n\n"
    return srt


def word_count(text):
    return len(text.split()) if text else 0


# ============================================================
# UI اصلی
# ============================================================
st.markdown('<div class="section-title">📤 آپلود فایل صوتی</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    audio = st.file_uploader(
        "فایل صوتی (mp3, wav, m4a, ogg)",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
        label_visibility="collapsed",
    )
with col2:
    lang_option = st.selectbox(
        "زبان صدا:",
        ["fa", "en"],
        format_func=lambda x: "🇮🇷 فارسی" if x == "fa" else "🇬🇧 English",
    )

# محدودیت حجم
if audio and audio.size > MAX_FILE_MB * 1024 * 1024:
    st.error(f"❌ حجم فایل بیشتر از {MAX_FILE_MB} مگابایت است.")
    st.stop()

if audio:
    st.audio(audio, format="audio/mpeg")
    st.caption(f"📁 {audio.name} — {audio.size / 1024:.1f} KB")

    if st.button("🎯 تبدیل به متن", use_container_width=True):
        with st.spinner("🎧 مرحله ۱: Whisper در حال رونویسی..."):
            try:
                raw_text = whisper_transcribe(audio.getvalue(), lang_option)
                st.session_state.raw_text = raw_text
            except Exception as e:
                st.error(f"خطا در Whisper: {e}")
                st.stop()

        with st.spinner("✍️ مرحله ۲: LLM در حال اصلاح..."):
            try:
                corrected = llm_correct(raw_text, lang_option)
                st.session_state.corrected = corrected
                st.session_state.lang = lang_option
            except Exception as e:
                st.error(f"خطا در اصلاح: {e}")
                st.session_state.corrected = raw_text
                st.session_state.lang = lang_option

        st.rerun()

# ============================================================
# نمایش نتایج
# ============================================================
if "corrected" in st.session_state:
    corrected = st.session_state.corrected
    raw = st.session_state.get("raw_text", "")
    lang = st.session_state.get("lang", "fa")

    st.markdown('<div class="section-title">📊 آمار</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{word_count(corrected)}</div><div class="stat-label">کلمه</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{len(corrected)}</div><div class="stat-label">کاراکتر</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{"🇮🇷" if lang=="fa" else "🇬🇧"}</div><div class="stat-label">{ "فارسی" if lang=="fa" else "English"}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">✨ متن نهایی</div>', unsafe_allow_html=True)
    final_text = st.text_area("ویرایش دستی:", corrected, height=200, label_visibility="collapsed")

    with st.expander("📝 متن خام Whisper (قبل از اصلاح)"):
        st.code(raw or "(خالی)", language=None)

    # دانلود
    st.markdown('<div class="section-title">📥 دانلود</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "📄 دانلود TXT",
            data=final_text.encode("utf-8"),
            file_name=f"voicesage_{lang}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "🎬 دانلود SRT",
            data=make_srt(final_text).encode("utf-8"),
            file_name=f"voicesage_{lang}.srt",
            mime="text/plain",
            use_container_width=True,
        )

    # ترجمه
    st.markdown('<div class="section-title">🌐 ترجمه</div>', unsafe_allow_html=True)
    if st.button("🔄 ترجمه به " + ("انگلیسی" if lang == "fa" else "فارسی")):
        with st.spinner("در حال ترجمه..."):
            try:
                translated = translate_text(final_text, lang)
                st.session_state.translated = translated
            except Exception as e:
                st.error(f"خطا در ترجمه: {e}")

    if "translated" in st.session_state:
        st.success(st.session_state.translated)
        st.download_button(
            "📄 دانلود ترجمه",
            data=st.session_state.translated.encode("utf-8"),
            file_name=f"voicesage_{'en' if lang=='fa' else 'fa'}_translated.txt",
            mime="text/plain",
        )
