from flask import Flask, render_template_string, jsonify, request
import random
import math
import copy

app = Flask(__name__)

# ==========================================
#              SUDOKU LOGIC
# ==========================================
BLANK = 0

def get_box_dims(size):
    if size == 9: return 3, 3
    if size == 6: return 2, 3
    if size == 4: return 2, 2
    root = int(math.sqrt(size))
    return root, root

def is_valid(board, row, col, num, size):
    box_h, box_w = get_box_dims(size)
    for i in range(size):
        if board[row][i] == num: return False
        if board[i][col] == num: return False
    start_row = row - (row % box_h)
    start_col = col - (col % box_w)
    for i in range(box_h):
        for j in range(box_w):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_board(board, size):
    for r in range(size):
        for c in range(size):
            if board[r][c] == BLANK:
                nums = list(range(1, size + 1))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, r, c, num, size):
                        board[r][c] = num
                        if solve_board(board, size): return True
                        board[r][c] = BLANK
                return False
    return True

def generate_board(size):
    board = [[BLANK for _ in range(size)] for _ in range(size)]
    solve_board(board, size)
    return board

def create_puzzle(size, difficulty):
    solution = generate_board(size)
    puzzle = copy.deepcopy(solution)
    total_cells = size * size
    
    # Difficulty logic
    if size == 4: attempts = 2 + int(difficulty * 0.5)
    elif size == 6: attempts = int(total_cells * (0.3 + (difficulty * 0.05)))
    else: attempts = int(total_cells * (0.35 + (difficulty * 0.04))) 

    holes = 0
    while holes < attempts:
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        if puzzle[r][c] != BLANK:
            puzzle[r][c] = BLANK
            holes += 1
            
    return {"solution": solution, "puzzle": puzzle}

# ==========================================
#              FLASK ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/new-game', methods=['POST'])
def new_game():
    data = request.json
    size = int(data.get('size', 4))
    diff = int(data.get('difficulty', 1))
    return jsonify(create_puzzle(size, diff))

