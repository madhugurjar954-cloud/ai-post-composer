import streamlit as st
import os
import requests
import json
import random
from html import escape
import streamlit.components.v1 as components
import re
from collections import Counter
import io
import csv
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Minimal animated GIF generator (in-memory)
def make_demo_gif():
    frames = []
    width, height = 700, 300
    font = ImageFont.load_default()
    steps = [
        ("1 — Idea", "Type a short idea or keywords (e.g. 'CS50 project')"),
        ("2 — Template", "Pick a template pack and press Generate (Templates)") ,
        ("3 — Improve", "Use Micro-edits & Analyzer to polish the copy"),
        ("4 — Send / Export", "Copy, QR to phone, or download as PNG/CSV")
    ]
    for title, subtitle in steps:
        img = Image.new('RGB', (width, height), color=(245, 247, 250))
        d = ImageDraw.Draw(img)
        d.rectangle([(0,0),(width,60)], fill=(3,102,214))
        d.text((20,10), 'AI Post Composer', fill=(255,255,255), font=font)
        d.text((20,90), title, fill=(12,14,18), font=font)
        d.text((20,130), subtitle, fill=(60,64,67), font=font)
        frames.append(img)
    buf = io.BytesIO()
    frames[0].save(buf, format='GIF', save_all=True, append_images=frames[1:], duration=900, loop=0)
    buf.seek(0)
    return buf

# --- Page setup
st.set_page_config(page_title="AI Post Composer — Live Demo", layout="centered", page_icon="✨")

