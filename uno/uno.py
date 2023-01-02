import numpy as np
import random


class Card(object):
    """
    object for an uno card

    Parameters
    ----------
    number : int (None)
        The numerical value of the card (None)
    color : str (None)
        The color of the card ('r', 'g', 'b', 'y' or None)
    action : str (None)
        The action of the card ('wild', 'wild+4', '+2', 'skip', 'reverse')
    """
    def __init__(self, number=None, color=None, action=None, wild=False):
        self.number = number
        self.color = color
        self.action = action
        self.wild = wild

    def playable(self, other_card):
        """Is the card playable on an other card?
        """
        if (self.number is not None) & (self.number == other_card.number):
            return True
        if self.action == 'wild':
            return True
        if self.action == 'wild+4':
            return True
        if (self.color is not None) & (self.color == other_card.color):
            return True
        if (self.action is not None) & (self.action == other_card.action):
            return True
        return False

    def __str__(self):
        result = ''
        if self.color is not None:
            result += self.color
        if self.number is not None:
            result += ' %i' % self.number
        if self.action is not None:
            result += ' ' + self.action

        return result

    def __repr__(self):
        return self.__str__()


class BasePlayer(object):
    """A single player. Subclass to add new strategies.

    hand : list of Card objects
        The starting hand

    """
    def __init__(self, hand):
        self.hand = hand

    def pick_wild_color(self):
        """Logic for picking wild card color

        Eventually, need to have a way to pass in info about opponent's hands so this can play defense
        """
        # Just always pick blue!
        return 'b'

    def __call__(self, up_card):
        """Call on the player to take a turn
        """
        # Check which cards are possible
        possible_cards = [card.playable(up_card) for card in self.hand]

        # if we have no possible cards to play, return None
        if not any(possible_cards):
            return None
        
        indx = np.min(np.where(possible_cards)[0])

        card_to_play = self.hand.pop(indx)

        if card_to_play.wild:
            color_choice = self.pick_wild_color()
            card_to_play.color = color_choice

        return card_to_play


class CommonColor(BasePlayer):

    def pick_wild_color(self):
        """Logic for picking wild card color

        Eventually, need to have a way to pass in info about opponent's hands so this can play defense
        """

        color_hist = {'r': 0, 'b': 0, 'g': 0, 'y': 0}
        for card in self.hand:
            if card.color is not None:
                color_hist[card.color] += 1

        winner = np.max(list(color_hist.values()))

        # Just take the first color that has the most cards
        for key in color_hist:
            if color_hist[key] == winner:
                return key


def generate_deck():
    """Generate a standard UNO deck, return a list of Card objects
    """
    deck = []
    for color in 'rgby':
        # zero to 9
        for number in range(10):
            deck.append(Card(number=number, color=color))
        # 1 to 9
        for number in range(1, 10):
            deck.append(Card(number=number, color=color))
        # Generate 2 of each action card in each color
        for action in ['+2', 'skip', 'reverse']:
            for i in range(2):
                deck.append(Card(color=color, action=action))
    # 4 of each wild card
    for action in ['wild', 'wild+4']:
        for i in range(4):
            deck.append(Card(action=action, wild=True))

    return deck


class Dealer(object):
    """A dealer to keep track of who wins
    """

    def __init__(self, players, seed=42):
        random.seed(seed)

        self.players = players
        # track how many wins each player gets
        self.wins = np.zeros(len(self.players), dtype=int)

    def _reshuffle(self, deck, discard_pile):
        """shuffle discard pile if deck is empty
        """
        if len(deck) == 0:
            random.shuffle(discard_pile)
            deck = discard_pile
            discard_pile = []
        return deck, discard_pile

    def play_game(self, n_start=7, draw_max=4):

        # Make sure no one tried to save a card from last time
        for player in self.players:
            player.hand = []

        n_players = len(self.players)

        # shuffle up a fresh deck
        deck = generate_deck()
        random.shuffle(deck)

        # and deal
        for player in self.players:
            for i in range(n_start):
                player.hand.append(deck.pop(0))

        lengths = 1
        turn_indx = 0

        # Flip the direction if a reverse is played
        direction = +1

        # keep playing until someone has no cards
        discard_pile = []

        # flip the top card
        top_card = deck.pop(0)
        # need to make sure it's not a wild
        while top_card.wild:
            discard_pile.append(top_card)
            top_card = deck.pop(0)

        counter = 0
        # Play until someone is out of cards
        while np.min(lengths) > 0:
            draw_counter = 0
            played_card = None
            while (draw_counter < draw_max) & (played_card is None):
                played_card = self.players[turn_indx](top_card)
                draw_counter += 1
                if played_card is None:
                    self.players[turn_indx].hand.append(deck.pop(0))
                    # Every time we take a card from the deck, see if we need to reshuffle
                    deck, discard_pile = self._reshuffle(deck, discard_pile)

            if played_card is not None:
                if played_card.action is not None:
                    indx_hit = (turn_indx + direction) % n_players
                    if played_card.action == 'skip':
                        turn_indx += 1
                    elif played_card.action == 'reverse':
                        direction = -1 * direction
                        # if playing heads-up, reverse acts as a skip
                        if len(self.players) == 2:
                            turn_indx += 1
                    elif played_card.action == '+2':
                        for i in range(2):
                            self.players[indx_hit].hand.append(deck.pop(0))
                            deck, discard_pile = self._reshuffle(deck, discard_pile)
                    elif played_card.action == 'wild+4':
                        for i in range(4):
                            self.players[indx_hit].hand.append(deck.pop(0))
                            deck, discard_pile = self._reshuffle(deck, discard_pile)

            # how many cards does each player have
            lengths = [len(player.hand) for player in self.players]

            # advance whose turn it is.
            turn_indx = (turn_indx + direction) % n_players 
            #counter += 1
            #if counter > 5:
            #    import pdb ; pdb.set_trace()
            if played_card is not None:
                # reset wild color if needed
                if top_card.wild:
                    top_card.color = None
                discard_pile.append(top_card)
                top_card = played_card
        # Someone has no cards in their hand, they win.
        winner = np.where(np.array(lengths) == 0)[0]
        return winner

    def __call__(self, n_games=100, n_start=7):
        for i in range(n_games):
            indx = self.play_game(n_start=n_start)
            self.wins[indx] += 1

        return self.wins

