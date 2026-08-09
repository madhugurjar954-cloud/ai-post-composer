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
import qrcode
import base64
from PIL import Image, ImageDraw, ImageFont
import textwrap

# --- Page setup
st.set_page_config(page_title="AI Post Composer — Live Demo", layout="centered", page_icon="✨")

# --- Sidebar: Theme & Pro settings
st.sidebar.header('Appearance & Pro')
accent = st.sidebar.color_picker('Accent color', '#0366d6')
dark_mode = st.sidebar.checkbox('Dark mode (preview)', value=False)
license_key = st.sidebar.text_input('Pro license key (optional)')
api_base = st.sidebar.text_input('API base (deployed server URL)', value='')
st.sidebar.markdown('**Notes**')
st.sidebar.markdown('• Templates work without any key.\n• For AI generation, set OPENAI_API_KEY on the server or provide an API base.')

# Inject CSS with chosen accent and optional dark mode
bg_gradient = "linear-gradient(180deg,#0f172a 0%, #0b1220 100%)" if dark_mode else "linear-gradient(180deg,#f8fafc 0%, #ffffff 100%)"
text_color = "#e6eef8" if dark_mode else "#042a3b"
muted_color = "#9ca3b3" if dark_mode else "#64748b"
card_bg = "#0b1220" if dark_mode else "#ffffff"

st.markdown(f"""
<style>
.stApp {{ background: {bg_gradient}; color: {text_color}; }}
.hero {{ padding: 18px; border-radius: 12px; background: linear-gradient(90deg,#ffffff,#f1f5f9); box-shadow: 0 6px 18px rgba(11,20,34,0.06); }}
.muted {{ color: {muted_color}; }}
.card {{ background: {card_bg}; padding:12px; border-radius:10px; box-shadow: 0 6px 20px rgba(2,6,23,0.04); }}
.small {{ font-size:13px; color:{muted_color} }}
.cta {{ background: {accent}; color: white; padding:10px 14px; border-radius:8px; text-decoration:none }}
.pill {{ background:#eef2ff; color:{accent}; padding:6px 10px; border-radius:999px; font-weight:600 }}
.output-area {{ white-space: pre-wrap; font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial; color: {text_color}; }}
.preview {{ border:1px solid #e6eef8; padding:12px; border-radius:8px; background:{card_bg} }}
.hashtag {{ color:{accent}; font-weight:600 }}
</style>
""", unsafe_allow_html=True)

