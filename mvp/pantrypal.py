"""
PantryPal MVP - Full Python App
================================
SETUP (run these in your terminal first):
    pip install flask anthropic

HOW TO RUN:
    1. Paste your Anthropic API key below where it says YOUR_API_KEY_HERE
       (or set the environment variable: export ANTHROPIC_API_KEY=sk-...)
    2. Run:  python pantrypal.py
    3. Open: http://localhost:5000

Get an API key at: https://console.anthropic.com
"""

import os
import json
from flask import Flask, request, jsonify
import anthropic

# ── API Key ────────────────────────────────────────────────────────────────────
# Option 1: paste your key directly here
API_KEY = "YOUR_API_KEY_HERE"

# Option 2: reads from environment variable ANTHROPIC_API_KEY (recommended)
if API_KEY == "YOUR_API_KEY_HERE":
    API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Flask App ──────────────────────────────────────────────────────────────────
app = Flask(__name__)

SYSTEM_PROMPT = """You are PantryPal, a friendly cooking assistant. The user will give you a list of ingredients they have. Suggest exactly 3 realistic, appetizing meals.

Respond ONLY with a valid JSON array (no markdown, no preamble, no backticks) with exactly 3 objects:
- "name": string — meal name
- "emoji": string — one food emoji
- "description": string — 1-2 sentence appetizing description
- "usedIngredients": string[] — ingredients from the user's list used in this meal
- "missingIngredients": string[] — extra ingredients needed (max 4, keep minimal)
- "difficulty": "Easy" | "Medium" | "Hard"
- "time": string — e.g. "15 min", "30 min", "1 hr"

Prioritize meals that use most of the provided ingredients. Be creative but realistic."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PantryPal</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;0,800;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #faf6ef;
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
  }

  /* Background blobs */
  .blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(90px);
    opacity: 0.18;
    pointer-events: none;
    z-index: 0;
  }
  .blob-1 { width: 520px; height: 520px; background: #c97d4e; top: -160px; right: -160px; }
  .blob-2 { width: 420px; height: 420px; background: #6b8f60; bottom: 80px;  left:  -130px; }

  .wrap {
    position: relative;
    z-index: 1;
    max-width: 980px;
    margin: 0 auto;
    padding: 0 20px 80px;
  }

  /* Header */
  .header {
    text-align: center;
    padding: 52px 0 30px;
    animation: fadeDown .6s ease both;
  }
  .logo-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  .logo-icon {
    font-size: 44px;
    animation: wobble 3.5s ease-in-out infinite;
  }
  @keyframes wobble {
    0%,100% { transform: rotate(-5deg); }
    50%      { transform: rotate( 5deg); }
  }
  .title {
    font-family: 'Fraunces', serif;
    font-size: clamp(42px, 7vw, 62px);
    font-weight: 800;
    color: #2c1f0e;
    letter-spacing: -1.5px;
    line-height: 1;
  }
  .subtitle {
    font-size: 16px;
    color: #7a6650;
    font-weight: 300;
    max-width: 430px;
    margin: 0 auto;
    line-height: 1.65;
  }

  /* Input card */
  .input-card {
    max-width: 640px;
    margin: 0 auto 44px;
    background: #fff9f2;
    border: 1.5px solid #e8ddd0;
    border-radius: 22px;
    padding: 28px;
    box-shadow: 0 8px 40px rgba(100,60,20,.08);
    animation: fadeUp .7s .15s ease both;
  }
  .card-label {
    font-family: 'Fraunces', serif;
    font-size: 18px;
    color: #2c1f0e;
    margin-bottom: 6px;
    display: block;
  }
  .card-hint {
    font-size: 13px;
    color: #9e8b78;
    font-style: italic;
    margin-bottom: 14px;
  }
  textarea {
    width: 100%;
    min-height: 110px;
    background: #faf6ef;
    border: 1.5px solid #ddd0c3;
    border-radius: 12px;
    padding: 14px 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: #2c1f0e;
    resize: vertical;
    outline: none;
    line-height: 1.65;
    transition: border-color .2s, box-shadow .2s;
  }
  textarea:focus {
    border-color: #c97d4e;
    box-shadow: 0 0 0 3px rgba(201,125,78,.15);
  }
  textarea::placeholder { color: #bfb0a0; }

  .btn {
    margin-top: 16px;
    width: 100%;
    padding: 15px;
    background: #2c1f0e;
    color: #faf6ef;
    font-family: 'Fraunces', serif;
    font-size: 17px;
    font-weight: 700;
    border: none;
    border-radius: 13px;
    cursor: pointer;
    transition: transform .15s, background .2s, box-shadow .2s;
    letter-spacing: .2px;
  }
  .btn:hover:not(:disabled) {
    background: #c97d4e;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(201,125,78,.35);
  }
  .btn:disabled { opacity: .55; cursor: not-allowed; transform: none; }

  /* Loading */
  .loading {
    display: none;
    text-align: center;
    padding: 38px;
    animation: fadeUp .4s ease both;
  }
  .spinner {
    display: inline-block;
    width: 48px; height: 48px;
    border: 3px solid #e8ddd0;
    border-top-color: #c97d4e;
    border-radius: 50%;
    animation: spin .9s linear infinite;
    margin-bottom: 14px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading p { font-family: 'Fraunces', serif; font-size: 18px; color: #7a6650; font-style: italic; }

  /* Error */
  .error-box {
    display: none;
    max-width: 560px;
    margin: 0 auto 24px;
    background: #fff0ec;
    border: 1.5px solid #f5c4b8;
    color: #a03020;
    border-radius: 13px;
    padding: 15px 20px;
    font-size: 14px;
    text-align: center;
  }

  /* Results */
  .results-title {
    display: none;
    font-family: 'Fraunces', serif;
    font-size: 26px;
    color: #2c1f0e;
    text-align: center;
    margin-bottom: 26px;
    animation: fadeUp .5s ease both;
  }
  .results-title span { color: #c97d4e; }

  /* Flip grid */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
    gap: 20px;
  }

  .flip-wrapper {
    perspective: 1200px;
    height: 355px;
    cursor: pointer;
    animation: fadeUp .5s ease both;
  }
  .flip-wrapper:nth-child(2) { animation-delay: .1s; }
  .flip-wrapper:nth-child(3) { animation-delay: .2s; }

  .flip-inner {
    position: relative;
    width: 100%; height: 100%;
    transform-style: preserve-3d;
    transition: transform .55s cubic-bezier(.4,0,.2,1);
  }
  .flip-inner.flipped { transform: rotateY(180deg); }

  .face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    border-radius: 18px;
    padding: 24px;
    border: 1.5px solid #e8ddd0;
    box-shadow: 0 5px 24px rgba(100,60,20,.08);
    transition: box-shadow .2s;
  }
  .face:hover { box-shadow: 0 10px 36px rgba(100,60,20,.14); }

  /* Front face */
  .front { background: #fff9f2; }
  .meal-emoji { font-size: 50px; display: block; margin-bottom: 10px; }
  .meal-name  {
    font-family: 'Fraunces', serif;
    font-size: 21px;
    color: #2c1f0e;
    margin-bottom: 8px;
    line-height: 1.2;
  }
  .meal-desc { font-size: 13.5px; color: #7a6650; line-height: 1.65; margin-bottom: 14px; }
  .meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .badge {
    font-size: 12px; font-weight: 500;
    padding: 4px 11px; border-radius: 999px;
    background: #f0e8dc; color: #6b4f30;
  }
  .badge-diff {
    font-size: 12px; font-weight: 500;
    padding: 4px 11px; border-radius: 999px;
    color: #fff;
  }
  .flip-hint {
    position: absolute; bottom: 15px; right: 18px;
    font-size: 11.5px; color: #bfb0a0; font-style: italic;
  }

  /* Back face */
  .back { background: #2c1f0e; color: #faf6ef; transform: rotateY(180deg); }
  .back-section-title {
    font-size: 10px; color: #c97d4e;
    text-transform: uppercase; letter-spacing: .8px;
    font-weight: 600; margin-bottom: 7px;
  }
  .back-section-title + .tag-row { margin-bottom: 14px; }
  .tag-row { display: flex; flex-wrap: wrap; gap: 5px; }
  .tag { font-size: 12px; padding: 4px 10px; border-radius: 999px; }
  .tag-have { background: rgba(76,175,125,.2);  color: #7ef5b0; }
  .tag-need { background: rgba(240,165,0,.2);   color: #f0c84e; }
  .all-good  { font-size: 13px; color: #7ef5b0; margin-top: 10px; }
  .back-hint {
    position: absolute; bottom: 15px; right: 18px;
    font-size: 11.5px; color: #7a6650; font-style: italic;
  }

  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-22px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(26px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>

<div class="blob blob-1"></div>
<div class="blob blob-2"></div>

<div class="wrap">

  <!-- Header -->
  <header class="header">
    <div class="logo-row">
      <span class="logo-icon">🥘</span>
      <h1 class="title">PantryPal</h1>
    </div>
    <p class="subtitle">Type what's in your fridge. We'll find meals you can make right now.</p>
  </header>

  <!-- Input -->
  <div class="input-card">
    <label class="card-label" for="ingInput">What do you have?</label>
    <p class="card-hint">e.g. "eggs, rice, half an onion, soy sauce, garlic, leftover chicken"</p>
    <textarea id="ingInput" placeholder="List your ingredients here…"></textarea>
    <button class="btn" id="suggestBtn" onclick="getSuggestions()">✨ Suggest Meals</button>
  </div>

  <!-- Loading / Error -->
  <div class="loading" id="loadingDiv">
    <div class="spinner"></div>
    <p>Raiding your pantry…</p>
  </div>
  <div class="error-box" id="errorDiv"></div>

  <!-- Results -->
  <h2 class="results-title" id="resultsTitle">Here are <span>3 meals</span> you can make</h2>
  <div class="grid" id="grid"></div>

</div>

<script>
const DIFF_COLOR = { Easy: '#4caf7d', Medium: '#f0a500', Hard: '#e05a3a' };
let flipState = {};

async function getSuggestions() {
  const ing = document.getElementById('ingInput').value.trim();
  if (!ing) return;

  document.getElementById('suggestBtn').disabled = true;
  document.getElementById('loadingDiv').style.display = 'block';
  document.getElementById('errorDiv').style.display  = 'none';
  document.getElementById('resultsTitle').style.display = 'none';
  document.getElementById('grid').innerHTML = '';
  flipState = {};

  try {
    const res  = await fetch('/suggest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ingredients: ing })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Server error');
    renderMeals(data.meals);
  } catch (e) {
    const err = document.getElementById('errorDiv');
    err.style.display = 'block';
    err.textContent   = '⚠️ ' + e.message;
  }

  document.getElementById('loadingDiv').style.display = 'none';
  document.getElementById('suggestBtn').disabled = false;
}

function renderMeals(meals) {
  document.getElementById('resultsTitle').style.display = 'block';
  const grid = document.getElementById('grid');

  meals.forEach((m, i) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'flip-wrapper';
    wrapper.onclick   = () => {
      flipState[i] = !flipState[i];
      inner.classList.toggle('flipped', flipState[i]);
    };

    const inner   = document.createElement('div');
    inner.className = 'flip-inner';

    const used    = m.usedIngredients    || [];
    const missing = m.missingIngredients || [];
    const diff    = m.difficulty || 'Easy';

    inner.innerHTML = `
      <div class="face front">
        <span class="meal-emoji">${m.emoji}</span>
        <div class="meal-name">${m.name}</div>
        <p class="meal-desc">${m.description}</p>
        <div class="meta">
          <span class="badge">⏱ ${m.time}</span>
          <span class="badge-diff" style="background:${DIFF_COLOR[diff] || '#888'}">${diff}</span>
        </div>
        <span class="flip-hint">Tap for ingredients →</span>
      </div>
      <div class="face back">
        <p class="back-section-title">✅ You have</p>
        <div class="tag-row">${used.map(t => `<span class="tag tag-have">${t}</span>`).join('')}</div>
        ${missing.length > 0
          ? `<p class="back-section-title">🛒 You'll also need</p>
             <div class="tag-row">${missing.map(t => `<span class="tag tag-need">${t}</span>`).join('')}</div>`
          : `<p class="all-good">🎉 You have everything!</p>`}
        <span class="back-hint">← Tap to go back</span>
      </div>`;

    wrapper.appendChild(inner);
    grid.appendChild(wrapper);
  });
}

// Ctrl/Cmd + Enter to submit
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('ingInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) getSuggestions();
  });
});
</script>
</body>
</html>"""


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML_PAGE


@app.route("/suggest", methods=["POST"])
def suggest():
    if not API_KEY:
        return jsonify({"error": "No API key set. Add your key at the top of pantrypal.py"}), 500

    data = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients", "").strip()

    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    try:
        client = anthropic.Anthropic(api_key=API_KEY)

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"My ingredients: {ingredients}"}
            ],
        )

        raw   = message.content[0].text
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        meals = json.loads(clean)

        return jsonify({"meals": meals})

    except json.JSONDecodeError:
        return jsonify({"error": "Could not parse meal suggestions. Try again!"}), 500
    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key. Check the key at the top of pantrypal.py"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  No API key found!")
        print("   Open pantrypal.py and paste your key where it says YOUR_API_KEY_HERE")
        print("   OR run:  export ANTHROPIC_API_KEY=sk-...\n")
    else:
        print("\n🥘  PantryPal is running!")
        print("   Open your browser at: http://localhost:5000\n")

    app.run(debug=True, port=5000)
