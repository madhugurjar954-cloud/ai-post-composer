import streamlit as st
import os
import requests
import json
import random
from html import escape
import streamlit.components.v1 as components

# --- Page setup
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
    .output-area { white-space: pre-wrap; font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header / Hero
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
        st.markdown('<div style="text-align:center"><span class="pill">MVP</span><div class="small">Instant demo — no install</div></div>', unsafe_allow_html=True)

st.markdown('---')

# --- Sidebar: Pro & settings
st.sidebar.header('Pro / Deployment')
license_key = st.sidebar.text_input('Pro license key (optional)')
api_base = st.sidebar.text_input('API base (deployed server URL)', value='')
st.sidebar.markdown('**Notes**')
st.sidebar.markdown('• Templates work without any key.\n• For AI generation, set OPENAI_API_KEY on the server or provide an API base.')

# --- Form inputs
with st.form(key='compose'):
    st.subheader('Compose a post — pick options and press Generate')
    mode = st.radio('Mode', options=['Templates', 'AI'], index=0)
    platform = st.selectbox('Platform', options=['linkedin', 'twitter'], format_func=lambda x: 'LinkedIn' if x=='linkedin' else 'X / Twitter')
    type_ = st.selectbox('Type', options=['short', 'thread', 'promo', 'personal'], format_func=lambda x: x.title())
    tone = st.selectbox('Tone', options=['professional', 'friendly', 'casual', 'confident'], format_func=lambda x: x.title())
    context = st.text_input('Keywords / context', value='e.g., CS50, project, interview tips')
    length = st.slider('Length (verbosity)', min_value=1, max_value=5, value=3)
    submit = st.form_submit_button('Generate')

# --- Templates content
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

# --- Helpers

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

# Initialize session state for output
if 'last_output' not in st.session_state:
    st.session_state['last_output'] = ''

# Handle generate action
if submit:
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

    if mode == 'Templates':
        template = sample(TEMPLATES[platform][type_])
        text = render_template(template, ctx)
        if length >= 4:
            text += '\n\nExtra tip: ' + ctx['advice']
        st.session_state['last_output'] = text
    else:
        # AI mode: prefer calling api_base if provided, otherwise use server secret
        payload = {
            'platform': platform,
            'type': type_,
            'tone': tone,
            'context': context,
            'length': length,
            'license': license_key
        }
        used_api = api_base.rstrip('/') if api_base else None
        with st.spinner('Generating AI post — this may take a few seconds'):
            try:
                if used_api:
                    resp = requests.post(used_api + '/api/generate', json=payload, timeout=30)
                    if resp.ok:
                        data = resp.json()
                        st.session_state['last_output'] = data.get('text', '')
                    else:
                        # Friendly message, log raw error to console
                        st.session_state['last_output'] = 'AI generation failed. Please try again in a minute or contact support.'
                        print('API error', resp.status_code, resp.text)
                else:
                    OPENAI_KEY = st.secrets.get('OPENAI_API_KEY') if 'OPENAI_API_KEY' in st.secrets else os.environ.get('OPENAI_API_KEY')
                    if not OPENAI_KEY:
                        st.session_state['last_output'] = 'No AI key configured. Set OPENAI_API_KEY in Streamlit secrets or provide an API base.'
                    else:
                        headers = {'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'}
                        body = {
                            'model': 'gpt-3.5-turbo',
                            'messages': [
                                {'role': 'system', 'content': 'You generate concise social media posts based on the user instructions.'},
                                {'role': 'user', 'content': f"Platform: {platform} Type: {type_} Tone: {tone} Context: {context} Length: {length}."}
                            ],
                            'max_tokens': 350,
                            'temperature': 0.75
                        }
                        r = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=body, timeout=30)
                        if r.ok:
                            j = r.json()
                            content = j.get('choices', [{}])[0].get('message', {}).get('content', '')
                            st.session_state['last_output'] = content
                        else:
                            st.session_state['last_output'] = 'AI generation failed. Please try again in a minute or contact support.'
                            print('OpenAI error', r.status_code, r.text)
            except Exception as e:
                st.session_state['last_output'] = 'AI generation failed. Please try again in a minute or contact support.'
                print('Generation exception', str(e))

# --- Display output and example outputs
with st.container():
    left, right = st.columns([2,1])
    with left:
        if st.session_state['last_output']:
            # Show output in a styled card and provide a copy button via a small HTML component
            text_to_show = st.session_state['last_output']
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<strong>Generated post</strong>', unsafe_allow_html=True)
            st.markdown(f'<div class="output-area" id="gen">{escape(text_to_show)}</div>', unsafe_allow_html=True)
            # Copy button component
            copy_html = f"""
            <div style='margin-top:8px'>
              <button onclick="navigator.clipboard.writeText(document.getElementById('gen').innerText)" style='background:#0366d6;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer'>Copy to clipboard</button>
            </div>
            """
            components.html(copy_html, height=60)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card"><strong>Try it</strong><div class="small muted">Choose options and press Generate — templates work immediately.</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<strong>Example outputs</strong>', unsafe_allow_html=True)
        st.markdown('<div class="small muted">Real examples help convert users — show 2-3 good samples here.</div>', unsafe_allow_html=True)
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