# ==========================================
#        FRONTEND (HTML/CSS/JS)
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sudoku-Grid</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {
            --bg: #e6e6fa; --text: #483d8b; --text-light: #7b68ee;
            --accent: #9370db; --danger: #ff6b6b; --success: #32cd32;
            --shadow-light: #ffffff; --shadow-dark: #b8b8d9;
            --line: #a4a4c1;
        }
        body { 
            background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; 
            margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; 
            overflow-y: auto; user-select: none;
        }
        
        /* LAYOUT */
        .layout { display: flex; gap: 35px; padding: 20px; width: 100%; max-width: 1400px; height: 95vh; box-sizing: border-box; }
        .sidebar { width: 280px; display: flex; flex-direction: column; gap: 20px; }
        .center { flex: 1; display: flex; flex-direction: column; align-items: center; padding-top: 10px; }
        
        /* COMPONENTS */
        .card { 
            padding: 20px; border-radius: 25px; background: var(--bg); 
            box-shadow: inset 6px 6px 12px var(--shadow-dark), inset -6px -6px 12px var(--shadow-light); 
            display: flex; flex-direction: column; 
        }
        .scrollable { flex: 1; overflow-y: auto; }
        
        .brand { text-align: center; font-size: 2.8rem; font-weight: 800; margin: 0; }
        .accent { color: var(--accent); }

        .btn { 
            border: none; background: var(--bg); color: var(--text); padding: 12px; border-radius: 50px; 
            font-weight: 700; cursor: pointer; width: 100%; margin-bottom: 8px;
            box-shadow: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light); 
            transition: all 0.1s ease; text-align: center;
        }
        .btn:active, .btn.active { 
            box-shadow: inset 4px 4px 8px var(--shadow-dark), inset -4px -4px 8px var(--shadow-light); 
            color: var(--accent); transform: translateY(1px); 
        }
        .btn.primary { color: var(--accent); font-size: 1.1rem; }
        .btn.danger { color: var(--danger); }
        .btn.small { width: auto; flex: 1; font-size: 0.9rem; }

        /* GRID */
        .grid-frame { 
            padding: 30px; border-radius: 40px; background: var(--bg); 
            box-shadow: 25px 25px 50px var(--shadow-dark), -25px -25px 50px var(--shadow-light); 
            margin-bottom: 25px; position: relative; 
        }
        .sudoku-grid { display: grid; gap: 8px; transition: filter 0.3s; }
        
        /* CELL STYLES */
        .cell { 
            width: 50px; height: 50px; border-radius: 12px; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 1.6rem; font-weight: 700; color: var(--text); 
            box-shadow: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light); 
            cursor: pointer; transition: transform 0.1s; position: relative;
        }
        .cell:hover { transform: scale(0.95); }
        .cell.selected { box-shadow: inset 3px 3px 6px var(--shadow-dark), inset -3px -3px 6px var(--shadow-light); color: var(--accent); }
        .cell.initial { color: var(--accent); }
        .cell.error { color: var(--danger); animation: shake 0.4s; }
        
        /* NOTES GRID */
        .note-container {
            display: grid; grid-template-columns: repeat(3, 1fr);
            width: 100%; height: 100%; pointer-events: none;
        }
        .note-num { font-size: 0.6rem; color: #7b68ee; display: flex; align-items: center; justify-content: center; font-weight: 600; }

        /* REGION LINES */
        .cell.region-right { margin-right: 12px; }
        .cell.region-right::after { content: ''; position: absolute; right: -9px; top: 5px; bottom: 5px; width: 4px; background: rgba(0,0,0,0.1); border-radius: 2px; }
        .cell.region-bottom { margin-bottom: 12px; }
        .cell.region-bottom::before { content: ''; position: absolute; bottom: -9px; left: 5px; right: 5px; height: 4px; background: rgba(0,0,0,0.1); border-radius: 2px; }

        /* STATIC NUMPAD */
        .numpad-container { display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; width: 100%; max-width: 400px; margin-bottom: 15px; }
        .numpad-btn {
            width: 45px; height: 45px; border-radius: 12px; border: none;
            background: var(--bg); color: var(--text); font-size: 1.2rem; font-weight: bold;
            box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light);
            cursor: pointer; transition: transform 0.1s;
        }
        .numpad-btn:active { box-shadow: inset 3px 3px 6px var(--shadow-dark), inset -3px -3px 6px var(--shadow-light); transform: translateY(2px); }
        .numpad-btn.del { color: var(--danger); }

        /* OVERLAYS & STATS */
        .overlay-screen { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(230, 230, 250, 0.9); z-index: 50; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            border-radius: 40px; backdrop-filter: blur(5px); transition: opacity 0.5s;
        }
        .blurred { filter: blur(8px); }
        .hidden { display: none !important; }

        .stats-bar { display: flex; gap: 20px; margin-bottom: 20px; width: 100%; justify-content: center; }
        .stat-pill { min-width: 90px; padding: 0 20px; height: 80px; border-radius: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 5px 5px 10px var(--shadow-dark), inset -5px -5px 10px var(--shadow-light); }
        .stat-pill b { font-size: 1.2rem; }
        
        .game-actions, .toggle-group, .controls-row { display: flex; gap: 10px; margin-bottom: 10px; }
        .share-row { display: flex; gap: 10px; }
        .rules-list { padding-left: 20px; font-size: 0.85rem; line-height: 1.5; color: var(--text); text-align: left; }
        
        @keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
    </style>
</head>
<body>

