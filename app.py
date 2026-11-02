import streamlit as st
import requests

st.set_page_config(page_title="VoiceSage — Test", page_icon="🎙️")
st.title("🎙️ VoiceSage — تست Whisper")

CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]

st.info("این یه نسخه‌ی تستی برای چک کردن Whisper است. یه فایل صوتی کوتاه آپلود کن.")

audio = st.file_uploader("فایل صوتی (mp3, wav, m4a)", type=["mp3", "wav", "m4a", "ogg"])

if audio and st.button("🎯 تبدیل به متن"):
    with st.spinner("در حال تبدیل..."):
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/openai/whisper"
        headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
        files = {"audio": (audio.name, audio.getvalue(), audio.type or "audio/mpeg")}
        
        try:
            r = requests.post(url, headers=headers, files=files, timeout=120)
            if r.status_code == 200:
                result = r.json().get("result", {})
                st.success("✅ تبدیل موفق!")
                st.text_area("متن:", result.get("text", ""), height=300)
                with st.expander("🔍 پاسخ کامل API"):
                    st.json(result)
            else:
                st.error(f"❌ خطا ({r.status_code}): {r.text[:500]}")
        except Exception as e:
            st.error(f"❌ خطا: {e}")
