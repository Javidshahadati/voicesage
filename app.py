import streamlit as st
import requests
import base64

st.set_page_config(page_title="VoiceSage — Test", page_icon="🎙️")
st.title("🎙️ VoiceSage — Whisper + LLM")

CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]


def whisper_transcribe(audio_bytes, lang="fa"):
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/openai/whisper-large-v3-turbo"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
    payload = {"audio": audio_b64, "language": lang, "task": "transcribe"}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("result", {}).get("text", "")


def llm_correct(raw_text, lang="fa"):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}

    if lang == "fa":
        system = """تو یه ویرایشگر حرفه‌ای متن فارسی هستی. متن خام از تبدیل صوت به دستت می‌رسه که ممکنه غلط املایی، غلط شنیداری، یا نقطه‌گذاری ناقص داشته باشه.

وظیفه‌ات:
1. غلط‌های شنیداری رو اصلاح کن (مثلاً اگه «عبداد» اومده و جمله درباره‌ی آب بود، «آب داد» کن)
2. غلط املایی و نقطه‌گذاری رو درست کن
3. کلمات رو به هم بچسبون و جمله‌ی روان بساز
4. معنی رو عوض نکن، فقط اصلاح کن
5. فقط متن اصلاح‌شده رو برگردون، بدون هیچ توضیح اضافه"""
    else:
        system = """You are a professional text editor. Fix spelling, grammar, and punctuation errors in the raw transcript. Don't change the meaning. Return only the corrected text."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"متن خام:\n{raw_text}\n\nمتن اصلاح‌شده:"},
    ]
    payload = {
        "model": "@cf/meta/llama-3.1-8b-instruct-fast",
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.2,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


st.info("دو مرحله: Whisper رونویسی می‌کنه، بعد LLM اصلاح می‌کنه.")

audio = st.file_uploader("فایل صوتی", type=["mp3", "wav", "m4a", "ogg"])
lang_option = st.selectbox(
    "زبان:", ["fa", "en"], format_func=lambda x: "فارسی" if x == "fa" else "English"
)

if audio and st.button("🎯 تبدیل + اصلاح"):
    with st.spinner("مرحله ۱: Whisper در حال رونویسی..."):
        try:
            raw_text = whisper_transcribe(audio.getvalue(), lang_option)
        except Exception as e:
            st.error(f"خطا در Whisper: {e}")
            st.stop()

    st.markdown("### 📝 متن خام (Whisper)")
    st.code(raw_text, language=None)

    with st.spinner("مرحله ۲: LLM در حال اصلاح..."):
        try:
            corrected = llm_correct(raw_text, lang_option)
        except Exception as e:
            st.error(f"خطا در اصلاح: {e}")
            st.stop()

    st.markdown("### ✨ متن اصلاح‌شده")
    st.success(corrected)

    st.text_area("ویرایش دستی (اگه لازم بود):", corrected, height=200, key="final_text")
