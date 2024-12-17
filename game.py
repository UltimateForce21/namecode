import random

class Game:
    def __init__(self, word_count=25):
        self.word_count = word_count
        self.words = self.generate_words()
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
        
    def generate_words(self):
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
    
    def select_word(self, index, team):
        if not self.revealed[index]:
            self.revealed[index] = True
            actual_team = self.teams[index]
            
            # Update scores when a card is revealed
            if actual_team in ['red', 'blue']:
                self.scores[actual_team] += 1
                self.remaining_cards[actual_team] -= 1
            
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
            
            # Switch turns if the team picks wrong color or neutral
            if actual_team != team and not game_over:
                self.current_team = 'blue' if team == 'red' else 'red'
            
            return {
                'success': True,
                'team': actual_team,
                'game_over': game_over,
                'winner': winner
            }
        return {'success': False}
    
    def get_state(self):
        return {
            'words': self.words,
            'teams': self.teams,
            'revealed': self.revealed,
            'current_team': self.current_team,
            'scores': self.scores,
            'remaining_cards': self.remaining_cards,
            'game_over': self.remaining_cards['red'] == 0 or self.remaining_cards['blue'] == 0,
            'winner': 'red' if self.remaining_cards['red'] == 0 else 'blue' if self.remaining_cards['blue'] == 0 else None
        }
    
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
