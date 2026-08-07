// Simple template-based generator (MVP). No external network calls.
const templates = {
  linkedin: {
    short: [
      "Here’s what I learned from {context} — key takeaway: {takeaway}. If you're learning CS, try this.",
      "Finished a small project on {context}. Main lesson: {takeaway}. Happy to share the repo if you want."
    ],
    thread: [
      "Thread: lessons from {context}\n\n1) {point1}\n2) {point2}\n3) {point3}\n\nIf you're starting with CS, focus on {advice}.",
      "I built something for {context} — the surprising part was {surprise}. Here’s how I solved it: {steps}."
    ],
    promo: [
      "Launching: {context} project — it helps with {benefit}. DM me for early access.",
      "I've opened early access to my {context} tool. Sign up to try it and get feedback."
    ],
    personal: [
      "Today I realized that {insight} while working on {context}. That changed my approach to {practice}.",
      "I used to struggle with {problem}. After working on {context}, I now {result}."
    ]
  },
  twitter: {
    short: [
      "{context}: {takeaway} #100DaysOfCode",
      "Built a thing for {context}. Key lesson: {takeaway}"
    ],
    thread: [
      "1/ Thread: {context}\n2/ {point1}\n3/ {point2}\n4/ {point3}\n5/ TL;DR: {advice}",
      "1/ I tried {context} and here are the steps that worked: {steps}\n2/ {result}"
    ],
    promo: [
      "Launching {context} — helps with {benefit}. More info: [link]",
      "Early access open for {context}. DM me!"
    ],
    personal: [
      "Working on {context} made me realize {insight}. #devlife",
      "Small wins: {context} -> {result}."
    ]
  }
};

function sample(list){ return list[Math.floor(Math.random()*list.length)] }

function fill(template, ctx){
  return template.replace(/\{([^}]+)\}/g, (_, key) => ctx[key] || ("[" + key + "]"));
}

const platformEl = document.getElementById('platform')
const typeEl = document.getElementById('type')
const toneEl = document.getElementById('tone')
const contextEl = document.getElementById('context')
const lengthEl = document.getElementById('length')
const lengthValue = document.getElementById('lengthValue')
const outputEl = document.getElementById('output')
const generateBtn = document.getElementById('generate')
const copyBtn = document.getElementById('copy')

const lengthMap = {1:'Very short',2:'Short',3:'Medium',4:'Long',5:'Very long'}
lengthEl.addEventListener('input', ()=> lengthValue.textContent = lengthMap[lengthEl.value])

generateBtn.addEventListener('click', ()=>{
  const platform = platformEl.value
  const type = typeEl.value
  const context = contextEl.value || "a project"
  const tone = toneEl.value
  // create a simple context object:
  const ctx = {
    context,
    takeaway: "focus on fundamentals",
    point1: "practice daily",
    point2: "build projects",
    point3: "read docs",
    advice: "start small and iterate",
    surprise: "it was easier than expected",
    steps: "1) plan 2) implement 3) test",
    insight: "small progress compounds",
    result: "I can explain it clearly"
  }
  const template = sample(templates[platform][type])
  let text = fill(template, ctx)
  // adjust length by repeating or trimming
  const len = parseInt(lengthEl.value)
  if(len >=4) text = text + "\n\n" + "Extra tip: " + ctx.advice
  outputEl.value = text
  // save last used
  chrome.storage.local.set({last: {platform,type,tone,context}})
})

copyBtn.addEventListener('click', ()=>{
  outputEl.select()
  document.execCommand('copy')
  copyBtn.textContent = 'Copied ✓'
  setTimeout(()=> copyBtn.textContent = 'Copy',1500)
})

// Load previous
chrome.storage.local.get('last', res=>{
  if(res.last){
    platformEl.value = res.last.platform || 'linkedin'
    typeEl.value = res.last.type || 'short'
    toneEl.value = res.last.tone || 'professional'
    contextEl.value = res.last.context || ''
  }
})
