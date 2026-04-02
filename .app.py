import streamlit as st
import google.generativeai as genai
import base64
import random
import json

# --- ١. ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="I_KURD Translator", page_icon="☀️", layout="centered")

# --- ٢. بارکردنی داتا ---
@st.cache_data
def load_all_data():
    try:
        with open('dialects.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

K_DATA = load_all_data()

# --- ٣. پڕۆمتی تێکەڵ (زانیاری فەرهەنگ + زیرەکی دەستکرد) ---
# لێرەدا فەرمانمان پێکردووە کە تەنها فەرهەنگ نەبێت، بەڵکو وەک زمانزانێک بیر بکاتەوە
SYSTEM_PROMPT = f"""
تۆ زمانزانێکی کوردی زیرەکیت. ئەمە داتای بنەڕەتی تۆیە: {json.dumps(K_DATA, ensure_ascii=False)}

ئەرکی تۆ:
1. بەکارهێنانی "زیرەکی دەستکرد" بۆ تێگەیشتن لە مانا و سیاقی ڕستەکە.
2. ئەگەر وشەیەک لە فەرهەنگەکەدا هەبوو، وەک "سەرچاوەی سەرەکی" بەکاری بهێنە.
3. ئەگەر وشەکە نەبوو، یان ڕستەکە پێویستی بە داڕشتنی ڕێزمانی هەبوو، زیرەکی خۆت بەکاربهێنە بۆ ئەوەی وەرگێڕانەکە سروشتی و ڕەوان بێت.
4. شێواز: سۆرانی/هەورامی (ئارامی)، کورمانجی/زازاکی (لاتینی)، لوڕی (فارسی).
5. تەنها وەڵامەکە بنووسە.
"""

# --- ٤. ستایلی مۆدێرن و تاریک (بێ پەڵەی سپی) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0E0A1A !important;
        direction: rtl;
    }
    
    * { font-family: 'Vazirmatn', sans-serif !important; color: #F8FDFE !important; }

    /* خانەکانی ناوبردن و نووسین */
    textarea, input, div[data-baseweb="select"] > div {
        background-color: #1A1230 !important;
        border: 1px solid rgba(107, 91, 226, 0.3) !important;
        border-radius: 12px !important;
    }

    /* لیستە شۆڕبووەوەکان */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #1A1230 !important;
        border: 1px solid #6B5BE2 !important;
    }
    
    li[data-baseweb="option"] { background-color: #1A1230 !important; }
    li[data-baseweb="option"]:hover { background-color: #5A49D9 !important; }

    /* بەشی نیشاندانی ئەنجام و کۆپی */
    [data-testid="stCodeBlock"], .result-box {
        background-color: #140E26 !important;
        border: 1px solid #6B5BE2 !important;
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] { background: rgba(255, 255, 255, 0.05); border-radius: 15px; }
    button[data-baseweb="tab"][aria-selected="true"] { background: #5A49D9 !important; border-radius: 10px !important; }
    
    .stButton>button {
        background: linear-gradient(135deg, #6B5BE2 0%, #5A49D9 100%) !important;
        border: none !important;
        border-radius: 12px;
        height: 45px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); opacity: 0.9; }
    
    .ltr-res { direction: ltr !important; text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ٥. لۆژیکی وەرگێڕان ---
def translate_logic(text, src, trg):
    keys = [st.secrets.get(f"GEMINI_KEY_{i}") for i in range(1, 21) if st.secrets.get(f"GEMINI_KEY_{i}")]
    if not keys: return "API Key نەدۆزرایەوە."
    
    random.shuffle(keys)
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(f"وەرگێڕە لە {src} بۆ {trg}: {text}")
            return response.text
        except: continue
    return "هەڵەیەک ڕوویدا، تکایە دووبارە هەوڵ بدەرەوە."

# --- ٦. ڕووکاری بەکارهێنەر ---
st.markdown('<h3 style="text-align:center; color:#B5AAFF;">I_KURD AI Translator</h3>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["وەرگێڕان", "ژمارە", "ڕێنووس"])
dlcts = ["سۆرانی", "Kurmancî", "هەورامی", "Zazakî", "لوڕی"]

with tab1:
    col1, col2 = st.columns(2)
    s_lang = col1.selectbox("لە:", dlcts, key="src1")
    t_lang = col2.selectbox("بۆ:", dlcts, index=2, key="trg1")
    
    u_input = st.text_area("", placeholder="چی لە مێشکدایە؟ بنووسە...", height=120)
    
    if st.button("وەرگێڕانی زیرەک ⚡"):
        if u_input:
            with st.spinner("AI خەریکی بیرکردنەوەیە..."):
                result = translate_logic(u_input, s_lang, t_lang)
                is_ltr = "ltr-res" if t_lang in ["Kurmancî", "Zazakî"] else ""
                
                st.markdown(f'<div class="result-box {is_ltr}">{result}</div>', unsafe_allow_html=True)
                st.code(result) # بۆ کۆپی کردن

# بەشەکانی تریش بە هەمان شێواز کار دەکەن