# small CSS
st.markdown(
    """
    <style>
    .muted { color: #64748b; }
    .card { background: white; padding:12px; border-radius:10px; box-shadow: 0 6px 20px rgba(2,6,23,0.04); }
    .small { font-size:13px; color:#94a3b8 }
    .cta { background: #0366d6; color: white; padding:10px 14px; border-radius:8px; text-decoration:none }
    .output-area { white-space: pre-wrap; font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial; }
    .preview { border:1px solid #e6eef8; padding:12px; border-radius:8px; background:#ffffff }
    .hashtag { color:#0366d6; font-weight:600 }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Hero with demo GIF
st.title("AI Post Composer — Live Demo ✨")
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("Write LinkedIn & X posts faster — templates, analyzer, batch export, and easy phone delivery.")
    st.markdown("\n• Turn an idea into a polished post in 60s\n• Curated template packs for Students, Makers, Job‑seekers\n• Batch export, QR to phone, and PNG download")
    st.markdown('---')
    # show demo gif
    gif_buf = make_demo_gif()
    st.image(gif_buf, caption='Demo: idea → template → polish → export', use_column_width=True)
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<strong>MVP</strong>')
    st.markdown('<div class="small muted">Instant demo — templates are free; Pro AI generation available if enabled.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar: Pro & settings
st.sidebar.header('Pro / Deployment')
license_key = st.sidebar.text_input('Pro license key (optional)')
api_base = st.sidebar.text_input('API base (deployed server URL)', value='')
st.sidebar.markdown('**Notes**')
st.sidebar.markdown('• Templates work without any key.\n• For AI generation, set OPENAI_API_KEY on the server or provide an API base.')

# --- Template packs & core templates
TEMPLATE_PACKS = {
    'General': {},
    'Students': {
        'linkedin': {'short': ["Finished my project on {context}. Key takeaway: {takeaway}."]}
    },
    'Makers': {
        'linkedin': {'promo': ["Built a small tool for {context} that helps with {benefit}."]}
    },
    'Job-seekers': {
        'linkedin': {'short': ["Looking for opportunities in {context}. I enjoy building {skill}."]}
    }
}
BASE_TEMPLATES = {
    'linkedin': {'short': ["Here’s what I learned from {context} — key takeaway: {takeaway}."]},
    'twitter': {'short': ["{context}: {takeaway} #100DaysOfCode"]}
}

# --- Form
with st.form('compose'):
    st.subheader('Compose a post — pick options and press Generate')
    mode = st.radio('Mode', ['Templates', 'AI'])
    platform = st.selectbox('Platform', ['linkedin','twitter'], format_func=lambda x: 'LinkedIn' if x=='linkedin' else 'X / Twitter')
    type_ = st.selectbox('Type', ['short','thread','promo','personal'])
    tone = st.selectbox('Tone', ['professional','friendly','casual','confident'])
    context = st.text_input('Keywords / context', value='e.g., CS50, project, interview tips')
    length = st.slider('Length', 1, 5, 3)
    pack_choice = st.selectbox('Template pack', list(TEMPLATE_PACKS.keys()))
    submitted = st.form_submit_button('Generate')

# helpers
import random, re
from collections import Counter

def sample(list_):
    return random.choice(list_)

def render_template(template, ctx):
    try:
        return template.format(**ctx)
    except Exception:
        text = template
        for k,v in ctx.items():
            text = text.replace('{' + k + '}', v)
        return text

def suggest_hashtags(text, context):
    stop = set(['the','and','for','with','that','this','from','your','you','are','was','have','has'])
    words = re.findall(r"\b\w{4,}\b", (text + ' ' + context).lower())
    candidates = [w for w in words if w not in stop]
    counts = Counter(candidates)
    tags = [w for w,_ in counts.most_common(6)]
    for t in ['100DaysOfCode','webdev','buildinpublic']:
        if t.lower() not in tags:
            tags.append(t)
    return ['#' + x for x in tags[:6]]

# session state
if 'last_output' not in st.session_state:
    st.session_state['last_output'] = ''

# Generate
if submitted:
    ctx = {'context': context, 'takeaway': 'focus on fundamentals', 'benefit':'save time', 'skill':'software', 'insight':'small progress compounds'}
    if mode == 'Templates':
        templates = TEMPLATE_PACKS.get(pack_choice, {})
        tpl = templates.get(platform, {}).get(type_, None)
        if tpl:
            t = sample(tpl)
        else:
            t = sample(BASE_TEMPLATES.get(platform, {}).get(type_, BASE_TEMPLATES[platform]['short']))
        out = render_template(t, ctx)
        if length >= 4:
            out += '\n\nTip: ' + ctx['insight']
        st.session_state['last_output'] = out
    else:
        # AI mode (calls API if available)
        used_api = api_base.rstrip('/') if api_base else None
        if used_api:
            try:
                resp = requests.post(used_api + '/api/generate', json={'platform':platform,'type':type_,'tone':tone,'context':context,'length':length,'license':license_key}, timeout=30)
                if resp.ok:
                    st.session_state['last_output'] = resp.json().get('text','')
                else:
                    st.session_state['last_output'] = 'AI error: please try later.'
            except Exception as e:
                st.session_state['last_output'] = 'AI request failed.'
        else:
            # Inform user how to enable
            st.session_state['last_output'] = 'AI disabled: add OPENAI_API_KEY to Streamlit secrets or provide API base.'

# Display output
if st.session_state['last_output']:
    st.markdown('---')
    st.header('Generated post')
    text = st.session_state['last_output']
    st.code(text)
    st.markdown('**Preview**')
    st.markdown(f'> {text}')
    hashtags = suggest_hashtags(text, context)
    st.markdown('**Suggested hashtags**: ' + ' '.join(hashtags))
    # QR and image download
    if st.button('Show QR to send to phone'):
        import qrcode
        buf = io.BytesIO()
        img = qrcode.make(text)
        img.save(buf, format='PNG')
        buf.seek(0)
        st.image(buf)
        st.download_button('Download QR PNG', data=buf, file_name='post-qr.png')
    if st.button('Download as PNG'):
        # render simple PNG
        font = ImageFont.load_default()
        wrapper = textwrap.TextWrapper(width=60)
        lines = wrapper.wrap(text)
        line_h = 14
        w,h = 800, 60 + line_h * len(lines)
        img = Image.new('RGB', (w,h), color=(255,255,255))
        d = ImageDraw.Draw(img)
        y = 20
        d.text((20,y), 'You — Preview', fill=(0,0,0), font=font)
        y += 30
        for line in lines:
            d.text((20,y), line, fill=(12,14,18), font=font)
            y += line_h
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        st.download_button('Download post image', data=buf, file_name='post.png')

# BEFORE / AFTER examples (new)
st.markdown('---')
st.header('Before → Template → Final (examples)')
examples = [
    {
        'idea':'Built a tiny project to practice CS problem solving',
        'template':"Finished my project on {context}. Key takeaway: {takeaway}.",
        'final':"Finished a small CS practice project that helps break down problems into manageable steps. Key lesson: focus on fundamentals and iterate. If you're studying CS, try tackling one small problem daily and build up."
    },
    {
        'idea':'Launching a study tool',
        'template':"Launching: {context} project — it helps with {benefit}.",
        'final':"Launching StudyBuddy — a lightweight tool to turn notes into practice questions. Early access open for students. DM to try it out."
    }
]
for ex in examples:
    st.markdown('**Idea:** ' + ex['idea'])
    st.markdown('**Template:** ' + ex['template'].format(context='CS50', takeaway='focus on fundamentals', benefit='memory retention'))
    st.markdown('**Final:** ' + ex['final'])
    st.markdown('---')

# FAQ (new)
st.header('FAQ — why pay instead of ChatGPT or Google?')
st.markdown('''
- ChatGPT is great for one-off text; AI Post Composer bundles curated templates, preview, hashtag suggestions, batch export, and phone delivery into a single workflow that saves time every week.
- We test templates for Students, Makers, and Job-seekers so results are tuned for your audience.
- Free demo is available — Pro features (AI generation, batch export, unlimited drafts) are optional for power users.
''')

# Waitlist
st.markdown('---')
st.header('Join the waitlist / get updates')
lead = st.text_input('Email for updates')
if st.button('Join waitlist (save email)'):
    if lead:
        st.session_state.setdefault('leads',[]).append(lead)
        st.success('Saved — thank you!')
if st.session_state.get('leads'):
    if st.button('Download leads CSV'):
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['email'])
        for e in st.session_state['leads']:
            w.writerow([e])
        buf.seek(0)
        st.download_button('Download CSV', data=buf.getvalue(), file_name='leads.csv')

# Footer: buy & next steps
st.markdown('---')
st.markdown('**Next steps I will do for you:** Replace Buy link with Gumroad URL, produce polished GIF/screenshots, tune AI prompts if you enable OpenAI key, and prepare Product Hunt pack.')
st.markdown('**Pricing suggestion:** $19 one-time for lifetime MVP; Pro monthly later.')

