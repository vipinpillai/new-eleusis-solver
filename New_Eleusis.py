import random
import operator
import itertools
from collections import OrderedDict
from itertools import combinations
import time
from NewEleusisHelper import *
from ScanRank import *

# Trivial functions to be used in the important test functions
# All require a nonempty string as the argument

def is_suit(s):
    """Test if parameter is one of Club, Diamond, Heart, Spade"""
    return s in "CDHS"

def is_color(s):
    """Test if parameter is one of Black or Red"""
    return s in "BR"

def is_value(s):
    """Test if parameter is a number or can be interpreted as a number"""
    return s.isdigit() or (len(s) == 1 and s[0] in "AJQK")

def is_card(s):
    """Test if parameter is a value followed by a suit"""
    return is_suit(s[-1]) and is_value(s[:len(s) - 1])

def value_to_number(name):
    """Given the "value" part of a card, returns its numeric value"""
    values = [None, 'A', '2', '3', '4', '5', '6',
              '7', '8', '9', '10', 'J', 'Q', 'K']
    return values.index(name)

def number_to_value(number):
    """Given the numeric value of a card, returns its "value" name"""
    values = [None, 'A', '2', '3', '4', '5', '6',
              '7', '8', '9', '10', 'J', 'Q', 'K']
    return values[number]

# -------------------- Important functions

def suit(card):
    """Returns the suit of a card"""
    return card[-1]

def color(card):
    """Returns the color of a card"""
    return {'C':'B', 'D':'R', 'H':'R', 'S':'B'}.get(suit(card))

def value(card):
    """Returns the numeric value of a card or card value as an integer 1..13"""
    prefix = card[:len(card) - 1]
    names = {'A':1, 'J':11, 'Q':12, 'K':13}
    if prefix in names:
        return names.get(prefix)
    else:
        return int(prefix)

def is_royal(card):
    """Tests if a card is royalty (Jack, Queen, or King)"""
    return value(card) > 10

def equal(a, b):
    """Tests if two suits, two colors, two cards, or two values are equal."""
    return str(a) == str(b) # This is to allow comparisons with integers

def less(a, b):
    """Tests if a is less than b, where a and b are suits, cards,
       colors, or values. For suits: C < D < H < S. For colors,
       B < R. For cards, suits are considered first, then values.
       Values are compared numerically."""
    if is_card(a):
        if suit(a) != suit(b):
            return suit(a) < suit(b)
        else:
            return value(a) < value(b)
    elif is_value(a):
        return value_to_number(a) < value_to_number(b)
    else:
        return a < b

def greater(a, b):
    """The opposite of less"""
    return less(b, a)

def plus1(x):
    """Returns the next higher value, suit, or card in a suit;
       must be one. If a color, returns the other color"""
    if is_value(x):
        assert value_to_number(x) < 13
        return number_to_value(value_to_number(x) + 1)
    elif is_suit(x):
        assert x != 'S'
        return "CDHS"["CDHS".index(x) + 1]
    elif is_card(x):
        return number_to_value(value(x) + 1) + suit(x)
    elif is_color(x):
        return "BR"["BR".index(x) - 1]
    
def minus1(x):
    """Returns the next lower value, suit, or card in a suit;
       must be one. If a color, returns the other color"""
    if is_value(x):
        assert value_to_number(x) > 1
        return number_to_value(value_to_number(x) - 1)
    elif is_suit(x):
        assert x != 'C'
        return "CDHS"["CDHS".index(x) - 1]
    elif is_card(x):
        return number_to_value(value(x) - 1) + suit(x)
    elif is_color(x):
        return "BR"["BR".index(x) - 1]

def even(card):
    """Tells if the card's numeric value is even"""
    return value(card) % 2 == 0

def odd(card):
    """Tells if the card's numeric value is odd"""
    return value(card) % 2 != 0

# -------------------- Lists of allowable functions

# These functions are declared so that logic can be supported;
# the actual implementation is in the 'evaluate' function
def andf(): pass
def orf():  pass
def notf(): pass
def iff():  pass

