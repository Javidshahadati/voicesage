import streamlit as st
import requests

st.set_page_config(page_title="Groq Test", page_icon="🧪")
st.title("🧪 تست Groq API از Streamlit Cloud")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY توی Secrets نیست!")
    st.stop()

st.success(f"✅ کلید پیدا شد — شروع: `{GROQ_API_KEY[:10]}...` — طول: {len(GROQ_API_KEY)}")

# تست ۱: لیست مدل‌ها
st.subheader("تست ۱: اتصال به Groq")
try:
    r = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        timeout=15,
    )
    st.write(f"Status: `{r.status_code}`")
    if r.status_code == 200:
        models = [m["id"] for m in r.json().get("data", [])]
        st.success(f"✅ اتصال برقراره! {len(models)} مدل موجوده.")
        with st.expander("لیست مدل‌های Whisper"):
            for m in models:
                if "whisper" in m.lower():
                    st.write(f"- `{m}`")
    else:
        st.error(f"❌ Groq خطا داد: {r.status_code}")
        st.code(r.text[:1000])
except Exception as e:
    st.error(f"❌ خطای شبکه: {e}")

st.divider()

# تست ۲: رونویسی یه فایل
st.subheader("تست ۲: رونویسی")
audio = st.file_uploader("یه فایل صوتی کوتاه آپلود کن", type=["mp3", "wav", "m4a", "ogg"])

if audio and st.button("🎯 تست Groq"):
    try:
        files = {"file": (audio.name, audio.getvalue())}
        data = {"model": "whisper-large-v3", "language": "fa", "response_format": "verbose_json"}
        r = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files=files,
            data=data,
            timeout=120,
        )
        st.write(f"Status: `{r.status_code}`")
        if r.status_code == 200:
            result = r.json()
            st.success("✅ Groq جواب داد!")
            st.write(f"**مدت صدا:** {result.get('duration', 'نامعلوم')} ثانیه")
            st.text_area("متن:", result.get("text", ""), height=200)
            with st.expander("پاسخ کامل API"):
                st.json(result)
        else:
            st.error(f"❌ خطا: {r.status_code}")
            st.code(r.text[:1000])
    except Exception as e:
        st.error(f"❌ خطای شبکه: {e}")