<div class="layout">
    <div class="sidebar">
        <h1 class="brand">Sudoku<span class="accent">.luv</span></h1>
        
        <div class="card scrollable">
            <h3>Difficulty</h3>
            <div id="level-list"></div>
        </div>

        <div class="card">
            <h3>Grid Size</h3>
            <div class="toggle-group">
                <button class="btn" id="btn-4" onclick="initGame(4, state.difficulty)">4x4</button>
                <button class="btn" id="btn-6" onclick="initGame(6, state.difficulty)">6x6</button>
                <button class="btn" id="btn-9" onclick="initGame(9, state.difficulty)">9x9</button>
            </div>
            <button class="btn" id="sound-btn" style="margin-top:10px;" onclick="toggleSound()">🔊 Sound ON</button>
        </div>
        <button class="btn" onclick="captureBoard()">📸 Capture</button>
    </div>

    <div class="center">
        <div class="stats-bar">
            <div class="stat-pill"><small>TIME</small><b id="timer">02:00</b></div>
            <div class="stat-pill"><small>ERRORS</small><b id="errors" style="color:var(--danger)">0</b></div>
            <div class="stat-pill"><small>RANK</small><b id="rank-disp">Noob</b></div>
        </div>

        <div class="game-actions">
            <button class="btn primary" onclick="initGame(state.size, state.difficulty)">🔄 New Game</button>
            <button class="btn" id="pause-btn" onclick="togglePause()">⏸️ Pause</button>
            <button class="btn danger" onclick="endGame()">🏳️ End</button>
        </div>

        <div class="grid-frame" id="capture-area">
            <div id="start-overlay" class="overlay-screen">
                <h2>Ready?</h2>
                <button class="btn primary" style="width:150px; font-size:1.2rem;" onclick="startGame()">▶️ Start</button>
            </div>
            <div id="pause-overlay" class="overlay-screen hidden">
                <h2>Paused</h2>
                <button class="btn" style="width:150px;" onclick="togglePause()">▶️ Resume</button>
            </div>
            <div id="win-overlay" class="overlay-screen hidden">
                <h1 style="color:var(--success); font-size:3rem;">Solved! 🎉</h1>
                <p>Level Up in 3s...</p>
            </div>
            <div id="grid" class="sudoku-grid blur-target"></div>
        </div>

        <div class="numpad-container" id="static-numpad"></div>

        <div class="controls-row">
            <button class="btn small" onclick="undo()">↩ Undo</button>
            <button class="btn small" id="note-btn" onclick="toggleNotes()">✎ Notes (OFF)</button>
            <button class="btn small" onclick="useHint()">💡 Hint</button>
        </div>
        
        <div style="width: 340px; margin-top: 15px;">
            <button id="check-btn" class="btn primary" onclick="checkBoard()">🔍 Check Board (-10s)</button>
            <button id="next-btn" class="btn success hidden" onclick="nextLevel()">⏩ Next Level</button>
        </div>
    </div>

    <div class="sidebar">
        <div class="card">
            <h3>Rules & Tips</h3>
            <ul class="rules-list">
                <li><strong>Auto-Check:</strong> The game checks for a WIN automatically.</li>
                <li><strong>Manual Check:</strong> Use "Check Board" to verify your current inputs (Cost: 10s).</li>
                <li><strong>Notes:</strong> Toggle Notes to mark possibilities.</li>
                <li><strong>Level Up:</strong> Completing a grid moves you to the next difficulty.</li>
            </ul>
        </div>
        <div class="card share-row">
            <button class="btn" onclick="alert('❤️ Thank you for playing!')">❤️ Like</button>
            <button class="btn" onclick="captureBoard()">🚀 Share</button>
        </div>
    </div>
</div>

