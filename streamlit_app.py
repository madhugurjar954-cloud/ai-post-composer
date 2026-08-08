import streamlit as st
import os
import requests
import json

st.set_page_config(page_title="AI Post Composer — Demo", layout="centered")

st.title("AI Post Composer — Live Demo")
st.write("A simple web demo for the AI Post Composer. Use Templates or enable Pro (AI) generation.")

# UI controls
platform = st.selectbox("Platform", options=["linkedin", "twitter"], format_func=lambda x: "LinkedIn" if x=="linkedin" else "X / Twitter")
type_ = st.selectbox("Type", options=["short", "thread", "promo", "personal"], format_func=lambda x: x.title())
tone = st.selectbox("Tone", options=["professional", "friendly", "casual", "confident"], format_func=lambda x: x.title())
context = st.text_input("Keywords / context", value="e.g., CS50, project, interview tips")
length = st.slider("Length", min_value=1, max_value=5, value=3)

col1, col2 = st.columns(2)
with col1:
    generate_templates = st.button("Generate (Templates)")
with col2:
    generate_ai = st.button("Generate (AI)")

st.markdown("---")
output = st.empty()

# License and API base
st.sidebar.header("Pro / Deployment")
license_key = st.sidebar.text_input("Pro license key (optional)")
api_base = st.sidebar.text_input("API base (deployed server URL)", value="")

# Templates (same lightweight templates as extension)
TEMPLATES = {
    "linkedin": {
        "short": [
            "Here’s what I learned from {context} — key takeaway: {takeaway}. If you're learning CS, try this.",
            "Finished a small project on {context}. Main lesson: {takeaway}. Happy to share the repo if you want."
        ],
        "thread": [
            "Thread: lessons from {context}\n\n1) {point1}\n2) {point2}\n3) {point3}\n\nIf you're starting with CS, focus on {advice}.",
            "I built something for {context} — the surprising part was {surprise}. Here’s how I solved it: {steps}."
        ],
        "promo": [
            "Launching: {context} project — it helps with {benefit}. DM me for early access.",
            "I've opened early access to my {context} tool. Sign up to try it and get feedback."
        ],
        "personal": [
            "Today I realized that {insight} while working on {context}. That changed my approach to {practice}.",
            "I used to struggle with {problem}. After working on {context}, I now {result}."
        ]
    },
    "twitter": {
        "short": [
            "{context}: {takeaway} #100DaysOfCode",
            "Built a thing for {context}. Key lesson: {takeaway}"
        ],
        "thread": [
            "1/ Thread: {context}\n2/ {point1}\n3/ {point2}\n4/ {point3}\n5/ TL;DR: {advice}",
            "1/ I tried {context} and here are the steps that worked: {steps}\n2/ {result}"
        ],
        "promo": [
            "Launching {context} — helps with {benefit}. More info: [link]",
            "Early access open for {context}. DM me!"
        ],
        "personal": [
            "Working on {context} made me realize {insight}. #devlife",
            "Small wins: {context} -> {result}."
        ]
    }
}

import random

def sample(list_):
    return random.choice(list_)


def fill(template, ctx):
    return template.replace("{", "{{").replace("}", "}}") if False else template

# We will do simple replacement using format-style keys

def render_template(template, ctx):
    try:
        return template.format(**ctx)
    except Exception:
        # fallback: naive replacement
        text = template
        for k, v in ctx.items():
            text = text.replace('{' + k + '}', v)
        return text


if generate_templates:
    ctx = {
        "context": context,
        "takeaway": "focus on fundamentals",
        "point1": "practice daily",
        "point2": "build projects",
        "point3": "read docs",
        "advice": "start small and iterate",
        "surprise": "it was easier than expected",
        "steps": "1) plan 2) implement 3) test",
        "insight": "small progress compounds",
        "result": "I can explain it clearly",
        "practice": "building small projects",
        "problem": "getting stuck on docs",
        "benefit": "save time"
    }
    template = sample(TEMPLATES[platform][type_])
    text = render_template(template, ctx)
    if length >= 4:
        text += "\n\nExtra tip: " + ctx['advice']
    output.text_area("Generated post", value=text, height=240)


if generate_ai:
    st.info("Sending request to AI... this uses your OPENAI API key on the server.")
    # Build payload
    payload = {
        "platform": platform,
        "type": type_,
        "tone": tone,
        "context": context,
        "length": length,
        "license": license_key
    }

    # Determine OPENAI key (prefer Streamlit secrets)
    OPENAI_KEY = None
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
    else:
        OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

    # If user provided api_base, call that; otherwise, call OpenAI directly from server (not recommended)
    if api_base:
        try:
            resp = requests.post(api_base.rstrip('/') + '/api/generate', json=payload, timeout=30)
            if resp.ok:
                data = resp.json()
                text = data.get('text') or json.dumps(data)
                output.text_area("Generated (AI)", value=text, height=240)
            else:
                output.text_area("Error from API", value=resp.text, height=160)
        except Exception as e:
            st.error("API request failed: " + str(e))
    else:
        if not OPENAI_KEY:
            st.error("No OpenAI API key found. Add OPENAI_API_KEY to Streamlit secrets or set the API base to your deployed server.")
        else:
            # Call OpenAI chat completions directly from the Streamlit app (server-side)
            prompt = f"You are a helpful assistant that writes social media posts. Platform: {platform} Type: {type_} Tone: {tone} Context: {context} Length: {length}. Produce one polished output appropriate for the platform."
            try:
                headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
                body = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You generate concise social media posts based on the user instructions."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.7
                }
                r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=30)
                if r.ok:
                    j = r.json()
                    content = j.get('choices', [{}])[0].get('message', {}).get('content', '')
                    output.text_area("Generated (AI)", value=content, height=240)
                else:
                    output.text_area("OpenAI error", value=r.text, height=160)
            except Exception as e:
                st.error("OpenAI call failed: " + str(e))


# Footer / purchase
st.markdown("---")
col1, col2 = st.columns([3,1])
with col1:
    st.write("MVP: Templates-only mode works without any API key. Pro (AI) mode requires an OpenAI key on the server or an API base URL.")
with col2:
    st.button("Buy — $19")

st.sidebar.markdown("---")
st.sidebar.write("Streamlit demo — deploy to Streamlit Cloud or provide an API base to use serverless endpoints.")
