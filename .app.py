import streamlit as st
import google.generativeai as genai
import base64
import random
import json

# --- ١. ڕێکخستنی سەرەکی ---
st.set_page_config(page_title="وەرگێڕی شێوەزارە کوردییەکان", page_icon="☀️", layout="centered")

def get_base_64(file):
    try:
        with open(file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

logo = get_base_64("logo.gif")
search_icon = get_base_64("search.gif")

# --- ٢. بارکردنی داتاکان ---
@st.cache_data
def load_all_data():
    try:
        with open('dialects.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return f"یاساکان:\n{data.get('rules', '')}\nجێناوەکان:\n{json.dumps(data.get('pronouns', {}), ensure_ascii=False)}\nفەرهەنگ:\n{json.dumps(data.get('dictionary', []), ensure_ascii=False)}"
    except: return ""

K_DATA = load_all_data()

# --- ٣. ڕێنماییە سیستەمییەکە ---
SYSTEM_PROMPT = f"تۆ پسپۆڕی زمانی کوردیت. پابەندی ئەم داتایانە بە:\n{K_DATA}\n١. تەنها وەڵام بنووسە. ٢. سۆرانی/هەورامی/لوڕی بە ئارامی، کورمانجی/زازاکی بە لاتینی."

# --- ٤. دیزاینی CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ background-color: #0E0A1A !important; background-image: radial-gradient(circle at 50% 0%, #2A1B54 0%, transparent 50%); }}
    #MainMenu, header, footer, .stDeployButton {{visibility: hidden; display: none;}}
    * {{ font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; color: #F8FDFE !important; }}
    
    /* چاککردنی گۆشە سپییەکان و دیزاینی خانەکان */
    textarea {{ background-color: rgba(30, 20, 60, 0.8) !important; border-radius: 20px !important; border: 1px solid rgba(107, 91, 226, 0.4) !important; padding: 15px !important; color: white !important; }}
    div[data-baseweb="select"] > div {{ background: rgba(42, 27, 84, 0.5) !important; border-radius: 15px !important; border: 1px solid rgba(107, 91, 226, 0.2) !important; }}
    
    /* ستایلی بەشی ئەنجام */
    .result-container {{ background: rgba(90, 73, 217, 0.15); padding: 20px; border-radius: 20px; border: 1px solid rgba(107, 91, 226, 0.4); margin-top: 20px; }}
    .ltr-text {{ direction: ltr !important; text-align: left !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; background: rgba(255, 255, 255, 0.03); padding: 5px; border-radius: 15px; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ background: #5A49D9 !important; border-radius: 10px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #6B5BE2 0%, #5A49D9 100%) !important; border-radius: 15px !important; height: 50px; width: 100%; border: none !important; }}
    .daily-banner {{ background: rgba(90, 73, 217, 0.2); padding: 8px; border-radius: 12px; text-align: center; margin-bottom: 15px; color: #B5AAFF !important; font-size: 0.8rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- ٥. لۆژیکی AI (بە سیستەمی فیلتەری کلیلەکان) ---
def get_ai_response(text, src, trg, ttype):
    all_keys = [st.secrets.get(f"GEMINI_KEY_{i}") for i in range(1, 21) if st.secrets.get(f"GEMINI_KEY_{i}")]
    random.shuffle(all_keys) # بۆ ئەوەی فشار تەنها لەسەر یەک کلیل نەبێت
    
    for api_key in all_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=SYSTEM_PROMPT)
            prompt = f"وەرگێڕە لە {src} بۆ {trg}: {text}" if ttype=="translate" else f"بگۆڕە: {text}"
            response = model.generate_content(prompt)
            return response.text
        except:
            continue # ئەگەر کلیلێک ئێرۆری دا، بچۆ سەر کلیلەکەی تر
    return "ببورە، هەموو کلیلەکان لە کار کەوتوون."

# --- ٦. UI ئەپەکە ---
st.markdown('<div class="daily-banner">✨ بەخێربێن بۆ یەکەمین وەرگێڕی شێوەزارە کوردییەکان</div>', unsafe_allow_html=True)
if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{logo}" width="65"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["وەرگێڕان", "ژمارە", "ڕێنووس"])
dlcts = ["سۆرانی", "Kurmancî", "هەورامی", "Zazakî", "لوڕی"]

with tab1:
    c1, c2 = st.columns(2)
    src, trg = c1.selectbox("لە:", dlcts, key="s1"), c2.selectbox("بۆ:", dlcts, index=2, key="t1")
    u_in = st.text_area("", key="i1", placeholder="دەق لێرە بنووسە...", height=110)
    
    if st.button("وەرگێڕان ⚡", key="b1"):
        if u_in:
            with st.spinner("وەرگێڕان دەکرێت..."):
                resp = get_ai_response(u_in, src, trg, "translate")
                # دیاریکردنی ئاڕاستەی نووسین (LTR بۆ لاتینی)
                is_ltr = "ltr-text" if trg in ["Kurmancî", "Zazakî"] else ""
                
                st.markdown(f'<div class="result-container {is_ltr}">{resp}</div>', unsafe_allow_html=True)
                st.code(resp) # ئەمە وەک دوگمەی کۆپی کار دەکات

with tab2:
    n_v = st.selectbox("شێوەزار:", dlcts, key="s2")
    n_in = st.text_input("ژمارە:", key="i2")
    if st.button("گۆڕین 🔢", key="b2"):
        if n_in:
            resp = get_ai_response(n_in, "", n_v, "num")
            st.markdown(f'<div class="result-container">{resp}</div>', unsafe_allow_html=True)
            st.code(resp)

with tab3:
    a_in = st.text_area("", key="i3", placeholder="دەق لێرە بنووسە...")
    if st.button("گۆڕین ✨", key="b3"):
        if a_in:
            resp = get_ai_response(a_in, "", "", "abc")
            st.markdown(f'<div class="result-container">{resp}</div>', unsafe_allow_html=True)
            st.code(resp)

st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.7rem; margin-top:25px;'>I_KURD|v1.3.1</p>", unsafe_allow_html=True)
