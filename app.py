from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from game import Game
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Store active games
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_game', methods=['POST'])
def create_game():
    game_id = generate_game_id()
    word_count = int(request.form.get('word_count', 25))  # Default to 25 words
    games[game_id] = Game(word_count)
    return jsonify({'game_id': game_id})

@app.route('/join_game/<game_id>')
def join_game(game_id):
    if game_id not in games:
        return "Game not found", 404
    return render_template('game.html', game_id=game_id)

@socketio.on('join')
def on_join(data):
    game_id = data['game_id']
    room = data['game_id']
    join_room(room)
    emit('update_game_state', games[game_id].get_state(), room=room)

@socketio.on('select_word')
def on_select_word(data):
    game_id = data['game_id']
    word_index = data['word_index']
    team = data['team']
    
    game = games[game_id]
    result = game.select_word(word_index, team)
    emit('update_game_state', game.get_state(), room=game_id)

@socketio.on('join_team')
def on_join_team(data):
    game_id = data['game_id']
    team = data['team']
    
    if game_id in games:
        # You might want to store player team information in the game state
        # For now, we'll just broadcast the team change
        emit('player_team_update', {
            'team': team
        }, room=game_id)

@socketio.on('get_game_state')
def on_get_game_state(data):
    game_id = data['game_id']
    if game_id in games:
        emit('update_game_state', games[game_id].get_state(), room=game_id)

def generate_game_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 