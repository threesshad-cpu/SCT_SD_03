from flask import Flask, render_template_string, jsonify, request
import random
import copy

app = Flask(__name__)

# --- PROCEDURAL SHUFFLE ENGINE ---
def transform_grid(grid):
    """Generates a unique variation of a Sudoku grid via symmetry and swaps."""
    new_grid = copy.deepcopy(grid)
    size = len(grid)
    # 1. Random Rotations
    for _ in range(random.randint(0, 3)):
        new_grid = [list(row) for row in zip(*new_grid[::-1])]
    # 2. Random Transpose
    if random.choice([True, False]):
        new_grid = [list(row) for row in zip(*new_grid)]
    return new_grid

# Seeds for Lvl 1-5
SEEDS = {
    "Lvl 1 Noob (4x4)": [[[2, 0, 4, 1], [1, 4, 3, 2], [4, 0, 2, 3], [3, 2, 1, 4]]],
    "Lvl 2 Beginner (4x4)": [[[1, 2, 4, 3], [4, 3, 2, 1], [3, 0, 1, 2], [0, 1, 3, 4]]],
    "Lvl 3 Casual (9x9)": [[[0, 3, 7, 2, 0, 4, 6, 9, 8], [2, 8, 9, 3, 7, 6, 1, 4, 5], [4, 6, 5, 8, 9, 1, 7, 2, 3], [5, 7, 1, 4, 6, 2, 3, 8, 9], [6, 9, 2, 1, 8, 5, 0, 0, 0], [0, 0, 0, 0, 0, 7, 0, 5, 0], [0, 2, 0, 0, 0, 0, 0, 0, 6], [0, 0, 6, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0]]],
    "Lvl 4 Smart (9x9)": [[[5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]]],
    "Lvl 5 Pro (9x9)": [[[0, 0, 0, 2, 6, 0, 7, 0, 1], [6, 8, 0, 0, 7, 0, 0, 9, 0], [1, 9, 0, 0, 0, 4, 5, 0, 0], [8, 2, 0, 1, 0, 0, 0, 4, 0], [0, 0, 4, 6, 0, 2, 9, 0, 0], [0, 5, 0, 0, 0, 3, 0, 2, 8], [0, 0, 9, 3, 0, 0, 0, 7, 4], [0, 4, 0, 0, 5, 0, 0, 3, 6], [7, 0, 3, 0, 1, 8, 0, 0, 0]]]
}

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/get-puzzle', methods=['POST'])
def get_puzzle():
    mode = request.json.get('mode', 'Lvl 1 Noob (4x4)')
    seed_pool = SEEDS.get(mode, SEEDS["Lvl 1 Noob (4x4)"])
    # Procedural Shuffle ensures every mission is unique
    shuffled_puzzle = transform_grid(random.choice(seed_pool))
    return jsonify({"puzzle": shuffled_puzzle, "size": len(shuffled_puzzle)})

