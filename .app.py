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

# --- ٢. بارکردنی داتاکان لە JSON ---
@st.cache_data
def load_all_data():
    try:
        with open('dialects.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        rules = data.get('rules', '')
        pronouns = json.dumps(data.get('pronouns', {}), ensure_ascii=False)
        dictionary = json.dumps(data.get('dictionary', []), ensure_ascii=False, indent=2)
        full_context = f"یاساکانی ڕێزمان:\n{rules}\n\nجێناوەکان:\n{pronouns}\n\nفەرهەنگی وشەکان:\n{dictionary}"
        return full_context
    except Exception as e:
        return "فەرهەنگەکە بەردەست نییە."

K_DATA = load_all_data()

# --- ٣. ڕێنماییە سیستەمییەکە ---
SYSTEM_PROMPT = f"""
تۆ پسپۆڕی زمانی کوردیت. 
یاسای بنەڕەتی: پێش هەموو شتێک سەیری ئەم داتایانەی خوارەوە بکە و پابەندی ڕێزمان و جێناوەکان بە:
{K_DATA}
١. ئەگەر وشەکە لە فەرهەنگەکەدا هەبوو، دەبێت بەتەواوی ئەو وەرگێڕانە بەکاربێنیت.
٢. سۆرانی، هەورامی بە پیتی ئارامی. Kurmancî و Zazakî بە لاتینی. لوڕی بە ڕێنوسی فارسی.
٣. تەنها وەڵامەکە بنووسە بێ هیچ دەقێکی زیادە.
.٤.لوڕی: دەبێت تەنها شێوەزاری 'لوڕی بەختیاری' بێت بە ڕێنووسی فارسی (قەدەغەیە وشەی فارسی بەکاربێت)..

"""

# --- ٤. دیزاینی CSS (چاککردنی گۆشە سپییەکان) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{ 
        background-color: #0E0A1A !important; 
        background-image: radial-gradient(circle at 50% 0%, #2A1B54 0%, transparent 50%);
    }}
    
    #MainMenu, header, footer, .stDeployButton {{visibility: hidden; display: none;}}
    .block-container {{ padding-top: 1rem !important; max-width: 450px !important; }}
    * {{ font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; color: #F8FDFE !important; }}
    
    /* چاککردنی گۆشە سپییەکانی خانەی نووسین */
    [data-testid="stForm"], [data-testid="stWidgetLabel"], .stTextArea, .stTextArea > div {{
        background-color: transparent !important;
    }}
    
    textarea {{ 
        background-color: rgba(30, 20, 60, 0.8) !important; 
        border-radius: 20px !important; 
        border: 1px solid rgba(107, 91, 226, 0.4) !important;
        color: white !important;
        padding: 15px !important;
    }}
    
    /* لابردنی سپیایی دەوری Selectbox و textarea */
    div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {{
        background-color: rgba(42, 27, 84, 0.5) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(107, 91, 226, 0.2) !important;
    }}

    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {{ 
        background-color: #1A1230 !important; 
        border: 1px solid rgba(107, 91, 226, 0.4) !important; 
        border-radius: 12px !important;
    }}
    
    li[data-baseweb="option"] {{ background-color: #1A1230 !important; color: white !important; }}
    li[data-baseweb="option"]:hover {{ background-color: #5A49D9 !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; background: rgba(255, 255, 255, 0.03); padding: 5px; border-radius: 15px; }}
    .stTabs [data-baseweb="tab"] {{ width: 100% !important; border: none !important; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ background: #5A49D9 !important; border-radius: 10px !important; }}
    
    .result-area {{ background: rgba(90, 73, 217, 0.15) !important; padding: 20px; border-radius: 20px; border: 1px solid rgba(107, 91, 226, 0.4) !important; text-align: center; font-size: 1.2rem; }}
    .stButton>button {{ background: linear-gradient(135deg, #6B5BE2 0%, #5A49D9 100%) !important; border-radius: 15px !important; border: none !important; height: 50px; width: 100%; }}
    .daily-banner {{ background: rgba(90, 73, 217, 0.2); padding: 8px; border-radius: 12px; text-align: center; margin-bottom: 15px; color: #B5AAFF !important; font-size: 0.8rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- ٥. لۆژیکی AI ---
@st.cache_data(show_spinner=False, ttl=3600)
def get_ai_response(text, src, trg, ttype):
    keys = [st.secrets.get(f"GEMINI_KEY_{i}") for i in range(1, 21) if st.secrets.get(f"GEMINI_KEY_{i}")]
    if not keys: return "تکایە کلیلەکان لە Secrets ڕێکبخە."
    genai.configure(api_key=random.choice(keys))
    model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=SYSTEM_PROMPT)
    prompts = {
        "translate": f"وەرگێڕە لە {src} بۆ {trg}: {text}",
        "abc": f"بگۆڕە (ئارامی ↔ لاتینی): {text}",
        "num": f"ژمارە بکە بە پیت بە شێوەزاری {trg}: {text}"
    }
    try:
        response = model.generate_content(prompts.get(ttype, text))
        return response.text
    except Exception:
        return "هەڵەیەک ڕوویدا، دووبارە هەوڵ بدەرەوە."

# --- ٦. UI ئەپەکە ---
st.markdown('<div class="daily-banner">✨ بەخێربێن بۆ یەکەمین وەرگێڕی شێوەزارە کوردییەکان</div>', unsafe_allow_html=True)
if logo: st.markdown(f'<div style="text-align:center; margin-bottom: 10px;"><img src="data:image/gif;base64,{logo}" width="65"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["وەرگێڕان", "ژمارە", "ڕێنووس"])
dlcts = ["سۆرانی", "Kurmancî", "هەورامی", "Zazakî", "لوڕی"]

with tab1:
    c1, c2 = st.columns(2)
    s_v, t_v = c1.selectbox("لە:", dlcts, key="s1"), c2.selectbox("بۆ:", dlcts, index=2, key="t1")
    u_in = st.text_area("", key="i1", placeholder="دەق لێرە بنووسە...", height=110)
    if st.button("وەرگێڕان ⚡", key="b1"):
        if u_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center; margin-top:20px;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = get_ai_response(u_in, s_v, t_v, "translate")
            res_box.markdown(f'<div class="result-area">{resp}</div>', unsafe_allow_html=True)

with tab2:
    n_v = st.selectbox("شێوەزار:", dlcts, key="s2")
    n_in = st.text_input("ژمارە:", key="i2", placeholder="نموونە: 125")
    if st.button("گۆڕین 🔢", key="b2"):
        if n_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = get_ai_response(n_in, "", n_v, "num")
            res_box.markdown(f'<div class="result-area">{resp}</div>', unsafe_allow_html=True)

with tab3:
    a_in = st.text_area("", key="i3", placeholder="دەقی ئارامی یان لاتینی لێرە دابنێ...", height=110)
    if st.button("گۆڕینی ڕێنووس ✨", key="b3"):
        if a_in:
            res_box = st.empty()
            if search_icon: res_box.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{search_icon}" width="80"></div>', unsafe_allow_html=True)
            resp = get_ai_response(a_in, "", "", "abc")
            res_box.markdown(f'<div class="result-area">{resp}</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.7rem; margin-top:25px;'>I_KURD|v1.3.1</p>", unsafe_allow_html=True)
