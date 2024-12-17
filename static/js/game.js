let socket;
let isSpymaster = false;
let currentTeam = null;

function createGame() {
    const wordCount = document.getElementById('word-count').value;
    fetch('/create_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `word_count=${wordCount}`
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = `/join_game/${data.game_id}`;

    
    });
}

function joinGame() {
    const gameId = document.getElementById('game-id').value.toUpperCase();
    window.location.href = `/join_game/${gameId}`;
}

function initializeGame() {
    socket = io();
    const gameId = window.location.pathname.split('/').pop();
    
    socket.on('connect', () => {
        socket.emit('join', {game_id: gameId});
    });
    
    socket.on('update_game_state', updateGameState);
}

function updateGameState(state) {
    const board = document.getElementById('game-board');
    board.innerHTML = '';
    
    state.words.forEach((word, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.textContent = word;
        
        if (state.revealed[index]) {
            card.classList.add('revealed', state.teams[index]);
        } else if (isSpymaster) {
            card.classList.add(state.teams[index]);
        }
        
        // Disable card clicks if game is over
        if (!state.game_over) {
            card.onclick = () => selectWord(index);
        }
        board.appendChild(card);
    });
    
    // Update scores and remaining cards
    document.getElementById('red-score').textContent = state.scores.red;
    document.getElementById('blue-score').textContent = state.scores.blue;
    document.getElementById('red-remaining').textContent = state.remaining_cards.red;
    document.getElementById('blue-remaining').textContent = state.remaining_cards.blue;
    
    // Update current team or show winner
    const currentTeamDiv = document.getElementById('current-team');
    if (state.game_over && state.winner) {
        currentTeamDiv.textContent = `${state.winner.toUpperCase()} TEAM WINS!`;
        currentTeamDiv.className = `current-team ${state.winner} winner`;
        // Disable team joining and role switching when game is over
        document.querySelectorAll('.controls button').forEach(btn => {
            btn.disabled = true;
        });
    } else {
        currentTeamDiv.textContent = `${state.current_team.toUpperCase()} TEAM'S TURN`;
        currentTeamDiv.className = `current-team ${state.current_team}`;
    }
}

function joinTeam(team) {
    currentTeam = team;
    const gameId = window.location.pathname.split('/').pop();
    socket.emit('join_team', {
        game_id: gameId,
        team: team
    });
    
    // Update UI to show current team
    document.querySelectorAll('.controls button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`button[onclick="joinTeam('${team}')"]`).classList.add('active');
}

function selectWord(index) {
    if (!currentTeam) {
        alert('Please join a team first!');
        return;
    }
    
    const gameId = window.location.pathname.split('/').pop();
    socket.emit('select_word', {
        game_id: gameId,
        word_index: index,
        team: currentTeam
    });
}

function toggleRole() {
    if (!currentTeam) {
        alert('Please join a team first!');
        return;
    }
    isSpymaster = !isSpymaster;
    
    // Update UI to show spymaster status
    const toggleBtn = document.querySelector('button[onclick="toggleRole()"]');
    toggleBtn.textContent = isSpymaster ? 'Switch to Operative' : 'Switch to Spymaster';
    toggleBtn.classList.toggle('active');
    
    // Request updated game state to show/hide team colors
    const gameId = window.location.pathname.split('/').pop();
    socket.emit('get_game_state', { game_id: gameId });
}

// Initialize game when on game page
if (window.location.pathname.includes('/join_game/')) {
    document.addEventListener('DOMContentLoaded', initializeGame);
} 