<script>
    let state = {
        size: 4, difficulty: 1,
        board: [], initial: [], solution: [], 
        notes: [], history: [],
        timer: 120, interval: null,
        selected: null, mistakes: 0, 
        notesMode: false,
        sound: true, gameOver: false, isPlaying: false, isPaused: false
    };

    const LEVELS = ["Noob", "Beginner", "Casual", "Smart", "Pro", "Ninja", "Master", "Genius", "Legend", "God Mode"];
    const TIME_LIMITS = [120, 150, 240, 330, 420, 510, 600, 720, 810, 900];
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioCtx();

    function playTone(type) {
        if(!state.sound) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        const now = ctx.currentTime;
        if(type==='pop'){ osc.frequency.setValueAtTime(400,now); osc.frequency.linearRampToValueAtTime(600,now+0.1); gain.gain.setValueAtTime(0.1,now); gain.gain.linearRampToValueAtTime(0,now+0.1); osc.start(now); osc.stop(now+0.1); }
        else if(type==='err'){ osc.type='sawtooth'; osc.frequency.setValueAtTime(150,now); gain.gain.setValueAtTime(0.1,now); gain.gain.linearRampToValueAtTime(0,now+0.3); osc.start(now); osc.stop(now+0.3); }
        else if(type==='win'){ osc.type='triangle'; osc.frequency.setValueAtTime(500,now); osc.frequency.linearRampToValueAtTime(800,now+0.5); gain.gain.setValueAtTime(0.2,now); gain.gain.linearRampToValueAtTime(0,now+1); osc.start(now); osc.stop(now+1); }
    }

    window.onload = () => {
        renderLevelList();
        initGame(4, 1);
    };

    function renderLevelList() {
        const list = document.getElementById('level-list');
        list.innerHTML = '';
        LEVELS.forEach((name, i) => {
            const btn = document.createElement('button');
            btn.className = `btn level-item`;
            btn.innerHTML = `<span>Lvl ${i+1}</span> <span>${name}</span>`;
            btn.onclick = () => initGame(state.size, i+1);
            list.appendChild(btn);
        });
    }

    async function initGame(size, diff) {
        if(!diff || diff < 1) diff = 1;
        if(!size) size = 4;
        
        state.size = size; 
        state.difficulty = diff;
        state.mistakes = 0; state.gameOver = false; state.selected = null; state.history = [];
        state.isPlaying = false; state.isPaused = false; state.notesMode = false;
        
        state.notes = Array.from({length: size}, () => Array.from({length: size}, () => []));
        state.timer = TIME_LIMITS[diff-1] || 120;

        document.getElementById('rank-disp').innerText = LEVELS[diff-1] || "Noob";
        document.getElementById('errors').innerText = 0;
        document.getElementById('note-btn').innerText = "✎ Notes (OFF)";
        document.getElementById('note-btn').classList.remove('active');
        updateTimerDisplay(); 
        
        document.getElementById('start-overlay').classList.remove('hidden'); 
        document.getElementById('pause-overlay').classList.add('hidden');
        document.getElementById('win-overlay').classList.add('hidden');
        document.getElementById('grid').classList.add('blurred');

        document.getElementById('btn-4').classList.toggle('active', size===4);
        document.getElementById('btn-6').classList.toggle('active', size===6);
        document.getElementById('btn-9').classList.toggle('active', size===9);

        setupNumpad(size);

        try {
            const res = await fetch('/new-game', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({size, difficulty: diff})
            });
            const data = await res.json();
            state.board = data.puzzle;
            state.initial = JSON.parse(JSON.stringify(data.puzzle));
            state.solution = data.solution;
            renderBoard();
            clearInterval(state.interval);
        } catch(e) { console.error(e); }
    }

    function setupNumpad(size) {
        const pad = document.getElementById('static-numpad');
        pad.innerHTML = '';
        for(let i=1; i<=size; i++) {
            const btn = document.createElement('button');
            btn.className = 'numpad-btn';
            btn.innerText = i;
            btn.onclick = () => fillCell(i);
            pad.appendChild(btn);
        }
        const del = document.createElement('button');
        del.className = 'numpad-btn del';
        del.innerText = '⌫';
        del.onclick = () => fillCell(0);
        pad.appendChild(del);
    }

    function startGame() {
        state.isPlaying = true;
        document.getElementById('start-overlay').classList.add('hidden');
        document.getElementById('grid').classList.remove('blurred');
        playTone('pop');
        renderBoard();
        runTimer();
    }

    function runTimer() {
        clearInterval(state.interval);
        updateTimerDisplay();
        state.interval = setInterval(() => {
            if(state.timer > 0 && !state.gameOver && !state.isPaused) {
                state.timer--;
                updateTimerDisplay();
            } else if(state.timer <= 0) {
                state.gameOver = true;
                clearInterval(state.interval);
                alert("⏳ Time's Up! Restarting game...");
                initGame(state.size, state.difficulty);
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        let t = state.timer;
        if (isNaN(t) || t < 0) t = 0;
        const m = Math.floor(t/60).toString().padStart(2,'0');
        const s = (t%60).toString().padStart(2,'0');
        document.getElementById('timer').innerText = `${m}:${s}`;
    }

    function renderBoard() {
        const grid = document.getElementById('grid');
        grid.innerHTML = '';
        grid.style.gridTemplateColumns = `repeat(${state.size}, 1fr)`;
        
        let boxW = (state.size === 9) ? 3 : (state.size === 6 ? 3 : 2);
        let boxH = (state.size === 9) ? 3 : (state.size === 6 ? 2 : 2);

        state.board.forEach((row, r) => {
            row.forEach((val, c) => {
                const cell = document.createElement('div');
                cell.className = 'cell';
                
                if((c + 1) % boxW === 0 && c !== state.size - 1) cell.classList.add('region-right');
                if((r + 1) % boxH === 0 && r !== state.size - 1) cell.classList.add('region-bottom');
                if(state.initial[r][c] !== 0) cell.classList.add('initial');
                if(state.selected && state.selected.r === r && state.selected.c === c) cell.classList.add('selected');
                
                if (!state.isPlaying || state.isPaused) {
                    cell.innerText = "";
                } else if (val !== 0) {
                    cell.innerText = val;
                } else {
                    cell.innerHTML = ""; 
                    const noteDiv = document.createElement('div');
                    noteDiv.className = 'note-container';
                    for(let k=1; k<=9; k++) {
                        const span = document.createElement('span');
                        span.className = 'note-num';
                        if(state.notes[r][c] && state.notes[r][c].includes(k)) {
                            span.innerText = k;
                        }
                        noteDiv.appendChild(span);
                    }
                    cell.appendChild(noteDiv);
                }
                
                cell.onclick = (e) => {
                    if(state.gameOver || !state.isPlaying || state.isPaused) return;
                    selectCell(r, c);
                };
                grid.appendChild(cell);
            });
        });
    }

    function selectCell(r, c) {
        state.selected = {r, c};
        renderBoard();
    }

    function toggleNotes() {
        state.notesMode = !state.notesMode;
        const btn = document.getElementById('note-btn');
        if(state.notesMode) {
            btn.classList.add('active');
            btn.innerText = "✎ Notes (ON)";
        } else {
            btn.classList.remove('active');
            btn.innerText = "✎ Notes (OFF)";
        }
    }

    function fillCell(num) {
        if(!state.selected) return;
        const {r, c} = state.selected;
        if(state.initial[r][c] !== 0) return; 

        state.history.push({
            board: JSON.parse(JSON.stringify(state.board)),
            notes: JSON.parse(JSON.stringify(state.notes))
        });
        if(state.history.length > 20) state.history.shift();

        if (state.notesMode) {
            if (num === 0) state.notes[r][c] = [];
            else {
                if (state.notes[r][c].includes(num)) state.notes[r][c] = state.notes[r][c].filter(n => n !== num);
                else state.notes[r][c].push(num);
            }
        } else {
            state.board[r][c] = num;
            if (num !== 0) state.notes[r][c] = [];
            
            // Note: We are NOT marking errors instantly on typing anymore (per your button request)
            // But we play a neutral pop.
            playTone('pop');
            
            // Only check for WIN automatically
            checkWin();
        }
        renderBoard();
    }

    function checkWin() {
        let isFull = true;
        for(let r=0; r<state.size; r++){
            for(let c=0; c<state.size; c++){
                if(state.board[r][c] === 0 || state.board[r][c] !== state.solution[r][c]){
                    isFull = false;
                    break;
                }
            }
        }
        
        if(isFull) {
            state.gameOver = true;
            clearInterval(state.interval);
            playTone('win');
            document.getElementById('win-overlay').classList.remove('hidden');
            confetti({ particleCount: 200, spread: 70, origin: { y: 0.6 } });
            setTimeout(() => {
                let nextDiff = state.difficulty + 1;
                if(nextDiff > 10) nextDiff = 1; 
                initGame(state.size, nextDiff);
            }, 3000);
        }
    }

    // --- NEW: MANUAL ERROR CHECKER BUTTON LOGIC ---
    function checkBoard() {
        if(state.gameOver || !state.isPlaying) return;
        
        // PENALTY: Remove 10 seconds
        state.timer = Math.max(0, state.timer - 10);
        updateTimerDisplay();
        
        let errs = 0;
        const cells = document.querySelectorAll('.cell');
        let idx = 0;
        
        for(let r=0; r<state.size; r++) {
            for(let c=0; c<state.size; c++) {
                const val = state.board[r][c];
                // Check if filled and incorrect
                if(val !== 0 && val !== state.solution[r][c]) {
                    cells[idx].classList.add('error'); // Add visual class
                    errs++;
                }
                idx++;
            }
        }
        
        if(errs > 0) {
            playTone('err');
            state.mistakes += errs;
            document.getElementById('errors').innerText = state.mistakes;
        } else {
            playTone('pop'); // Success sound if grid is clean
        }
    }

    function togglePause() {
        if(!state.isPlaying || state.gameOver) return;
        state.isPaused = !state.isPaused;
        const btn = document.getElementById('pause-btn');
        if(state.isPaused) {
            document.getElementById('pause-overlay').classList.remove('hidden');
            document.getElementById('grid').classList.add('blurred');
            btn.innerText = "▶️ Resume";
            clearInterval(state.interval);
        } else {
            document.getElementById('pause-overlay').classList.add('hidden');
            document.getElementById('grid').classList.remove('blurred');
            btn.innerText = "⏸️ Pause";
            runTimer();
        }
    }

    function endGame() {
        if(!state.isPlaying) return;
        if(!confirm("Give up?")) return;
        state.gameOver = true;
        clearInterval(state.interval);
        state.board = JSON.parse(JSON.stringify(state.solution));
        renderBoard();
        alert("Game Over!");
    }

    function undo() { 
        if(state.history.length > 0) { 
            const prev = state.history.pop(); 
            state.board = prev.board;
            state.notes = prev.notes;
            renderBoard(); 
            playTone('pop'); 
        } 
    }
    
    function useHint() { 
        if(!state.isPlaying || state.isPaused) return;
        state.timer = Math.max(0, state.timer - 5);
        let empty = [];
        for(let r=0; r<state.size; r++) for(let c=0; c<state.size; c++) if(state.board[r][c]===0) empty.push({r,c});
        if(empty.length>0) {
            const h = empty[Math.floor(Math.random()*empty.length)];
            state.board[h.r][h.c] = state.solution[h.r][h.c];
            state.notes[h.r][h.c] = [];
            renderBoard(); playTone('pop');
            checkWin(); 
        }
    }
    function toggleSound() { state.sound = !state.sound; document.getElementById('sound-btn').innerText = state.sound ? "🔊 Sound ON" : "🔇 Sound OFF"; }
    function captureBoard() { const element = document.getElementById('capture-area'); html2canvas(element).then(canvas => { const link = document.createElement('a'); link.download = `Sudoku.png`; link.href = canvas.toDataURL(); link.click(); }); }
    
    window.addEventListener('keydown', (e) => {
        if(state.gameOver || !state.isPlaying || state.isPaused || !state.selected) return;
        const {r, c} = state.selected;
        if(e.key === 'ArrowUp') selectCell(Math.max(0, r-1), c);
        else if(e.key === 'ArrowDown') selectCell(Math.min(state.size-1, r+1), c);
        else if(e.key === 'ArrowLeft') selectCell(r, Math.max(0, c-1));
        else if(e.key === 'ArrowRight') selectCell(r, Math.min(state.size-1, c+1));
        const num = parseInt(e.key);
        if(!isNaN(num) && num >= 1 && num <= state.size) fillCell(num);
        if(e.key === 'Backspace' || e.key === 'Delete') fillCell(0);
        if(e.key === 'n' || e.key === 'N') toggleNotes();
    });
</script>
</body>
</html>
"""
0
if __name__ == '__main__':
    print("✅ Sudoku Ultimate Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)