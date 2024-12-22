import random

class Game:
    def __init__(self, word_count=25, custom_words=None):
        self.word_count = word_count
        if custom_words:
            # Combine custom words with default words if needed
            default_words = self.generate_default_words()
            needed_words = word_count - len(custom_words)
            if needed_words > 0:
                self.words = custom_words + random.sample(default_words, needed_words)
            else:
                self.words = custom_words[:word_count]
        else:
            self.words = self.generate_default_words()
        
        self.teams = self.assign_teams()
        self.revealed = [False] * word_count
        self.current_team = 'red'
        self.team_members = {
            'red': {'operatives': set(), 'spymaster': None},
            'blue': {'operatives': set(), 'spymaster': None}
        }
        # Add score tracking
        self.scores = {
            'red': 0,
            'blue': 0
        }
        # Count initial cards for each team
        self.remaining_cards = {
            'red': len([t for t in self.teams if t == 'red']),
            'blue': len([t for t in self.teams if t == 'blue'])
        }
        
        # Add hint tracking
        self.current_hint = None
        self.current_hint_count = 0
        self.guesses_remaining = 0
        self.game_phase = 'giving_hint'  # ['giving_hint', 'guessing']
        
    def generate_default_words(self):
        # This is a small sample word list - you should expand this
        word_list = [
            "APPLE", "BANK", "CARD", "DOG", "EAGLE", "FIRE", "GOLD", 
            "HOUSE", "ICE", "JUMP", "KING", "LION", "MOON", "NIGHT",
            "ORANGE", "PAPER", "QUEEN", "RAIN", "SNOW", "TIME",
            "UMBRELLA", "VOICE", "WATER", "XRAY", "YEAR", "ZEBRA",
            "BEACH", "CLOUD", "DANCE", "EARTH"
        ]
        return random.sample(word_list, self.word_count)
    
    def assign_teams(self):
        teams = ['red'] * 8 + ['blue'] * 8 + ['neutral'] * (self.word_count - 17)
        teams[0] = 'assassin'  # One assassin card
        random.shuffle(teams)
        return teams
    
    def give_hint(self, hint, count):
        """Spymaster gives a hint and number of related words"""
        if self.game_phase != 'giving_hint':
            return {'success': False, 'message': 'Not the hint-giving phase'}
            
        self.current_hint = hint
        self.current_hint_count = count
        self.guesses_remaining = count + 1  # Allow one extra guess
        self.game_phase = 'guessing'
        
        return {
            'success': True,
            'hint': hint,
            'count': count
        }
    
    def select_word(self, index, team):
        """Modified to handle the guessing phase logic"""
        if self.game_phase != 'guessing':
            return {'success': False, 'message': 'Not the guessing phase'}
            
        if not self.revealed[index]:
            self.revealed[index] = True
            actual_team = self.teams[index]
            
            # Update scores and remaining cards
            if actual_team in ['red', 'blue']:
                self.scores[actual_team] += 1
                self.remaining_cards[actual_team] -= 1
            
            # Decrement remaining guesses
            self.guesses_remaining -= 1
            
            # Check win conditions
            game_over = False
            winner = None
            
            # Check if assassin was found
            if actual_team == 'assassin':
                game_over = True
                winner = 'blue' if team == 'red' else 'red'
            
            # Check if a team found all their words
            elif self.remaining_cards['red'] == 0:
                game_over = True
                winner = 'red'
            elif self.remaining_cards['blue'] == 0:
                game_over = True
                winner = 'blue'
            
            # End turn conditions
            end_turn = False
            
            # Wrong color or neutral ends turn
            if actual_team != team:
                end_turn = True
            
            # No more guesses ends turn
            if self.guesses_remaining <= 0:
                end_turn = True
            
            if end_turn and not game_over:
                self.current_team = 'blue' if team == 'red' else 'red'
                self.game_phase = 'giving_hint'
                self.current_hint = None
                self.current_hint_count = 0
            
            return {
                'success': True,
                'team': actual_team,
                'game_over': game_over,
                'winner': winner,
                'end_turn': end_turn
            }
        return {'success': False, 'message': 'Word already revealed'}
    
    def get_state(self):
        # Check if assassin card was revealed
        assassin_index = self.teams.index('assassin')
        assassin_revealed = self.revealed[assassin_index]
        assassin_revealed_by = None
        
        # If assassin was revealed, determine which team revealed it
        if assassin_revealed:
            # Find the last team that played before the current team
            assassin_revealed_by = 'blue' if self.current_team == 'red' else 'red'
        
        game_over = (self.remaining_cards['red'] == 0 or 
                     self.remaining_cards['blue'] == 0 or 
                     assassin_revealed)
        
        winner = None
        if game_over:
            if assassin_revealed:
                # If assassin was revealed, the other team wins
                winner = 'blue' if assassin_revealed_by == 'red' else 'red'
            else:
                # Otherwise, winner is the team that found all their words
                winner = 'red' if self.remaining_cards['red'] == 0 else 'blue'
        
        # Create the base state dictionary
        state = {
            'words': self.words,
            'teams': self.teams,
            'revealed': self.revealed,
            'current_team': self.current_team,
            'scores': self.scores,
            'remaining_cards': self.remaining_cards,
            'game_over': game_over,
            'winner': winner,
            # Add hint-related state
            'current_hint': self.current_hint,
            'current_hint_count': self.current_hint_count,
            'guesses_remaining': self.guesses_remaining,
            'game_phase': self.game_phase
        }
        
        return state
    
    def add_player_to_team(self, player_id, team, is_spymaster=False):
        self.remove_player_from_teams(player_id)
        
        if is_spymaster:
            if self.team_members[team]['spymaster'] is None:
                self.team_members[team]['spymaster'] = player_id
                return True
            return False  # Spymaster role already taken
        else:
            self.team_members[team]['operatives'].add(player_id)
            return True
    
    def remove_player_from_teams(self, player_id):
        for team in ['red', 'blue']:
            if self.team_members[team]['spymaster'] == player_id:
                self.team_members[team]['spymaster'] = None
            self.team_members[team]['operatives'].discard(player_id)
