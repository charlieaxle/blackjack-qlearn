CARD_VALUES = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10,'A':11}
import random

class Card(object):    
    def __init__(self, card_type=None):
        '''
        Initializes a new Card object
    
        Params:
            type (string): Type of card, i.e. "7" or "A". If None, random Card is selected.
    
        Object Attributes:
            type (string): The type of card, i.e. "7" or "A"
            value (string): The value of the card
        '''
        if card_type:
            self.type= card_type
        else:
            self.type = list(CARD_VALUES.keys())[random.randint(0,len(CARD_VALUES)-1)]
        self.value = CARD_VALUES[self.type]
        self.busted = False
        
    def __str__(self):
        return self.type+':'+str(self.value)

class Hand(object):    
    def __init__(self, initial_cards=0):
        '''
        Initializes a new Hand object
        
        Object Attributes:
            cards (list): A list that may contain multiple Card objects
            score (int): The current value of the cards in the hand
            busted (boolean): True if hand is bust, otherwise False
        '''
        self.cards = []
        self.score = 0
        self.busted = False
        self.deal_card(initial_cards)      
    
    def get_score(self):
        '''
        Used to access the current score of a Hand object
        Params: None
        Returns: self.score
        '''
        return sum([card.value for card in self.cards])
    
    def deal_card(self, num_cards=1):
        '''
        Used to add card(s) to Hand object
        
        Params:
            num_cards(int, default=1): Number of cards to add
        Returns:
            None
        '''        
        for i in range(num_cards):
            self.cards.append(Card())
            self.score = self.get_score()
            self.busted = (self.score > 21)
    
    def possible_moves(self):
        '''
        Used to get possible moves available to a hand'
        
        Params:
            None
        Returns:
            List of possible moves. Currently always returns ["hit","stand"]
        '''
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
        '''
        Initializes a new BlackjackGame object
        
                
        Attributes:
            turn (string): "player" or "dealer" depending on current turn
            winner (string): Winner of hand
            over (boolean): True if hand is over, otherwise False
            player_hand (Hand): Player's current hand
            dealer_hand (Hand): Dealer's current hand
            game_state (tuple): Tuple containing player hand value and dealer hand value
            
        '''
        self.turn='player'
        self.winner = None
        self.over = False
        self.player_hand = Hand(2)        
        self.dealer_hand = Hand(2)
        self.game_state = (self.player_hand.get_score(),self.dealer_hand.cards[0].value)
        
    def update_game_state(self):
        '''
        Function to update the current game state - invoked after a player is dealt a card
        
        Params:None
        Returns:None
        '''
        self.game_state = (self.player_hand.get_score(),self.dealer_hand.cards[0].value)
        
        
    def player_allowed_moves(self):
        '''
        Function to get moves availbe to player based on current hand
        
        Params:None
        Reutnrs: List of possible moves
        '''
        return self.player_hand.possible_moves()
    
    def player_move(self, move):
        '''
        Allows player to make a move ("hit" or "stand")
        
        Params: 
            move (string): Move made - currently only "hit" or "stand" allowed
        Returns:None
        '''
        if move =='hit':
            self.player_hand.deal_card()
            self.update_game_state()
        else:
            self.turn='dealer'
    
    def dealer_move(self):
        '''
        Function that makes the dealer make one move. Dealer's move is restricted by rules
        
        Params:None
        Returns:None
        '''
        if self.dealer_hand.get_score() < 17:
            self.dealer_hand.deal_card()
            self.update_game_state()
        else:
            self.turn = None
            self.over = True