functions = [suit, color, value, is_royal, equal, less,
             greater, plus1, minus1, even, odd, andf,
             orf, notf, iff]

function_names = ['suit', 'color', 'value', 'is_royal',
                  'equal', 'equals', 'less', 'greater', 'plus1',
                  'minus1', 'even', 'odd', 'andf', 'orf',
                  'notf', 'iff', 'and', 'or', 'not', 'if']

# ----- Functions for creating, printing, and evaluating Trees

# Build a dictionary from function names to actual functions
to_function = {'and':andf, 'or':orf, 'not':notf, 'if':iff, 'equals':equal, 'even':even, 'odd':odd}
for f in functions:
    to_function[f.__name__] = f
    
def quote_if_needed(s):
    """If s is not a function, quote it"""
    function_names = map(lambda x: x.__name__, functions)
    return s if s in function_names else "'" + s + "'"

def scan(s):
    """This is an iterator for "tokens," where a token is a
       parenthesis or sequence of nonblank characters; commas
       and whitespace act as delimiters, and are discarded"""
    token = ''
    for ch in s:
        if ch.isspace():
            continue
        if ch in '(),':
            if token != '':
                yield token
                token = ''
            if ch != ',':
                yield ch
        else:
            token += ch
    if token != '':
        yield token
            
def tree(s):
    """Given a function in the usual "f(a, b)" notation, returns
       a Tree representation of that function, for example,
       equal(color(current),'R') becomes
       Tree(equal(Tree(color(current)),'R')) """
    tokens = list(scan(s))
    if len(tokens) == 1:
        return tokens[0]
    expr = ""
    functions = [] # a stack of functions
    args = []      # a stack of argument lists
    depth = 0
    for i in range(0, len(tokens) - 1):
        if tokens[i + 1] == '(':
            f = to_function[tokens[i]]
            depth += 1
        expr += tokens[i]
        if tokens[i] == ')':
            expr += ')'
            depth -= 1
    assert depth == 1, "*** Unmatched parentheses ***"
    return expr + '))'

def combine(f, args):
    """Makes a Tree from a function and a list of arguments"""
    if len(args) == 1:
        return Tree(f, args[0])
    elif len(args) == 2:
        return Tree(f, args[0], args[1])
    elif len(args) == 3:
        return Tree(f, args[0], args[1], args[2])
    else:
        raise Exception("Incorrect arguments: {} {}".format(f, str(args)))
    
def parse(s):
    """Converts a string representation of a rule into a Tree"""
    def parse2(s, i):
        if s[i] in function_names:
            f = to_function.get(s[i])
            assert s[i + 1] == "(", "No open parenthesis after " + s[i]
            (arg, i) = parse2(s, i + 2)
            args = [arg]
            while s[i] != ")":
                (arg, i) = parse2(s, i)
                args.append(arg)
            subtree = combine(f, args)
            return (subtree, i + 1)
        else:
            return (s[i], i + 1)
    return parse2(list(scan(s)), 0)[0]


class Tree:

    def __init__(self, root, first=None, second=None, third=None):
        """Create a new Tree; default is no children"""
        self.root = root
        assert root in functions
        if third == None:
            self.test = None
            self.left = first
            self.right = second
        else: # rearrange parameters so test can be put first
            self.test = first
            self.left = second
            self.right = third

    def __str__(self):
        """Provide a printable representation of this Tree"""
        if self.test != None: # it's an iff Tree
            return 'iff({}, {}, {})'.format(self.left, self.right, self.test)
        if self.left == None and self.right == None:
            return str(self.root)
        elif self.right == None:
            return '{}({})'.format(self.root.__name__, self.left)
        else:
            return '{}({}, {})'.format(self.root.__name__, self.left, self.right)

    def __repr__(self):
        s = "Tree("
        if self.root in functions:
            s += self.root.__name__
        else:
            str(self.root) + '!'
        if self.left != None:  s += ", " + repr(self.left)
        if self.right != None: s += ", " + repr(self.right)
        if self.test != None:  s += ", " + repr(self.test)
        return s + ")"
    
