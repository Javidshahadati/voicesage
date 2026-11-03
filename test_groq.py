import streamlit as st
import requests

st.set_page_config(page_title="Groq Test", page_icon="🧪")
st.title("🧪 تست Groq API از Streamlit Cloud")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY توی Secrets نیست!")
    st.stop()

st.success(f"✅ کلید پیدا شد — شروع: `{GROQ_API_KEY[:10]}...` — طول: {len(GROQ_API_KEY)}")

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

st.subheader("تست ۲: رونویسی — مقایسه دو مدل")
audio = st.file_uploader("یه فایل صوتی آپلود کن", type=["mp3", "wav", "m4a", "ogg"])

if audio and st.button("🎯 تست هر دو مدل"):
    models_to_test = ["whisper-large-v3", "whisper-large-v3-turbo"]
    
    for model_name in models_to_test:
        st.markdown(f"### 🔹 مدل: `{model_name}`")
        try:
            files = {"file": (audio.name, audio.getvalue())}
            data = {"model": model_name, "language": "fa", "response_format": "verbose_json"}
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
                duration = result.get("duration", "نامعلوم")
                text = result.get("text", "")
                word_count = len(text.split())
                st.write(f"**مدت صدا:** {duration} ثانیه")
                st.write(f"**تعداد کلمات:** {word_count}")
                st.text_area(f"متن ({model_name}):", text, height=150, key=f"text_{model_name}")
            else:
                st.error(f"❌ خطا: {r.status_code}")
                st.code(r.text[:500])
        except Exception as e:
            st.error(f"❌ خطای شبکه: {e}")
        st.divider()
