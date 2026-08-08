import streamlit as st
import os
import requests
import json
import random

st.set_page_config(page_title="AI Post Composer — Live Demo", layout="centered", page_icon="✨")

# Simple CSS to make the app look nicer
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#f8fafc 0%, #ffffff 100%); }
    .hero { padding: 18px; border-radius: 12px; background: linear-gradient(90deg,#ffffff,#f1f5f9); box-shadow: 0 6px 18px rgba(11,20,34,0.06); }
    .muted { color: #64748b; }
    .card { background: white; padding:12px; border-radius:10px; box-shadow: 0 6px 20px rgba(2,6,23,0.04); }
    .small { font-size:13px; color:#94a3b8 }
    .cta { background: #0366d6; color: white; padding:10px 14px; border-radius:8px; text-decoration:none }
    .pill { background:#eef2ff; color:#0366d6; padding:6px 10px; border-radius:999px; font-weight:600 }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header / Hero
with st.container():
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("""
        <h1 style='margin:0'>AI Post Composer — Live Demo ✨</h1>
        <p class='muted' style='margin-top:6px'>Write LinkedIn & X posts faster — templates, tones, and optional AI generation.</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        # show a small badge
        st.markdown('<div style="text-align:center"><span class="pill">MVP</span><div class="small">Instant demo — no install</div></div>', unsafe_allow_html=True)

st.markdown('---')

# Controls area
with st.container():
    st.subheader('Compose a post — try templates or AI')
    platform = st.selectbox('Platform', options=['linkedin', 'twitter'], format_func=lambda x: 'LinkedIn' if x=='linkedin' else 'X / Twitter')
    type_ = st.selectbox('Type', options=['short', 'thread', 'promo', 'personal'], format_func=lambda x: x.title())
    tone = st.selectbox('Tone', options=['professional', 'friendly', 'casual', 'confident'], format_func=lambda x: x.title())
    context = st.text_input('Keywords / context', value='e.g., CS50, project, interview tips')
    length = st.slider('Length (verbosity)', min_value=1, max_value=5, value=3)

    colA, colB = st.columns([1,1])
    with colA:
        gen_templates = st.button('Generate (Templates)')
    with colB:
        gen_ai = st.button('Generate (AI)')

    st.markdown('')

# Sidebar: Pro & settings
st.sidebar.header('Pro / Deployment')
license_key = st.sidebar.text_input('Pro license key (optional)')
api_base = st.sidebar.text_input('API base (deployed server URL)', value='')
st.sidebar.markdown('**Notes**')
st.sidebar.markdown('• Templates work without any key.\n• For AI generation, set OPENAI_API_KEY on the server or provide an API base.')

# Templates content
TEMPLATES = {
    'linkedin': {
        'short': [
            "Here’s what I learned from {context} — key takeaway: {takeaway}. If you're learning CS, try this.",
            "Finished a small project on {context}. Main lesson: {takeaway}. Happy to share the repo if you want."
        ],
        'thread': [
            "Thread: lessons from {context}\n\n1) {point1}\n2) {point2}\n3) {point3}\n\nIf you're starting with CS, focus on {advice}.",
            "I built something for {context} — the surprising part was {surprise}. Here’s how I solved it: {steps}."
        ],
        'promo': [
            "Launching: {context} project — it helps with {benefit}. DM me for early access.",
            "I've opened early access to my {context} tool. Sign up to try it and get feedback."
        ],
        'personal': [
            "Today I realized that {insight} while working on {context}. That changed my approach to {practice}.",
            "I used to struggle with {problem}. After working on {context}, I now {result}."
        ]
    },
    'twitter': {
        'short': [
            "{context}: {takeaway} #100DaysOfCode",
            "Built a thing for {context}. Key lesson: {takeaway}"
        ],
        'thread': [
            "1/ Thread: {context}\n2/ {point1}\n3/ {point2}\n4/ {point3}\n5/ TL; DR: {advice}",
            "1/ I tried {context} and here are the steps that worked: {steps}\n2/ {result}"
        ],
        'promo': [
            "Launching {context} — helps with {benefit}. More info: [link]",
            "Early access open for {context}. DM me!"
        ],
        'personal': [
            "Working on {context} made me realize {insight}. #devlife",
            "Small wins: {context} -> {result}."
        ]
    }
}

# Small helper functions

def sample(list_):
    return random.choice(list_)


def render_template(template, ctx):
    try:
        return template.format(**ctx)
    except Exception:
        text = template
        for k, v in ctx.items():
            text = text.replace('{' + k + '}', v)
        return text

# Output area with examples and live preview
with st.container():
    left, right = st.columns([2,1])
    with left:
        out_place = st.empty()
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<strong>Example outputs</strong>', unsafe_allow_html=True)
        st.markdown('<div class="small muted">Real examples help convert users — show 2-3 good samples here.</div>', unsafe_allow_html=True)
        # Two curated examples
        st.markdown('''
        <div style='margin-top:8px'>
        <div style='padding:8px;border-radius:8px;background:#f8fafc'><strong>Personal (LinkedIn)</strong><br>
        Today I realized that small, consistent projects compound into big wins. Working on my CS50 project helped me focus on fundamentals and ship something useful.
        </div>
        <div style='padding:8px;border-radius:8px;background:#fff7ed;margin-top:8px'><strong>Promo (X)</strong><br>
        Launching ProjectX — helps students practice interviews with bite-sized challenges. Early access open — DM to join.
        </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Handle button interactions
if gen_templates:
    ctx = {
        'context': context,
        'takeaway': 'focus on fundamentals',
        'point1': 'practice daily',
        'point2': 'build projects',
        'point3': 'read docs',
        'advice': 'start small and iterate',
        'surprise': 'it was easier than expected',
        'steps': '1) plan 2) implement 3) test',
        'insight': 'small progress compounds',
        'result': 'I can explain it clearly',
        'practice': 'building small projects',
        'problem': 'getting stuck on docs',
        'benefit': 'save time'
    }
    template = sample(TEMPLATES[platform][type_])
    text = render_template(template, ctx)
    if length >= 4:
        text += '\n\nExtra tip: ' + ctx['advice']
    out_place.text_area('Generated (Templates)', value=text, height=260)

if gen_ai:
    # Prefer the provided API base (serverless) if user set it; otherwise try streamlit secret
    st.info('Sending request to AI... this uses your OPENAI API key on the server.')
    payload = {
        'platform': platform,
        'type': type_,
        'tone': tone,
        'context': context,
        'length': length,
        'license': license_key
    }

    used_api = None
    if api_base:
        used_api = api_base.rstrip('/')
    else:
        # If deployed on Streamlit, use its server-side key
        used_api = None

    with st.spinner('Generating...'):
        if used_api:
            try:
                resp = requests.post(used_api + '/api/generate', json=payload, timeout=30)
                if resp.ok:
                    data = resp.json()
                    text = data.get('text') or json.dumps(data)
                    out_place.text_area('Generated (AI)', value=text, height=260)
                else:
                    out_place.text_area('Error from API', value=resp.text, height=200)
            except Exception as e:
                st.error('API request failed: ' + str(e))
        else:
            # Call OpenAI directly from this Streamlit server if secrets are set
            OPENAI_KEY = None
            if 'OPENAI_API_KEY' in st.secrets:
                OPENAI_KEY = st.secrets['OPENAI_API_KEY']
            else:
                OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

            if not OPENAI_KEY:
                st.error('No OpenAI API key found. Add OPENAI_API_KEY to Streamlit secrets or set the API base to your deployed server.')
            else:
                prompt = f"You are a helpful assistant that writes social media posts. Platform: {platform} Type: {type_} Tone: {tone} Context: {context} Length: {length}. Produce one polished output appropriate for the platform."
                try:
                    headers = {'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'}
                    body = {
                        'model': 'gpt-3.5-turbo',
                        'messages': [
                            {'role': 'system', 'content': 'You generate concise social media posts based on the user instructions.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'max_tokens': 350,
                        'temperature': 0.75
                    }
                    r = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=body, timeout=30)
                    if r.ok:
                        j = r.json()
                        content = j.get('choices', [{}])[0].get('message', {}).get('content', '')
                        out_place.text_area('Generated (AI)', value=content, height=260)
                    else:
                        out_place.text_area('OpenAI error', value=r.text, height=200)
                except Exception as e:
                    st.error('OpenAI call failed: ' + str(e))

# Footer and CTA
st.markdown('---')
colL, colR = st.columns([3,1])
with colL:
    st.markdown('**Ready to try?** Use the live demo, or get the lifetime MVP on Gumroad (install instructions included).')
with colR:
    st.markdown('<a class="cta" href="REPLACE_WITH_GUMROAD_LINK" target="_blank">Buy — $19</a>', unsafe_allow_html=True)

st.sidebar.markdown('---')
st.sidebar.write('Want this as a Chrome extension? The extension calls the same AI backend and offers a popup UI.')
st.sidebar.markdown('**Support:** https://github.com/madhugurjar954-cloud/ai-post-composer/issues')