##    debugging = True
##    def evaluate(self, cards):
##        """For debugging, uncomment these lines and change
##           the name of evaluate (below) to evaluate"""
##        before = str(self)
##        after = self.evaluate2(cards)
##        if self.debugging: print "Tree: ", before, "-->", after
##        return after
    
    def evaluate(self, cards):
        """Evaluate this tree with the given card values"""
        def subeval(expr):
            if expr.__class__.__name__ == "Tree":
                return expr.evaluate(cards)
            else:
                if expr == "current":
                    return current
                elif expr == "previous":
                    return previous
                elif expr == "previous2":
                    return previous2
                else:
                    return expr
        try:
            (previous2, previous, current) = cards
            f = self.root
            if f not in functions:
                return f
            
            if f in [suit, color, value, is_royal, minus1, plus1, even, odd]:
                return f(subeval(self.left))
            
            elif f in [equal, less, greater]:
                return f(subeval(self.left), subeval(self.right))
            
            elif f == andf:
                if subeval(self.left):
                    return subeval(self.right)
                return False
            
            elif f == orf:
                if subeval(self.left):
                    return True
                return subeval(self.right)
            
            elif f == notf:
                return not subeval(self.left)
            
            elif f == iff:
                if subeval(self.test):
                    return subeval(self.left)
                else:
                    return subeval(self.right)
        except Exception as e:
            print e
            print "Expression = ", self
            print " with cards =", cards
            raise

#master_board_state = [('KS', []), ('9H', []), ('6C', ['KS', '9C']), ('JH', []), ('QD',[]), ('5S', ['AS'])]
#master_board_state = [('KH', []), ('9C', []), ('6D', ['KS', '9C']), ('JS', []), ('QD',[]), ('5C', ['AS'])]
#master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('9S', []), ('7H', []), ('6C', ['KS', '9C']), ('6H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('JD', []), ('QC', []), ('KH', ['KS', '9C']), ('6S', [])]
#master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS'])]
#master_board_state = [('QS', []), ('4D', []), ('5C', ['KS', '9C']), ('10H', []), ('8C',[]), ('9H', ['AS'])]
#master_board_state = [('7C', [])]
#master_board_state = [('10S', []), ('10S', []), ('10S', []), ('10S', []), ('10S', [])]
#master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D', []), ('9S', ['AS', 'KS', 'QC']), ('KD', []), ('6C', []), ('3D', []), ('AD', []), ('JD', []), ('AS', []), ('2H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D', []), ('9S', ['AS', 'KS', 'QC']), ('KD', []), ('6C', []), ('3D', []), ('AD', []), ('JD', []), ('AS', []), ('2H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D', []), ('9S', ['AS', 'KS', 'QC']), ('KD', []), ('6C', []), ('3D', []), ('AD', []), ('JD', []), ('AS', []), ('2H', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D', []), ('9S', ['AS', 'KS', 'QC']), ('KD', []), ('6C', []), ('3D', []), ('AD', []), ('JD', []), ('AS', []), ('2H', [])]
#master_board_state = []
predicted_rule = None
#master_rule = Tree(orf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))
three_length_hypothesis_flag = True
card_characteristic_list =[]
#board_state = ['9S','3H']
rule_list={}
play_counter = 0


numeric_characterstic = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
suit_characterstic = ['C','S','D','H']


def set_play_counter(counter):
    global play_counter
    play_counter = counter

def get_play_counter():
    return play_counter

def play(card):
    '''
     This function plays a card and validates the card and then updates the board state with the new card 
     based on whether the card is legal or not
    '''
    #play_counter += 1
    set_play_counter(get_play_counter()+1)
    #Invoke validate_card() which returns True/False if the current play is legal/illegal.
    #Update the board_state by calling update_board_state()
    #Return a boolean value based on the legality of the card. 
    print str(get_master_board_state())
    card_legality = True
    if len(get_master_board_state()) < 3:
        print card
        update_board_state(get_master_board_state(),card_legality,card) 
    else:
        card_legality = validate_card(card)
        print 'card_legality: ' + str(card_legality)
        update_board_state(get_master_board_state(),card_legality,card)
    return card_legality