class Agent(object):
    def __init__(self, money=0, epsilon = .1, learning_rate = .5, discount=.2):
        '''
        Initializes a new Agent object
        
        Parameters:
            money (int, default=0): How much money Agent starts with
            epsilon (float, default=.1): Float between 0 and 1. Used for Epsilon-Greedy algorithm.
            learning_rate (float, default=.5): Learning rate in Q-learning algorithm
            discount (float, default=.2): Discount in Q-learning algorithm
        
        Object Attributes:
            money (int): Amount of money agent currently has
            epsilon, learning_rate, discount (float): As initialized. Will not change, unless reset
            Q (dictionary): Table of Q-values. Each entry in form: (game state): {"hit":Q-value, "stand":Q-value}
                *Q initialized for 0 Q-value for all possible states and actions
        '''
            
        self.money = money
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount = discount
        self.Q = {}
        for state in [(i,j) for i in range(4,22) for j in range(2,12)]:
            self.Q[state] = {'hit':0, 'stand':0}
    
    def learn(self, num_hands):
        '''
        This method can be called to make the Agent "learn" Blackjack strategy over a number of hands.
        The Agent does not win or lose money during these rounds, just explores strategy.

        Params:
            num_hands (int): Number of hands to learn from
        Returns:None
        '''
        for i in range(num_hands):
            self.learn_from_hand()
    
    def learn_from_hand(self):
        '''
        Method for Agent to play one Blackjack hand and update current strategy (self.Q)

        Params:None
        Returns:None
        '''
        game = BlackjackGame()
        winner = ''
        last_move = ''
        cur_state = ()
        next_state = ()
        while game.turn == 'player' and not game.player_hand.busted:
            cur_state = game.game_state
            move = self.get_move(game)
            last_move = move
            game.player_move(move)
            next_state = game.game_state

            if game.player_hand.busted:
                self.Q[cur_state][move] += self.learning_rate * (-1 )
            
            else:
                self.Q[cur_state][move] += self.learning_rate * (0 + self.discount*self.Q[next_state][self.get_best_move(game)]-self.Q[cur_state][move] )
            
            
        if game.player_hand.busted:
            winner = 'dealer'
 
        else:
            while not game.over:
                game.dealer_move()

            if game.dealer_hand.busted or game.player_hand.get_score() > game.dealer_hand.get_score():
                winner = 'player'
                self.Q[cur_state][move] += self.learning_rate * (1 - self.Q[cur_state][move] )

            elif game.player_hand.get_score() < game.dealer_hand.get_score():
                winner = 'dealer'
                self.Q[cur_state][move] += self.learning_rate * (-1 -self.Q[cur_state][move] )

            else:
                winner = None
                reward = 0
        
    def get_move(self, game):
        '''
        Method for Agent to pick a move.  Epsilon-Greedy choice based on current self.Q-learning

        Params:
            game (BlackjackGame()): An instance of a BlackjackGame
        Returns:None
        '''

        random_val = random.random()
        if random_val < self.epsilon:
            return random.choice(game.player_allowed_moves())
    
        else:
            return self.get_best_move(game)
    
    def get_best_move(self, game):
        '''
        Method for Agent to find the best move given current game state and self.Q

        Params:
            game (BlackjackGame()): An instance of a BlackjackGame
        Returns:None
        '''

        best_value = max([value for value in self.Q[game.game_state].values()])
        best_moves = []
        for move in self.Q[game.game_state]:
            if self.Q[game.game_state][move] == best_value:
                best_moves.append(move)
        best_move = random.choice(best_moves)
        return best_move

    def play(self, num_hands):
        '''
        Method to make Agent play multiple hands. Agent will always choose move that is best according to self.Q

        Params:
            num_hands (int): Number of hands to play
        Returns:None
        '''
        starting_money = self.money
        for i in range(num_hands):
            self.play_optimal()
            
        return {'money_left':self.money, 'return_rate':(self.money-starting_money)/starting_money }
    
    def play_optimal(self):
        '''
        Method to make Agent play a single hands. Agent will always choose move that is best according to self.Q

        Params:
            num_hands (int): Number of hands to play
        Returns: tuple containing (player score, dealer score, winner, and self.money)
        '''
        game = BlackjackGame()
        winner = ''
        while game.turn == 'player' and not game.player_hand.busted:
            move = self.get_best_move(game)
            game.player_move(move)
        
        if game.player_hand.busted:
            winner = 'dealer'
            self.money -= 1

        else:
            while not game.over:
                game.dealer_move()

            if game.dealer_hand.busted or game.player_hand.get_score() > game.dealer_hand.get_score():
                winner = 'player'
                self.money += 1

            elif game.player_hand.get_score() < game.dealer_hand.get_score():
                winner = 'dealer'
                self.money -= 1

            else:
                winner = None
        
        return (game.player_hand.get_score(), game.dealer_hand.get_score(),'Winner='+str(winner), self.money)