# --- PROFESSIONAL NEUMORPHIC UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sudoku Titan v11.3 | SCT/DEC25/0792</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <style>
        :root { --bg: #e0e5ec; --text: #4a4a8c; --accent: #6b5fb5; --shadow-light: #ffffff; --shadow-dark: #a3b1c6; }
        [data-theme="dark"] { --bg: #2d3436; --text: #ffffff; --accent: #74b9ff; --shadow-light: #3d4648; --shadow-dark: #1e2324; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; height: 100vh; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
        .layout { display: grid; grid-template-columns: 280px 1fr 320px; gap: 30px; width: 95%; max-width: 1500px; align-items: center; }
        .card { padding: 25px; border-radius: 30px; background: var(--bg); box-shadow: 9px 9px 16px var(--shadow-dark), -9px -9px 16px var(--shadow-light); margin-bottom: 25px; position: relative; }
        .btn { border: none; background: var(--bg); color: var(--text); padding: 12px; border-radius: 15px; cursor: pointer; box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light); font-weight: bold; width: 100%; margin-bottom: 12px; transition: 0.2s; }
        .btn:active, .btn.active { box-shadow: inset 3px 3px 6px var(--shadow-dark), inset -3px -3px 6px var(--shadow-light); color: var(--accent); }
        .grid-frame { padding: 20px; border-radius: 35px; background: var(--bg); box-shadow: 15px 15px 30px var(--shadow-dark), -15px -15px 30px var(--shadow-light); display: flex; justify-content: center; }
        .sudoku-grid { display: grid; gap: 8px; justify-content: center; }
        .cell { width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; box-shadow: 4px 4px 8px var(--shadow-dark), -4px -4px 8px var(--shadow-light); background: var(--bg); color: var(--text); transition: 0.1s; }
        .cell.peeking { background: var(--accent) !important; color: white !important; transform: scale(1.15); z-index: 10; }
        #robot-console { background: #1b1e23; color: #0be881; padding: 15px; border-radius: 20px; height: 160px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 0.75rem; border: 2px solid var(--accent); margin-top: 15px; }
        .bot-container { position: absolute; top: -85px; left: 50%; transform: translateX(-50%); width: 140px; pointer-events: none; z-index: 100; }
    </style>
</head>
<body data-theme="light">
<div class="layout">
    <aside>
        <div class="card"><h2 style="color:var(--accent); margin:0;">Sudoku-Grid</h2></div>
        <div class="card">
            <h3>Missions</h3>
            {% for name in ["Lvl 1 Noob (4x4)", "Lvl 2 Beginner (4x4)", "Lvl 3 Casual (9x9)", "Lvl 4 Smart (9x9)", "Lvl 5 Pro (9x9)"] %}
            <button class="btn mode-btn" onclick="loadPuzzle('{{name}}', this)">{{name}}</button>
            {% endfor %}
            <button class="btn" onclick="loadPuzzle(state.currentMode)">🔀 Shuffle Matrix</button>
            <button class="btn" onclick="toggleTheme()">🌓 Theme Mode</button>
        </div>
    </aside>

    <main class="grid-frame"><div id="grid" class="sudoku-grid"></div></main>

    <aside>
        <div class="card" style="padding-top:60px;">
            <div id="botWrapper" class="bot-container">
                <lottie-player id="botAvatar" src="https://assets10.lottiefiles.com/packages/lf20_m6cu98v2.json" speed="1" loop autoplay></lottie-player>
            </div>
            <h3>Logic Engine v11.3</h3>
            <div id="robot-console">> Omega Brain Active...</div>
            <button id="solveBtn" class="btn" onclick="runAI()" style="background:var(--accent); color:white; height:55px; margin-top:20px;">🚀 ACTIVATE AI SOLVER</button>
        </div>
    </aside>
</div>

<script>
    let state = { board: [], initial: [], isSolving: false, size: 9, currentMode: 'Lvl 1 Noob (4x4)', heat: {} };
    const synth = window.speechSynthesis;

    window.onload = () => loadPuzzle('Lvl 1 Noob (4x4)');

    // RESTORED STANDARD ROBOT VOICE
    function robotSpeak(text) {
        synth.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.pitch = 1.6; utter.rate = 1.1; 
        const voices = synth.getVoices();
        utter.voice = voices.find(v => v.name.includes('Google') || v.name.includes('English')) || voices[0];
        synth.speak(utter);
    }

    function log(msg, type = "info") {
        const c = document.getElementById('robot-console');
        const line = document.createElement('div');
        line.style.color = type === "backtrack" ? "#ffa502" : "#0be881";
        line.innerHTML = `> ${msg}`;
        c.appendChild(line);
        c.scrollTop = c.scrollHeight;
    }

    async function loadPuzzle(mode, btn) {
        if(state.isSolving) return;
        if(btn) { document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); }
        state.currentMode = mode;
        const res = await fetch('/get-puzzle', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({mode}) });
        const data = await res.json();
        state.board = data.puzzle; state.initial = JSON.parse(JSON.stringify(data.puzzle));
        state.size = data.size; state.heat = {}; renderBoard();
        robotSpeak(`Sector ${mode} shuffled. Mission ready.`);
        log(`System: Generated fresh variation for ${mode}.`);
    }

    function renderBoard(sR = -1, sC = -1) {
        const grid = document.getElementById('grid'); grid.innerHTML = '';
        grid.style.gridTemplateColumns = `repeat(${state.size}, 45px)`;
        state.board.forEach((row, r) => {
            row.forEach((val, c) => {
                const cell = document.createElement('div');
                cell.className = 'cell' + (state.initial[r][c] !== 0 ? ' initial' : '');
                if (r === sR && c === sC) cell.classList.add('peeking');
                
                // Heatmap logic
                const bts = state.heat[`${r},${c}`] || 0;
                if(bts > 0) cell.style.backgroundColor = `rgba(255, 71, 87, ${Math.min(bts/8, 0.4)})`;
                
                cell.innerText = val || '';
                grid.appendChild(cell);
            });
        });
    }

    // QUANTUM SOLVER (MRV)
    async function runAI() {
        if (state.isSolving) return;
        state.isSolving = true;
        robotSpeak("Initiating Quantum Logic. Observing search tree.");
        log("AI: Solving with Minimum Remaining Values...");
        
        const bot = document.getElementById('botWrapper');
        bot.style.transform = "translateX(-50%) translateY(15px) scale(1.1)"; // Peeking animation

        const start = Date.now();
        const success = await solve(state.board);
        const time = ((Date.now() - start) / 1000).toFixed(2);
        
        state.isSolving = false;
        bot.style.transform = "translateX(-50%)"; 
        
        if (success) { 
            renderBoard(); 
            robotSpeak("Mission success. I have achieved logic admiral rank."); 
            log(`Success in ${time}s.`); 
            confetti();
            // Mechanical Wink
            setTimeout(() => { bot.style.filter = "brightness(1.5) contrast(1.2)"; }, 200);
            setTimeout(() => { bot.style.filter = "none"; }, 600);
        }
    }

    async function solve(board) {
        let r = -1, c = -1, minOpts = state.size + 1, found = false;
        for (let i = 0; i < state.size; i++) {
            for (let j = 0; j < state.size; j++) {
                if (board[i][j] === 0) {
                    found = true;
                    let opts = 0;
                    for (let n = 1; n <= state.size; n++) if (isValid(board, i, j, n)) opts++;
                    if (opts < minOpts) { minOpts = opts; r = i; c = j; }
                }
            }
        }
        if (!found) return true;

        for (let n = 1; n <= state.size; n++) {
            if (isValid(board, r, c, n)) {
                board[r][c] = n;
                // Real-time processing log
                if (Math.random() < 0.08) { 
                    renderBoard(r, c); 
                    log(`AI Peeking: Testing ${n} at [${r},${c}]`);
                    await new Promise(res => setTimeout(res, 5)); 
                }
                if (await solve(board)) return true;
                board[r][c] = 0;
                state.heat[`${r},${c}`] = (state.heat[`${r},${c}`] || 0) + 1;
                if (Math.random() < 0.05) log(`AI Talk: Backtracking sector [${r},${c}]`, "backtrack");
            }
        }
        return false;
    }

    function isValid(b, r, c, n) {
        for (let i = 0; i < state.size; i++) if (b[r][i] === n || b[i][c] === n) return false;
        const box = state.size === 9 ? 3 : 2;
        const sR = r - (r % box), sC = c - (c % box);
        for (let i = 0; i < box; i++) for (let j = 0; j < box; j++) if (b[sR + i][sC + j] === n) return false;
        return true;
    }

    function toggleTheme() {
        document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
        log(`System: Toggled ${document.body.dataset.theme} mode.`);
    }
</script>
</body>
</html>"""
if __name__ == '__main__': app.run(debug=True)