import streamlit as st
import requests
import base64

st.set_page_config(page_title="VoiceSage — Test", page_icon="🎙️")
st.title("🎙️ VoiceSage — تست Whisper")

CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]

st.info("این یه نسخه‌ی تستی برای چک کردن Whisper است. یه فایل صوتی کوتاه آپلود کن.")

audio = st.file_uploader("فایل صوتی (mp3, wav, m4a)", type=["mp3", "wav", "m4a", "ogg"])

# انتخاب زبان
lang_option = st.selectbox(
    "زبان فایل صوتی:",
    options=["fa", "en"],
    format_func=lambda x: "فارسی" if x == "fa" else "English",
)

if audio and st.button("🎯 تبدیل به متن"):
    with st.spinner("در حال تبدیل..."):
        # ۱. تبدیل فایل به Base64
        audio_bytes = audio.getvalue()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        # ۲. درخواست به Cloudflare
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/openai/whisper-large-v3-turbo"
        headers = {
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "audio": audio_b64,
            "language": lang_option,
            "task": "transcribe",
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                result = r.json().get("result", {})
                st.success("✅ تبدیل موفق!")
                st.text_area("متن:", result.get("text", ""), height=300)
                with st.expander("🔍 پاسخ کامل API"):
                    st.json(result)
            else:
                error_msg = r.text[:500]
                st.error(f"❌ خطا ({r.status_code}): {error_msg}")
        except Exception as e:
            st.error(f"❌ خطا: {e}")