#scan_and_rank_rules(scan_and_rank_hypothesis())

# ranked_hypothesis_list, hypothesis_index_dict = scan_and_rank_hypothesis()

def validate_and_refine_formulated_rule(rule_list = [(Tree(orf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))),(Tree(orf, Tree(even, 'previous'), Tree(even,'current'))),(Tree(orf, Tree(andf, Tree(odd, 'previous'), Tree(even,'current')), Tree(andf, Tree(even, 'previous'), Tree(odd,'current'))))]):

    '''
    1. get_card_mapping_characterstic() ==> 
    2. combined_char_indices_list = [get_card_mapping_characterstic(tuple[0]), get_card_mapping_characterstic(tuple[1]), char_dict[i]]

        for characteristic_tuple in itertools.product(*combined_char_indices_list):
            #print 'Tuple: ' + str(characteristic_tuple)
            if characteristic_tuple in hypothesis_index_dict.keys():
                hypothesis_index_dict[characteristic_tuple].append((i-2, i-1, i))
            else:
                hypothesis_index_dict[characteristic_tuple] = [(i-2, i-1, i)]
            if characteristic_tuple in hypothesis_dict.keys():
                hypothesis_occurrence_count[characteristic_tuple] += 1
                hypothesis_dict[characteristic_tuple] += ((weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3)*hypothesis_occurrence_count[characteristic_tuple]
            else:
                hypothesis_dict[characteristic_tuple] = (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3
                hypothesis_occurrence_count[characteristic_tuple] = 1
            mean += (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3
    '''
    
    #board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS'])]
    
    i = 0   
    exception_legal = {}
    exception_illegal = {}
    # Red must follow black
    #rule1 = Tree(orf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))
    #print rule1.evaluate(['6H', '7D', '9S'])
    #Even must follow Odd test
    '''rule2 = Tree(orf, Tree(even, 'previous'), Tree(even,'current'))

    #Alternate the sequence even odd
    rule3 = Tree(orf, Tree(andf, Tree(odd, 'previous'), Tree(even,'current')), Tree(andf, Tree(even, 'previous'), Tree(odd,'current')))

    legal_card = ['10S', '3H', '6H', '7D','9S','7S']
    
    legal_card2 = ['8S','7H','6S']
    print rule2.evaluate((legal_card2))

    legal_card3 = ['6C','5C','7C']
    print rule3.evaluate((legal_card3))'''

    
    #legal_card = ['10S', '3H', '6H', '7D','9S','7S']
    legal_card = parse_board_state()
    legal_card = legal_card['legal_cards']
    #print legal_card
    #legal_card = ['10S','3H']
    #illegal_cards = [('3H', '6C', 'KS'), ('3H', '6C', '9C'), ('7D', '9S', 'AS'), ('6H','7D','9S')]
    illegal_cards = parse_illegal_indices()

    for rule in rule_list:
        while((i + 2) < len(legal_card)):
            my_legal_list = (legal_card[i],legal_card[i+1],legal_card[i+2])
            if rule.evaluate((my_legal_list)) == False:
                if rule in exception_legal:
                    exception_legal[rule].append(my_legal_list)
                else:
                    exception_legal[rule] = [my_legal_list]
            i += 1

        for tup in illegal_cards:
            if len(tup) > 2:
                my_illegal_list = (tup[0], tup[1], tup[2])
                if rule.evaluate((my_illegal_list)) == True:
                    if rule in exception_illegal:
                        exception_illegal[rule].append(my_illegal_list)
                    else:
                        exception_illegal[rule] = [my_illegal_list]

    legal_exceptions_list = exception_legal.values() #The legal exceptions values for a rule
    illegal_exceptions_list = exception_illegal.values() #The illegal exceptions values for a rule

    #print str(legal_exceptions_list) + "legal!!"
    #print illegal_exceptions_list
    #print exception_legal
    #print exception_illegal

    #property_dict = {'1' : 'C1' , '2' : 'C2', '3': 'C3', '4': 'C4', '5': 'C5', '6': 'C6', '7': 'C7', '8': 'C8', '9': 'C9', '10': 'C10', '11': 'C11', '12': 'C12', '13': 'C13', 'red':'C14' , 'black': 'C15', 'diamond': 'C16' , 'heart':'C17', 'spade': 'C18', 'club': 'C19', 'even': 'C20', 'odd': 'C21', 'royal': 'C22' , 'not_royal': 'C23'}
    hypothesis_index_dict = {}
    hypothesis_dict = {}
    weighted_property_dict = set_characteristic_weights()
    hypothesis_occurrence_count = {}
    mean = 0.0

    if len(legal_exceptions_list) > 0:
        for tup in legal_exceptions_list:
            for val in tup:
                combined_char_indices_list = [get_card_mapping_characterstic(val[0]), get_card_mapping_characterstic(val[1]), get_card_mapping_characterstic(val[2])]
                for characteristic_tuple in itertools.product(*combined_char_indices_list):
                    if characteristic_tuple in hypothesis_index_dict.keys():
                        hypothesis_index_dict[characteristic_tuple].append((val[2],val[1],val[0]))
                    else:
                        hypothesis_index_dict[characteristic_tuple] = [(val[2],val[1],val[0])]
                    if characteristic_tuple in hypothesis_dict.keys():
                        hypothesis_occurrence_count[characteristic_tuple] += 1
                        hypothesis_dict[characteristic_tuple] += ((weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3)*hypothesis_occurrence_count[characteristic_tuple]
                    else:
                        hypothesis_dict[characteristic_tuple] = (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3
                        hypothesis_occurrence_count[characteristic_tuple] = 1
                    mean += (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]]) / 3
        
        for tup in legal_exceptions_list:
            for val in tup:     
                hypothesis_occurrence_count = {}
                combined_char_indices_list = [get_card_mapping_characterstic(val[1]), get_card_mapping_characterstic(val[2])]
                for characteristic_tuple in itertools.product(*combined_char_indices_list):
                    if characteristic_tuple in hypothesis_index_dict.keys():
                        hypothesis_index_dict[characteristic_tuple].append((val[2], val[1]))
                    else:
                        hypothesis_index_dict[characteristic_tuple] = [(val[2], val[1])]

                    if characteristic_tuple in hypothesis_dict.keys():
                        hypothesis_occurrence_count[characteristic_tuple] += 1
                        hypothesis_dict[characteristic_tuple] += ((weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2)*hypothesis_occurrence_count[characteristic_tuple]
                    else:
                        hypothesis_occurrence_count[characteristic_tuple] = 1
                        hypothesis_dict[characteristic_tuple] = (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2
                    mean += (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2
        
        ranked_hypothesis_dict = OrderedDict(sorted(hypothesis_dict.items(), key = lambda (key, value) : (value, key), reverse=True))
        hypothesis_offset = len(ranked_hypothesis_dict)
        mean_cutoff = mean/hypothesis_offset
        ranked_hypothesis = {} 
        for value in ranked_hypothesis_dict.iteritems():
            if value[1] > mean_cutoff:
                ranked_hypothesis[value[0]] = value[1]
            else:
                break
        #print ranked_hypothesis_dict
    else:
        print "Legal exception list is NULL!!"
    


    print '=======================================Illegal======================================================================='
    hypothesis_index_dict = {}
    hypothesis_dict = {}
    weighted_property_dict = set_characteristic_weights()
    hypothesis_occurrence_count = {}
    ranked_hypothesis_dict = {}
    mean = 0.0

    if len(illegal_exceptions_list) > 0:
        for tup in illegal_exceptions_list:
            for val in tup:
                combined_char_indices_list = [get_card_mapping_characterstic(val[0]), get_card_mapping_characterstic(val[1]), get_card_mapping_characterstic(val[2])]
                for characteristic_tuple in itertools.product(*combined_char_indices_list):
                    if characteristic_tuple in hypothesis_index_dict.keys():
                        hypothesis_index_dict[characteristic_tuple].append((val[2],val[1],val[0]))
                    else:
                        hypothesis_index_dict[characteristic_tuple] = [(val[2],val[1],val[0])]
                    if characteristic_tuple in hypothesis_dict.keys():
                        hypothesis_occurrence_count[characteristic_tuple] += 1
                        hypothesis_dict[characteristic_tuple] += ((weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3)*hypothesis_occurrence_count[characteristic_tuple]
                    else:
                        hypothesis_dict[characteristic_tuple] = (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]])/3
                        hypothesis_occurrence_count[characteristic_tuple] = 1
                    mean += (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]]+weighted_property_dict[characteristic_tuple[2]]) / 3
        
        for tup in legal_exceptions_list:
            for val in tup:     
                hypothesis_occurrence_count = {}
                combined_char_indices_list = [get_card_mapping_characterstic(val[1]), get_card_mapping_characterstic(val[2])]
                for characteristic_tuple in itertools.product(*combined_char_indices_list):
                    if characteristic_tuple in hypothesis_index_dict.keys():
                        hypothesis_index_dict[characteristic_tuple].append((val[2], val[1]))
                    else:
                        hypothesis_index_dict[characteristic_tuple] = [(val[2], val[1])]

                    if characteristic_tuple in hypothesis_dict.keys():
                        hypothesis_occurrence_count[characteristic_tuple] += 1
                        hypothesis_dict[characteristic_tuple] += ((weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2)*hypothesis_occurrence_count[characteristic_tuple]
                    else:
                        hypothesis_occurrence_count[characteristic_tuple] = 1
                        hypothesis_dict[characteristic_tuple] = (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2
                    mean += (weighted_property_dict[characteristic_tuple[0]]+weighted_property_dict[characteristic_tuple[1]])/2
        
        ranked_hypothesis_dict = OrderedDict(sorted(hypothesis_dict.items(), key = lambda (key, value) : (value, key), reverse=True))
        hypothesis_offset = len(ranked_hypothesis_dict)
        mean_cutoff = mean/hypothesis_offset
        ranked_hypothesis = {} 
        for value in ranked_hypothesis_dict.iteritems():
            if value[1] > mean_cutoff:
                ranked_hypothesis[value[0]] = value[1]
            else:
                break
    else:
        print "Illegal exception list is NULL!!"
        
    return
    
    #print ranked_hypothesis_dict


def setRule(ruleExp):
    '''
     This function set the predicted rule variable as the rule exp passed as parameter
    '''
    global predicted_rule
    predicted_rule = ruleExp

def rule():
    '''
     This function returns the current rule
    '''
    #return the current rule
    return predicted_rule;

def score(scientist_rule):
    current_score = 0
    player_won = False
    print 'Master Board State: ' + str(get_master_board_state())
    print 'legal cards length: ' + str(len(parse_board_state()['legal_cards']))
    illegal_cards = parse_illegal_indices()
    illegal_counter = 0
    for elem in illegal_cards:
        if len(elem) == 2:
            illegal_counter += 1
    print 'illegal cards length: ' + str(illegal_counter)

    free_counter = 0
    for elem in master_board_state:
        free_counter += 1
        if free_counter > 20:
            current_score += 1
        if elem[1]:
            free_counter += len(elem[1])
            current_score += 2*len(elem[1]) 


    current_rule = rule()
    if str(scientist_rule) != str(current_rule):
        print 'Scientist: ' + str(scientist_rule)
        print 'Current: ' + str(current_rule)
        current_score += 15
        # TODO: Validate predicted rule using validate_rule method for the current rule
        # TODO: Check if predicted rule conforms to the rule current 
        # TODO: Increase score by +30 for a rule that does not describe all cards on board
    else:
        player_won = True
    return current_score, player_won

def find_numeric_characteristic_relation(current_card, prev_card, prev2_card):
    '''
     This function defines a numeric relation between a sliding window of current, prev, prev2 cards
    '''
    numeric_relation_dic = {}
    if (equal(current_card, prev_card)):
        numeric_relation_dic['current_equal_prev'] = True
    if (equal(current_card, prev2_card)):
        numeric_relation_dic['current_equal_prev2'] = True
    if (equal(prev_card, prev2_card)):
        numeric_relation_dic['prev_equal_prev2'] = True

    # greater relation
    if (greater(current_card, prev_card)):
        numeric_relation_dic['current_greater_prev'] = True
    if (greater(current_card, prev2_card)):
        numeric_relation_dic['current_greater_prev2'] = True
    if (greater(prev_card, prev2_card)):
        numeric_relation_dic['prev_greater_prev2'] = True

    # less relation
    if (less(current_card, prev_card)):
        numeric_relation_dic['current_less_prev'] = True
    if (less(current_card, prev2_card)):
        numeric_relation_dic['current_less_prev2'] = True
    if (less(prev_card, prev2_card)):
        numeric_relation_dic['prev_less_prev2'] = True


    # adds relation
    numeric_relation_dic['current_adds_prev'] = value(current_card) + value(prev_card)
    numeric_relation_dic['current_adds_prev2'] = value(current_card) + value(prev2_card)
    numeric_relation_dic['prev_adds_prev2'] = value(prev_card) + value(prev2_card)

    # minus relation
    numeric_relation_dic['current_minus_prev'] = value(current_card) - value(prev_card)
    numeric_relation_dic['current_minus_prev2'] = value(current_card) - value(prev2_card)
    numeric_relation_dic['prev_minus_prev2'] = value(prev_card) - value(prev2_card)

    return numeric_relation_dic;

def validate_card(card):
    #Output: Return True/False, if the current card conforms to the actual rule.
    
    board_state = parse_board_state()
    legal_cards = board_state['legal_cards']
    return master_rule.evaluate((legal_cards[-2], legal_cards[-1] , card))  

def map_characteristic_value_to_characteristic_property(characteristic_value):
    '''
     This function returns a mapping of the characterstic value to the property
    '''
    characteristic_value_to_characteristic_property_dict = {'R':color, 'B':color, 'S':suit, 'C':suit, 'H':suit, 'D':suit, '1': value, '2': value, '3': value, '4': value, '5': value, '6': value, '7': value, '8': value, '9': value, '10': value}
    return characteristic_value_to_characteristic_property_dict[characteristic_value]    

def create_tree(rule):
    '''
     This function converts the internal mapping of characterstic values eg C1,C2 to a tree format which 
     can be easily validated using the evaluate function
    '''
    #TODO - Handle numeric relations during hypothesis transformation. Will be done by invoking find_characteristic_numeric_relation

    triple_tree_characteristic_list = ['R', 'B', 'S', 'C', 'H', 'D', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']

    param_switch_dict = {
        0: 'previous2',
        1: 'previous',
        2: 'current'
    }

    transformed_hypothesis_list = []
    transformed_rule_list = []
    for hypothesis in rule:
        #Form an AND of each hypothesis part of the rule

        for i in xrange(0, len(hypothesis)):
            if len(hypothesis) == 3:
                param_index = i
            elif len(hypothesis) == 2:
                if i == 2:
                    break
                param_index = i+1
            
            characteristic_value = map_card_characteristic_to_value(hypothesis[i])
            if characteristic_value in triple_tree_characteristic_list:
                characteristic_property = map_characteristic_value_to_characteristic_property(characteristic_value)
                transformed_hypothesis = Tree(characteristic_property, param_switch_dict.get(param_index))
            else:
                if characteristic_value == 'not_royal':
                    transformed_hypothesis = Tree(is_royal, param_switch_dict.get(param_index))
                    transformed_hypothesis = Tree(notf, transformed_hypothesis)
                elif characteristic_value == 'royal':
                    transformed_hypothesis = Tree(is_royal, param_switch_dict.get(param_index))
                else:
                    characteristic_property = to_function[characteristic_value]
                    transformed_hypothesis = Tree(characteristic_property, param_switch_dict.get(param_index))

            if characteristic_value in triple_tree_characteristic_list:
                #create Tree with 3 paramaters
                #characteristic_index = C14, characteristic_value = R, characteristic_property = 'color'
                first_param = equal
                third_param = characteristic_value
                transformed_hypothesis = Tree(first_param, transformed_hypothesis, third_param)
            transformed_hypothesis_list.append(transformed_hypothesis)

        transformed_hypothesis = transformed_hypothesis_list[0]
        for i in xrange(1, len(transformed_hypothesis_list)):
            transformed_hypothesis = Tree(to_function['and'], transformed_hypothesis, transformed_hypothesis_list[i])
        transformed_rule_list.append(transformed_hypothesis)
        transformed_hypothesis_list = []

    transformed_rule = transformed_rule_list[0]
    for i in xrange(1, len(transformed_rule_list)):
        transformed_rule = Tree(to_function['and'], transformed_rule , transformed_rule_list[i])

    return transformed_rule


#print create_tree((('C14', 'C19', 'C14'), ('C14', 'C15', 'C17')))
def set_three_length_hypothesis_flag(value):
    global three_length_hypothesis_flag
    three_length_hypothesis_flag = value

def get_three_length_hypothesis_flag():
    return three_length_hypothesis_flag

def scientist(prev2, prev, curr):
    #parse_board_state()
    #initialize_variable_offset()
    if not prev2:
        set_three_length_hypothesis_flag(False)
    else:
        play(prev2)

    play(prev)
    play(curr)
    
    current_card = pick_random_card()
    top_rule_confidence = {};
    initalize_characteristic_list()
    loop_start_time = time.time()
    while play_counter <= 200:
        print '------------------Current Counter----------------' + str(play_counter)
        play(current_card)
        print 'current card: ' + current_card
 
        if play_counter < 15:
            current_card = pick_random_card()
        else:
            start_time = time.time()
            ranked_hypothesis = scan_and_rank_hypothesis(get_three_length_hypothesis_flag())
            print("---scan_and_rank_hypothesis:  %s seconds ---" % (time.time() - start_time))
            start_time = time.time()
            pr_ranked_hypothesis = scan_and_rank_rules(ranked_hypothesis)
            print("---scan_and_rank_rules:  %s seconds ---" % (time.time() - start_time))
            top_rule = pr_ranked_hypothesis.popitem()[0]
            if top_rule in top_rule_confidence:
                top_rule_confidence[top_rule] += 1
                if top_rule_confidence[top_rule] > 10:
                    break
            else:
                top_rule_confidence[top_rule] = 1
            print '----------------TOP Rule: ' + str(top_rule)
            current_card = pick_next_negative_card(top_rule)
            
            # #Create Tree for each rule in pr_ranked_hypothesis and pass to validate
            # print str(create_tree(top_rule[0]))
            # #validate_and_refine_formulated_rule()
            # # pick_next_random_card()
            # #validate_and_refine_formulated_rule()
            # print 'Negative Card: ' + str(current_card)

    print("==================================Scientist Run time---:  %s seconds ---" % (time.time() - loop_start_time))
    return create_tree(top_rule)


def main():
    global master_rule
    master_rule = Tree(orf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))
    setRule(master_rule)
    prev2 = None
    prev = '10S'
    curr = '3H'
    scientist_rule = scientist(prev2, prev, curr)
    #scientist_rule = Tree(andf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))
    print 'Predicted Rule By Scientist: ' + str(scientist_rule)
    result_score, player_won = score(scientist_rule)
    if player_won:
        print 'The Player won the Game! :) '
    else:
        print 'God won the Game!'
    print 'Score: ' + str(result_score)

if __name__ == "__main__": main()