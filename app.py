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
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Vazirmatn', -apple-system, sans-serif !important; }
code, pre { font-family: 'Inter', monospace !important; }
.hero {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
    padding: 2.5rem 1.5rem; border-radius: 24px; color: white; text-align: center;
    margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(30, 64, 175, 0.3);
}
.hero h1 { font-size: 2.8rem; font-weight: 800; margin: 0; color: white !important; }
.hero p { font-size: 1.1rem; opacity: 0.95; margin-top: 0.75rem; }
.badges { display: flex; justify-content: center; gap: 0.5rem; margin-top: 1.25rem; flex-wrap: wrap; }
.badge { background: rgba(255,255,255,0.25); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.3); }
.stButton > button {
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
    color: white !important; border: none; border-radius: 12px;
    padding: 0.65rem 1.5rem; font-weight: 600; font-size: 1rem;
    transition: all 0.25s ease; box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(124, 58, 237, 0.35); }
div[data-testid="stFileUploader"] { border: 2px dashed #cbd5e1; border-radius: 16px; padding: 1rem; background: #f8fafc; }
.stTextArea textarea { border-radius: 12px; border: 1px solid #e2e8f0; font-family: 'Vazirmatn', sans-serif !important; font-size: 1rem; line-height: 1.8; }
.section-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 1.5rem 0 1rem 0; padding-right: 0.75rem; border-right: 4px solid #7c3aed; }
.stat-card { background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%); border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid #e2e8f0; }
.stat-value { font-size: 1.75rem; font-weight: 800; color: #1e40af; }
.stat-label { font-size: 0.8rem; color: #64748b; margin-top: 0.25rem; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

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

CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]
CF_BASE = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai"

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

MAX_FILE_MB = 25


def whisper_transcribe(audio_bytes, lang="fa", filename="audio.wav"):
    # اول Groq (turbo — کامل رونویسی می‌کنه)
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            files = {"file": (filename, audio_bytes)}
            data = {
                "model": "whisper-large-v3-turbo",
                "language": lang,
                "response_format": "verbose_json",
            }
            r = requests.post(url, headers=headers, files=files, data=data, timeout=120)
            if r.status_code == 200:
                result = r.json()
                return result.get("text", "").strip(), "Groq (turbo)"
            else:
                return None, f"Groq error {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return None, f"Groq network error: {e}"

    # fallback: Cloudflare
    try:
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        url = f"{CF_BASE}/run/@cf/openai/whisper-large-v3-turbo"
        headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
        payload = {"audio": audio_b64, "language": lang, "task": "transcribe"}
        r = requests.post(url, headers=headers, json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("result", {}).get("text", "").strip(), "Cloudflare"
    except Exception as e:
        return None, f"Cloudflare error: {e}"


def llm_correct(raw_text, lang="fa"):
    url = f"{CF_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}

    if lang == "fa":
        system = """تو یه ویرایشگر محافظه‌کار متن فارسی هستی.

قوانین سختگیرانه:
1. هیچ کلمه‌ای رو حذف نکن — هر چیزی که کاربر گفته باید بمونه
2. عددها رو تغییر نده
3. غلط‌های واضح شنیداری رو اصلاح کن:
   - «چه خواهد» → «چه خبر»
   - «حوش مصنعی» → «هوش مصنوعی»
   - «اهمونی» → «مهمونی»
   - «کوبی» → «خوبی»
   - «پی ایس» → «پی اس»
4. اگه شک داری، متن اصلی رو نگه دار
5. نقطه‌گذاری اضافه کن
6. فقط متن اصلاح‌شده رو برگردون، بدون توضیح"""
    else:
        system = "You are a conservative text editor. Fix obvious mishearings only. NEVER delete words or change numbers. Add punctuation. Return only corrected text."

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

        def fmt(t):
            s = str(t)
            if "." not in s:
                s += ".000"
            return s

        srt += f"{i}\n{fmt(start)} --> {fmt(end)}\n{line.strip()}\n\n"
    return srt


def word_count(text):
    return len(text.split()) if text else 0


st.markdown('<div class="section-title">📤 آپلود فایل صوتی</div>', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    audio = st.file_uploader(
        "فایل صوتی",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
        label_visibility="collapsed",
    )
with col2:
    lang_option = st.selectbox(
        "زبان صدا:",
        ["fa", "en"],
        format_func=lambda x: "🇮🇷 فارسی" if x == "fa" else "🇬🇧 English",
    )

if audio and audio.size > MAX_FILE_MB * 1024 * 1024:
    st.error(f"❌ حجم فایل بیشتر از {MAX_FILE_MB} مگابایت است.")
    st.stop()

if audio:
    st.audio(audio, format="audio/mpeg")
    st.caption(f"📁 {audio.name} — {audio.size / 1024:.1f} KB")

    if st.button("🎯 تبدیل به متن", use_container_width=True):
        with st.spinner("🎧 مرحله ۱: رونویسی..."):
            raw_text, provider = whisper_transcribe(
                audio.getvalue(), lang_option, audio.name
            )
            if raw_text is None:
                st.error(f"❌ خطا در رونویسی: {provider}")
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

        st.rerun()

if "corrected" in st.session_state:
    corrected = st.session_state.corrected
    raw = st.session_state.get("raw_text", "")
    lang = st.session_state.get("lang", "fa")
    provider = st.session_state.get("provider", "")

    st.markdown(
        f'<div class="section-title">📊 آمار (منبع: {provider})</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{word_count(corrected)}</div><div class="stat-label">کلمه</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{len(corrected)}</div><div class="stat-label">کاراکتر</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        flag = "🇮🇷" if lang == "fa" else "🇬🇧"
        lang_name = "فارسی" if lang == "fa" else "English"
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{flag}</div><div class="stat-label">{lang_name}</div></div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("llm_error"):
        st.warning(f"⚠️ LLM اصلاح نشد: {st.session_state.llm_error}")

    st.markdown('<div class="section-title">✨ متن نهایی</div>', unsafe_allow_html=True)
    final_text = st.text_area(
        "ویرایش دستی:", corrected, height=200, label_visibility="collapsed"
    )

    with st.expander("📝 متن خام (قبل از اصلاح)"):
        st.code(raw or "(خالی)", language=None)

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

    st.markdown('<div class="section-title">🌐 ترجمه</div>', unsafe_allow_html=True)
    target_name = "انگلیسی" if lang == "fa" else "فارسی"
    if st.button(f"🔄 ترجمه به {target_name}"):
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
            file_name=f"voicesage_{'en' if lang == 'fa' else 'fa'}_translated.txt",
            mime="text/plain",
        )
