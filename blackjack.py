CARD_VALUES = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10,'A':11}
import random

class RandomCard(object):
    def __init__(self):
        self.type = list(CARD_VALUES.keys())[random.randint(0,len(CARD_VALUES)-1)]
        self.value = CARD_VALUES[self.type]
        
    def __str__(self):
        return self.type+':'+str(self.value)

class Hand(object):
    def __init__(self, initial_cards=0):
        self.cards = []
        self.score = 0
        
        self.deal_card(initial_cards)      
    
    def get_score(self):
        return sum([card.value for card in self.cards])
    
    def deal_card(self, num_cards=1):
        
        for i in range(num_cards):
            self.cards.append(RandomCard())
            self.score = self.get_score()

    def is_bust(self):
        return self.score > 21
    
    def possible_moves(self):
        #if self.score < 21:
        #    return ['hit','stand']
        #else:
        #    return ['stand']
        return ['hit','stand']
        
    def __str__(self):
        hand_string = ''
        for card in self.cards:
            hand_string += card.type+'-'
        hand_string = hand_string[:-1]
        hand_string += ' : '+ str(self.get_score())
        return hand_string
    
    
class BlackjackGame(object):
    def __init__(self):
        self.turn='player'
        self.winner = None
        self.over = False
        self.player_hand = Hand(2)        
        self.dealer_hand = Hand(2)
        
        self.game_state = (self.player_hand.get_score(),self.dealer_hand.cards[0].value)
        
    def update_game_state(self):
        self.game_state = (self.player_hand.get_score(),self.dealer_hand.cards[0].value)
        
        
    def player_allowed_moves(self):
        return self.player_hand.possible_moves()
    
    def player_move(self, move):
        if move =='hit':
            self.player_hand.deal_card()
            self.update_game_state()
        else:
            self.turn='dealer'
    
    def dealer_move(self):
        if self.dealer_hand.get_score() < 17:
            self.dealer_hand.deal_card()
            self.update_game_state()
        else:
            self.turn = None
            self.over = True

class DumbAgent(object):
    def __init__(self, money=0):
        self.money = money
    
    def play_hand(self):
        game = BlackjackGame()
        winner = ''
        while game.turn == 'player' and not game.player_hand.is_bust():
            move = game.player_allowed_moves()[random.randint(0,1)]
            game.player_move(move)
        
        if game.player_hand.is_bust():
            winner = 'dealer'
            self.money -= 1
        else:
            while not game.over:
                game.dealer_move()

            if game.dealer_hand.is_bust() or game.player_hand.get_score() > game.dealer_hand.get_score():
                winner = 'player'
                self.money += 1

            elif game.player_hand.get_score() < game.dealer_hand.get_score():
                winner = 'dealer'
                self.money -= 1

            else:
                winner = None
        
        return (game.player_hand.get_score(), game.dealer_hand.get_score(),'Winner='+str(winner), self.money)
	
class SmartAgent(object):
    def __init__(self, money=0, epsilon = .1, learning_rate = .5, discount=.2):
        self.money = money
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount = discount
        self.Q = {}
        for state in [(i,j) for i in range(4,22) for j in range(2,12)]:
            self.Q[state] = {'hit':0, 'stand':0}
    
    def learn(self, num_hands):
        for i in range(num_hands):
            self.learn_from_hand()
    
    def learn_from_hand(self):
        game = BlackjackGame()
        winner = ''
        last_move = ''
        cur_state = ()
        next_state = ()
        while game.turn == 'player' and not game.player_hand.is_bust():
            cur_state = game.game_state
            move = self.get_move(game)
            last_move = move
            game.player_move(move)
            next_state = game.game_state

            if game.player_hand.is_bust():
                self.Q[cur_state][move] += self.learning_rate * (-1 )
            
            else:
                self.Q[cur_state][move] += self.learning_rate * (0 + self.discount*self.Q[next_state][self.get_best_move(game)]-self.Q[cur_state][move] )
            
            
        if game.player_hand.is_bust():
            winner = 'dealer'
 
        else:
            while not game.over:
                game.dealer_move()

            if game.dealer_hand.is_bust() or game.player_hand.get_score() > game.dealer_hand.get_score():
                winner = 'player'
                self.Q[cur_state][move] += self.learning_rate * (1 - self.Q[cur_state][move] )

            elif game.player_hand.get_score() < game.dealer_hand.get_score():
                winner = 'dealer'
                self.Q[cur_state][move] += self.learning_rate * (-1 -self.Q[cur_state][move] )

            else:
                winner = None
                reward = 0
        
    def get_move(self, game):
        random_val = random.random()
        if random_val < self.epsilon:
            return random.choice(game.player_allowed_moves())
    
        else:
            return self.get_best_move(game)
    
    def get_best_move(self, game):
        best_value = max([value for value in self.Q[game.game_state].values()])
        best_moves = []
        for move in self.Q[game.game_state]:
            if self.Q[game.game_state][move] == best_value:
                best_moves.append(move)
        best_move = random.choice(best_moves)
        return best_move
    
    def play_optimal(self):
        game = BlackjackGame()
        winner = ''
        while game.turn == 'player' and not game.player_hand.is_bust():
            move = self.get_best_move(game)
            game.player_move(move)
        
        if game.player_hand.is_bust():
            winner = 'dealer'
            self.money -= 1
        else:
            while not game.over:
                game.dealer_move()

            if game.dealer_hand.is_bust() or game.player_hand.get_score() > game.dealer_hand.get_score():
                winner = 'player'
                self.money += 1

            elif game.player_hand.get_score() < game.dealer_hand.get_score():
                winner = 'dealer'
                self.money -= 1

            else:
                winner = None
        
        return (game.player_hand.get_score(), game.dealer_hand.get_score(),'Winner='+str(winner), self.money)
	
	
agent = SmartAgent(money=10000, epsilon=.1, learning_rate=.2, discount=.75)
results = []
for i in [0,100,1000,5000,10000]:
    agent = SmartAgent(money=10000)
    agent.learn(i)
    
    for j in range(10000):
        agent.play_optimal()
    
    results.append((i, agent.money))