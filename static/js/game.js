let socket;
let isSpymaster = false;
let currentTeam = null;

async function createGame() {
    const totalWordCount = document.getElementById('word-count').value;
    const theme = document.getElementById('theme').value;
    const themeWordCount = document.getElementById('theme-word-count').value;
    const loadingBar = document.getElementById('loading-bar');
    const progressBar = loadingBar.querySelector('.progress');
    
    if (theme) {
        if (themeWordCount > totalWordCount) {
            alert('Theme word count cannot be greater than total word count');
            return;
        }
        
        try {
            // Show loading bar
            loadingBar.style.display = 'block';
            progressBar.style.width = '30%';
            
            // Generate theme-based words
            const response = await fetch('/generate_theme_words', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme: theme,
                    word_count: parseInt(themeWordCount)
                })
            });
            
            progressBar.style.width = '60%';
            
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error);
            }
            
            progressBar.style.width = '90%';
            
            // Create game with custom words
            const gameResponse = await fetch('/create_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `word_count=${totalWordCount}&custom_words=${data.words.join(',')}`
            });
            
            progressBar.style.width = '100%';
            
            const gameData = await gameResponse.json();
            window.location.href = `/join_game/${gameData.game_id}`;
            
        } catch (error) {
            alert('Error generating theme words: ' + error.message);
            loadingBar.style.display = 'none';
        }
    } else {
        // Create game with default words
        const response = await fetch('/create_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `word_count=${totalWordCount}`
        });
        
        const data = await response.json();
        window.location.href = `/join_game/${data.game_id}`;
    }
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