# --- Header / Hero
with st.container():
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("""
        <h1 style='margin:0'>AI Post Composer — Live Demo ✨</h1>
        <p class='muted' style='margin-top:6px'>Write LinkedIn & X posts faster — curated templates, hashtag suggestions, drafts, intelligent analyzer, and optional AI generation.</p>
        <ul style='margin-top:6px'>
          <li style='margin-bottom:4px'>Turn a raw idea into a polished post in seconds (templates + AI)</li>
          <li style='margin-bottom:4px'>Batch variations and CSV export for scheduling</li>
          <li style='margin-bottom:4px'>Send posts to your phone via QR or download as an image</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="text-align:center"><span class="pill">MVP</span><div class="small">Instant demo — no install</div></div>', unsafe_allow_html=True)

st.markdown('---')

# --- Template packs
TEMPLATE_PACKS = {
    'General': {},
    'Students': {
        'linkedin': {
            'short': [
                "Finished my project on {context}. Key takeaway: {takeaway}. Grateful for mentors and lessons learned.",
                "Just shipped a small project for {context}. Learned: {takeaway}. Happy to share resources."
            ],
            'personal': [
                "As a student, building {context} taught me {insight}. Small steps matter.",
            ]
        }
    },
    'Makers': {
        'linkedin': {
            'promo': [
                "Built a small tool for {context} that helps with {benefit}. Early access: DM.",
            ],
            'short': [
                "Made progress on {context} today — main lesson: {takeaway}."
            ]
        }
    },
    'Job-seekers': {
        'linkedin': {
            'short': [
                "Looking for opportunities in {context}. I enjoy building {skill}. Open to chats."
            ]
        }
    }
}

# --- Form inputs
with st.form(key='compose'):
    st.subheader('Compose a post — pick options and press Generate')
    mode = st.radio('Mode', options=['Templates', 'AI'], index=0)
    platform = st.selectbox('Platform', options=['linkedin', 'twitter'], format_func=lambda x: 'LinkedIn' if x=='linkedin' else 'X / Twitter')
    type_ = st.selectbox('Type', options=['short', 'thread', 'promo', 'personal'], format_func=lambda x: x.title())
    tone = st.selectbox('Tone', options=['professional', 'friendly', 'casual', 'confident'], format_func=lambda x: x.title())
    context = st.text_input('Keywords / context', value='e.g., CS50, project, interview tips')
    length = st.slider('Length (verbosity)', min_value=1, max_value=5, value=3)

    st.markdown('**Template pack**')
    pack_choice = st.selectbox('Choose a template pack', options=list(TEMPLATE_PACKS.keys()))

    submit = st.form_submit_button('Generate')

# --- Core templates (fallback)
BASE_TEMPLATES = {
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

# merge selected pack templates into base for generation
def merged_templates(pack):
    merged = json.loads(json.dumps(BASE_TEMPLATES))
    pack_templates = TEMPLATE_PACKS.get(pack, {})
    for p, types in pack_templates.items():
        if p not in merged:
            merged[p] = types
        else:
            for t, arr in types.items():
                merged[p].setdefault(t, [])
                merged[p][t].extend(arr)
    return merged

TEMPLATES = merged_templates(pack_choice)

# --- Hashtag & emoji suggestions
TRENDING_TAGS = ['100DaysOfCode', 'webdev', 'coding', 'buildinpublic', 'students', 'tech']
EMOJI_MAP = {
    'professional': ['💼','✅'],
    'friendly': ['😊','🙌'],
    'casual': ['😄','🔥'],
    'confident': ['🚀','💪']
}

def suggest_hashtags(text, context):
    stop = set(['the','and','for','with','that','this','from','your','you','are','was','have','has','but','not','yet','get','got'])
    words = re.findall(r"\b\w{4,}\b", (text + ' ' + context).lower())
    candidates = [w for w in words if w not in stop]
    counts = Counter(candidates)
    most = [w for w,_ in counts.most_common(6)]
    tags = []
    for t in most:
        tag = re.sub(r'[^a-z0-9]','',t)
        if tag:
            tags.append(tag)
    for t in TRENDING_TAGS:
        if t.lower() not in tags:
            tags.append(t)
    return ['#' + x for x in tags[:6]]

def suggest_emojis(tone):
    return EMOJI_MAP.get(tone, ['✨'])

# --- Save / Load Drafts
if 'drafts' not in st.session_state:
    st.session_state['drafts'] = {}

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

PLATFORM_LIMITS = {'twitter': 280, 'linkedin': 1300}

# Initialize session state
if 'last_output' not in st.session_state:
    st.session_state['last_output'] = ''
if 'leads' not in st.session_state:
    st.session_state['leads'] = []

# --- Text analysis utilities (intelligent features)

def count_syllables(word):
    word = word.lower()
    vowels = 'aeiouy'
    syllables = 0
    prev_was_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            syllables += 1
        prev_was_vowel = is_vowel
    if word.endswith('e') and syllables > 1:
        syllables -= 1
    return max(1, syllables)

def flesch_kincaid_grade(text):
    sentences = max(1, len(re.findall(r'[.!?]+', text)))
    words = re.findall(r"\w+", text)
    word_count = max(1, len(words))
    syllables = sum(count_syllables(w) for w in words)
    score = 0.39 * (word_count / sentences) + 11.8 * (syllables / word_count) - 15.59
    return round(score, 1)

def detect_cta(text):
    patterns = ['sign up', 'signup', 'dm', 'message', 'contact', 'learn more', 'join', 'apply', 'download', 'try', 'get', 'visit']
    t = text.lower()
    return any(p in t for p in patterns)

def detect_passive(text):
    return len(re.findall(r'\b(was|were|is|are|been|being)\b\s+\w+\s+by\b', text.lower()))

def readability_feedback(text):
    grade = flesch_kincaid_grade(text)
    feedback = []
    avg_words = sum(len(s.split()) for s in re.split(r'[.!?]+', text) if s.strip())
    avg_words = avg_words or 0
    if avg_words > 20:
        feedback.append('Long sentences detected — consider splitting sentences for clarity.')
    if grade > 12:
        feedback.append(f'Text reads at ~grade {grade} — simplify language for wider audience.')
    if len(text.split()) < 20:
        feedback.append('Short posts can work well; consider adding one clear CTA or result.')
    return feedback

# --- Utility: generate QR image from text
def generate_qr_image(text):
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    return img

# --- Utility: render post as downloadable PNG
def render_post_image(text, platform='linkedin'):
    # Simple PNG rendering with wrapped text
    width = 800
    padding = 30
    font = ImageFont.load_default()
    # wrap text
    wrapper = textwrap.TextWrapper(width=60)
    lines = wrapper.wrap(text)
    line_height = 14
    height = padding*2 + line_height * (len(lines) + 2)
    img = Image.new('RGB', (width, height), color=(255,255,255))
    d = ImageDraw.Draw(img)
    y = padding
    d.text((padding,y), f'You — {platform.title()}', fill=(0,0,0), font=font)
    y += line_height*2
    for line in lines:
        d.text((padding,y), line, fill=(12,14,18), font=font)
        y += line_height
    return img

# --- Handle generate action
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
        template = sample(TEMPLATES.get(platform, {}).get(type_, BASE_TEMPLATES[platform][type_]))
        text = render_template(template, ctx)
        if length >= 4:
            text += '\n\nExtra tip: ' + ctx['advice']
        st.session_state['last_output'] = text
    else:
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

# --- Display output, preview, hashtags, emojis, drafts
with st.container():
    left, right = st.columns([2,1])
    with left:
        if st.session_state['last_output']:
            text_to_show = st.session_state['last_output']
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<strong>Generated post</strong>', unsafe_allow_html=True)

            # character counter and platform limit
            limit = PLATFORM_LIMITS.get(platform, 10000)
            count = len(text_to_show)
            warn = ''
            if count > limit:
                warn = f"⚠️ Exceeds {limit} characters (current: {count})"
            st.markdown(f"<div class='small muted'>Character count: {count} {warn}</div>", unsafe_allow_html=True)

            st.markdown(f'<div class="output-area" id="gen">{escape(text_to_show)}</div>', unsafe_allow_html=True)
            # copy button
            copy_html = f"""
            <div style='margin-top:8px'>
              <button onclick="navigator.clipboard.writeText(document.getElementById('gen').innerText)" style='background:{accent};color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer'>Copy to clipboard</button>
            </div>
            """
            components.html(copy_html, height=60)

            # Preview area (visual mock)
            st.markdown('<div style="margin-top:12px" class="preview">', unsafe_allow_html=True)
            if platform == 'linkedin':
                st.markdown(f"<strong style='font-size:15px'>You — LinkedIn preview</strong><div style='margin-top:8px'>{escape(text_to_show)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<strong style='font-size:15px'>You — X preview</strong><div style='margin-top:8px'>{escape(text_to_show)}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Phone & image helpers
            st.markdown('<div style="margin-top:8px">', unsafe_allow_html=True)
            if st.button('Show QR to send to phone'):
                qr_img = generate_qr_image(text_to_show)
                buf = io.BytesIO()
                qr_img.save(buf, format='PNG')
                buf.seek(0)
                st.image(buf)
                st.download_button('Download QR PNG', data=buf, file_name='post-qr.png')
            if st.button('Download post as image'):
                img = render_post_image(text_to_show, platform)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                st.download_button('Download post image', data=buf, file_name='post.png')
            st.markdown('</div>', unsafe_allow_html=True)

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

# Hashtag and emoji suggestions UI
if st.session_state.get('last_output'):
    suggested = suggest_hashtags(st.session_state['last_output'], context)
    emojis = suggest_emojis(tone)
    st.markdown('---')
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<strong>Suggestions</strong>', unsafe_allow_html=True)
    st.markdown(f"<div class='small muted'>Hashtags suggested from your content</div>", unsafe_allow_html=True)
    cols = st.columns(len(suggested))
    for i, tag in enumerate(suggested):
        cols[i].markdown(f"<div class='hashtag'>{tag}</div>", unsafe_allow_html=True)
    st.markdown('<div style="margin-top:8px" class="small muted">Emoji suggestions: ' + ' '.join(emojis) + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Draft save/load/export
st.markdown('---')
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<strong>Drafts</strong>', unsafe_allow_html=True)
col_d1, col_d2 = st.columns([2,1])
with col_d1:
    draft_name = st.text_input('Draft name (to save current output)')
with col_d2:
    if st.button('Save draft'):
        if st.session_state.get('last_output'):
            name = draft_name.strip() or f"draft-{len(st.session_state['drafts'])+1}"
            st.session_state['drafts'][name] = st.session_state['last_output']
            st.success(f'Saved draft: {name}')

if st.session_state['drafts']:
    sel = st.selectbox('Load a draft', options=list(st.session_state['drafts'].keys()))
    col_l1, col_l2, col_l3 = st.columns([1,1,1])
    if col_l1.button('Load'):
        st.session_state['last_output'] = st.session_state['drafts'][sel]
        st.experimental_rerun()
    if col_l2.button('Delete'):
        del st.session_state['drafts'][sel]
        st.experimental_rerun()
    if col_l3.button('Export .txt'):
        text = st.session_state['drafts'][sel]
        st.download_button('Download draft as .txt', data=text, file_name=f'{sel}.txt')

st.markdown('</div>', unsafe_allow_html=True)

# --- Intelligent Analyzer and Batch Planner
st.markdown('---')
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<strong>Smart Post Analyzer</strong>', unsafe_allow_html=True)
st.markdown('<div class="small muted">Analyze the current generated post and get actionable suggestions to improve engagement.</div>', unsafe_allow_html=True)

if st.session_state.get('last_output'):
    analysis_text = st.session_state['last_output']
    grade = flesch_kincaid_grade(analysis_text)
    passive_count = detect_passive(analysis_text)
    has_cta = detect_cta(analysis_text)
    feedback = readability_feedback(analysis_text)

    st.markdown(f"<div style='margin-top:8px'><strong>Readability (approx grade level):</strong> {grade}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>Passive constructions found:</strong> {passive_count}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>Call-to-action present:</strong> {'Yes' if has_cta else 'No'}</div>", unsafe_allow_html=True)
    if feedback:
        st.markdown('<div style="margin-top:8px"><strong>Suggestions:</strong></div>', unsafe_allow_html=True)
        for f in feedback:
            st.markdown(f"<div class='small muted'>• {f}</div>", unsafe_allow_html=True)
    st.markdown('<div style="margin-top:8px"><strong>Micro-edit suggestions</strong></div>', unsafe_allow_html=True)
    if not has_cta:
        st.markdown("<div class='small muted'>• Add a single clear CTA (e.g., 'DM me to try', 'Sign up for early access', 'Check the repo').</div>", unsafe_allow_html=True)
    if passive_count > 0:
        st.markdown("<div class='small muted'>• Avoid passive voice (e.g., 'was built by' → rewrite as 'I built').</div>", unsafe_allow_html=True)
    if grade > 12:
        st.markdown("<div class='small muted'>• Simplify complex sentences and replace jargon with plain language.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="small muted">Generate a post first to analyze it.</div>', unsafe_allow_html=True)

# --- Batch Generator
st.markdown('---')
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<strong>Batch Planner</strong>', unsafe_allow_html=True)
st.markdown('<div class="small muted">Create multiple variations and export as CSV for scheduling.</div>', unsafe_allow_html=True)
num = st.number_input('Number of variations', min_value=1, max_value=20, value=5)
include_hashtags = st.checkbox('Include suggested hashtags', value=True)
include_emojis = st.checkbox('Include suggested emojis', value=False)
if st.button('Generate batch'):
    rows = []
    for i in range(int(num)):
        tone_variation = random.choice(['professional','friendly','casual','confident'])
        tpl = sample(TEMPLATES.get(platform, {}).get(type_, BASE_TEMPLATES[platform][type_]))
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
        text = render_template(tpl, ctx)
        hashtags = suggest_hashtags(text, context) if include_hashtags else []
        emojis = suggest_emojis(tone_variation) if include_emojis else []
        rows.append({'platform': platform, 'type': type_, 'tone': tone_variation, 'context': context, 'text': text, 'hashtags': ' '.join(hashtags), 'emojis': ' '.join(emojis)})
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=['platform','type','tone','context','text','hashtags','emojis'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    buffer.seek(0)
    st.download_button('Download batch as CSV', data=buffer.getvalue(), file_name='ai-post-composer-batch.csv', mime='text/csv')
    st.success(f'Generated {len(rows)} variations')
st.markdown('</div>', unsafe_allow_html=True)

# --- Waitlist / leads capture (no external service required)
st.markdown('---')
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<strong>Join the waitlist / get updates</strong>', unsafe_allow_html=True)
lead_email = st.text_input('Enter your email to join the waitlist')
if st.button('Join waitlist'):
    if lead_email:
        st.session_state['leads'].append(lead_email)
        st.success('Thanks — saved. You will be notified about new features and early access!')
if st.session_state['leads']:
    if st.button('Download leads (CSV)'):
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['email'])
        for e in st.session_state['leads']:
            w.writerow([e])
        buf.seek(0)
        st.download_button('Download CSV', data=buf.getvalue(), file_name='leads.csv')
st.markdown('</div>', unsafe_allow_html=True)

# Footer and CTA
st.markdown('---')
colL, colR = st.columns([3,1])
with colL:
    st.markdown('**Ready to try?** Use the live demo, or get the lifetime MVP on Gumroad (install instructions included).')
    st.markdown('**Pricing:** $19 one-time · 7-day refund if install fails')
with colR:
    st.markdown('<a class="cta" href="REPLACE_WITH_GUMROAD_LINK" target="_blank">Buy — $19</a>', unsafe_allow_html=True)

st.sidebar.markdown('---')
st.sidebar.write('Want this as a Chrome extension? The extension calls the same AI backend and offers a popup UI.')
st.sidebar.markdown('**Support:** https://github.com/madhugurjar954-cloud/ai-post-composer/issues')
