// Updated popup.js with AI calls and license activation
const templates = {
  linkedin: { /* ... same as before ... */ },
  twitter: { /* ... same as before ... */ }
};

// For brevity, load the original templates from a small inline function
(function loadTemplates(){
  templates.linkedin = {
    short:["Here’s what I learned from {context} — key takeaway: {takeaway}. If you're learning CS, try this.","Finished a small project on {context}. Main lesson: {takeaway}. Happy to share the repo if you want."] ,
    thread:["Thread: lessons from {context}\n\n1) {point1}\n2) {point2}\n3) {point3}\n\nIf you're starting with CS, focus on {advice}.","I built something for {context} — the surprising part was {surprise}. Here’s how I solved it: {steps}."] ,
    promo:["Launching: {context} project — it helps with {benefit}. DM me for early access.","I've opened early access to my {context} tool. Sign up to try it and get feedback."],
    personal:["Today I realized that {insight} while working on {context}. That changed my approach to {practice}.","I used to struggle with {problem}. After working on {context}, I now {result}."]
  }
  templates.twitter = {
    short:["{context}: {takeaway} #100DaysOfCode","Built a thing for {context}. Key lesson: {takeaway}"],
    thread:["1/ Thread: {context}\n2/ {point1}\n3/ {point2}\n4/ {point3}\n5/ TL;DR: {advice}","1/ I tried {context} and here are the steps that worked: {steps}\n2/ {result}"],
    promo:["Launching {context} — helps with {benefit}. More info: [link]","Early access open for {context}. DM me!"],
    personal:["Working on {context} made me realize {insight}. #devlife","Small wins: {context} -> {result}."]
  }
})();

function sample(list){ return list[Math.floor(Math.random()*list.length)] }
function fill(template, ctx){ return template.replace(/\{([^}]+)\}/g, (_, key) => ctx[key] || ("[" + key + "]")); }

const platformEl = document.getElementById('platform')
const typeEl = document.getElementById('type')
const toneEl = document.getElementById('tone')
const contextEl = document.getElementById('context')
const lengthEl = document.getElementById('length')
const lengthValue = document.getElementById('lengthValue')
const outputEl = document.getElementById('output')
const generateBtn = document.getElementById('generate')
const generateAIBtn = document.getElementById('generateAI')
const copyBtn = document.getElementById('copy')
const licenseInput = document.getElementById('license')
const activateBtn = document.getElementById('activate')
const licenseStatus = document.getElementById('licenseStatus')
const apiBaseInput = document.getElementById('apiBase')

const lengthMap = {1:'Very short',2:'Short',3:'Medium',4:'Long',5:'Very long'}
lengthEl.addEventListener('input', ()=> lengthValue.textContent = lengthMap[lengthEl.value])

// Load saved settings
chrome.storage.local.get(['last','license','licenseActive','apiBase'], res=>{
  if(res.last){
    platformEl.value = res.last.platform || 'linkedin'
    typeEl.value = res.last.type || 'short'
    toneEl.value = res.last.tone || 'professional'
    contextEl.value = res.last.context || ''
  }
  if(res.license) licenseInput.value = res.license
  if(res.apiBase) apiBaseInput.value = res.apiBase
  if(res.licenseActive){ licenseStatus.textContent = 'Activated'; licenseStatus.style.color = '#059669' }
})

// Template generator
generateBtn.addEventListener('click', ()=>{
  const platform = platformEl.value
  const type = typeEl.value
  const context = contextEl.value || "a project"
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
  const len = parseInt(lengthEl.value)
  if(len >=4) text = text + "\n\n" + "Extra tip: " + ctx.advice
  outputEl.value = text
  chrome.storage.local.set({last: {platform,type,tone,context}})
})

// AI generation
generateAIBtn.addEventListener('click', async ()=>{
  const apiBase = apiBaseInput.value.trim()
  if(!apiBase){ alert('Please set your deployed API base URL in the API base field before using AI generation.'); return }
  const license = licenseInput.value.trim()
  if(!license){ alert('Please enter your Pro license key and activate it first.'); return }

  generateAIBtn.textContent = 'Generating...'
  try{
    const payload = {
      platform: platformEl.value,
      type: typeEl.value,
      tone: toneEl.value,
      context: contextEl.value || 'a project',
      length: lengthEl.value,
      license
    }
    const resp = await fetch(apiBase + '/api/generate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    })
    const data = await resp.json()
    if(resp.ok && data.text){
      outputEl.value = data.text
    } else {
      outputEl.value = data.error || JSON.stringify(data)
    }
  } catch(err){
    outputEl.value = 'Error: ' + err.message
  }
  generateAIBtn.textContent = 'Generate (AI)'
})

// Copy
copyBtn.addEventListener('click', ()=>{
  outputEl.select()
  document.execCommand('copy')
  copyBtn.textContent = 'Copied ✓'
  setTimeout(()=> copyBtn.textContent = 'Copy',1500)
})

// Activate license
activateBtn.addEventListener('click', async ()=>{
  const license = licenseInput.value.trim()
  const apiBase = apiBaseInput.value.trim()
  if(!license){ alert('Paste your license key first'); return }
  chrome.storage.local.set({license})
  if(!apiBase){
    // no server – assume local dev or no enforcement
    chrome.storage.local.set({licenseActive:true}, ()=>{
      licenseStatus.textContent = 'Activated (local)'; licenseStatus.style.color = '#059669'
    })
    return
  }
  activateBtn.textContent = 'Checking...'
  try{
    const resp = await fetch(apiBase + '/api/checkLicense', {
      method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({license})
    })
    const data = await resp.json()
    if(resp.ok && data.valid){
      chrome.storage.local.set({licenseActive:true}, ()=>{
        licenseStatus.textContent = 'Activated'; licenseStatus.style.color = '#059669'
      })
    } else {
      chrome.storage.local.set({licenseActive:false}, ()=>{
        licenseStatus.textContent = 'Invalid key'; licenseStatus.style.color = '#e11d48'
      })
    }
  } catch(err){
    licenseStatus.textContent = 'Check failed'; licenseStatus.style.color = '#e11d48'
  }
  activateBtn.textContent = 'Activate'
})

// Save apiBase on change
apiBaseInput.addEventListener('change', ()=>{
  chrome.storage.local.set({apiBase: apiBaseInput.value.trim()})
})
