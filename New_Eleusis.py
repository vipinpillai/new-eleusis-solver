import random
import operator
import itertools
from collections import OrderedDict


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
to_function = {'and':andf, 'or':orf, 'not':notf, 'if':iff, 'equals':equal}
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


def scientist():
	# parse_board_state()
	# initialize_variable_offset()
	# pick_random_card()
	# plays = 0
	# while plays <= 200:
	# 	#play(<card>)
	# 	parse_illegal_indices()
	# 	initalize_characteristic_list()
	# 	#TODO Please remove
	# 	characteristic_list = get_card_characteristics('7H')
	# 	# update_characteristic_list(characteristic_list)
	# 	map_card_characteristic_to_property()
	# 	# scan_and_rank_hypothesis()
	# 	scan_and_rank_rules()
	# 	validate_and_refine_formulated_rule()
	# 	# pick_next_random_card()
	# 	#validate_and_refine_formulated_rule()
	# 	#pick_next_negative_card()
        return ''

	parse_board_state()
	initialize_variable_offset()
	pick_random_card()
	plays = 0
	while plays <= 200:
		#play(<card>)
		parse_illegal_indices()
		initalize_characteristic_list()
		#TODO Please remove
		characteristic_list = get_card_characteristics('7H')
		# update_characteristic_list(characteristic_list)
		map_card_characteristic_to_property()
		# scan_and_rank_hypothesis()
		scan_and_rank_rules()
		validate_and_refine_formulated_rule()
		# pick_next_random_card()
		#validate_and_refine_formulated_rule()
		#pick_next_negative_card()

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



#master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS'])]
master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS']), ('10S', []), ('3H', []), ('6C', []), ('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', [])]
#master_board_state = [('7C', [])]

master_board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS'])]
predicted_rule = ''
card_characteristic_list =[]
board_state = ['9S','3H']
rule_list={}

# R => Red
# B => Black
# C => Club
# D => Diamond
# H => Hearts
# S => Spade
numeric_characterstic = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
suit_characterstic = ['C','S','D','H']

def pick_random_card():
	rank = random.choice( ('A','2','3','4','5','6','7','8','9','10','J','Q','K') )
	suit = random.choice( ('C','D','H','S') )
	card = rank + suit
	return card

def pick_random_card(card_characterstic_list):
	'''
	 Pick a random card using the card characterstic list given in the input
	'''
	if (card_characterstic_list):
		card_number = card_characterstic_list['numeric_characterstic']
		if(len(card_characterstic_list['suit_characterstic'])==1):
			card_suit = card_characterstic_list['suit_characterstic']
		else:
			# case when multiple card characterstic are present for example getting negative card
			card_suit = card_characterstic_list['suit_characterstic'].split(',')
		# TODO need to handle removing color
		# TODO And removing royal card

		numeric_characterstic.remove(card_number) # remove the number
		suit_characterstic.remove(card_suit) # remove the suit as we dont want a random card with the same suit
	rank = random.choice( numeric_characterstic )
	suit = random.choice( suit_characterstic )
	card = rank + suit
	return card

def update_board_state(board_state,flag,current_card):
	#We can also try using the global board state directly without passing it each time.
	#global board_state

	#If the card is valid, append it at the end of the board state with an empty list.
	board_state = board_state
	if flag == True:
		board_state.append(current_card,[])	
	#If the card is invalid, append it to the invalid list of the last card in the board state.
	else:
		board_state[-1][1].append(current_card)
		
	return board_state

def initialize_negative_characteristic_list(card_characterstic_list):
	# mapping of negative character
	negative_characterstic_list = {'Black':'Red','Red':'Black', 'C':'H,D' , 'S' : 'H,D', 'H': 'S,C', 'D': 'S,C'}
	if (not card_characterstic_list):
		print('Characterstic list empty')
		return None
	characterstic_list = []
	if (card_characterstic_list['suit_characterstic']) :
		suit_characterstic_values = negative_characterstic_list[card_characterstic_list['suit_characterstic']].split(',')
		characterstic_list.append(suit_characterstic_values[0])
		characterstic_list.append(suit_characterstic_values[1])
	characterstic_list.append(negative_characterstic_list[card_characterstic_list[2]])
	return pick_random_card(characterstic_list)

def master_board_state_1():
    return master_board_state

def parse_board_state():
    board_state = master_board_state_1()
    prev = ''
    prev2 = ''
    if len(board_state) == 2:
    	#2 elements present, initialize prev & prev2
    	prev2 = board_state[0]
    	prev = board_state[1]
    	#Check if 1 or 2 cards are played based on the rule generated.
    	#Return the legal board state.
    	#Based on the rule curr, prev and prev2 will be initialized. 
    else:
    	curr_tuple = board_state[-1]
    	if curr_tuple[1]:
    		curr = curr_tuple[1][-1]
    	else:
    		curr = curr_tuple[0]
    	prev2, prev = prev, curr
    legal_cards = [x for (x,y) in board_state]
    return_dict = {'prev2':prev2, 'prev':prev, 'curr':curr, 'legal_cards':legal_cards}
    return return_dict

def parse_illegal_indices():
	#This function returns list of tuples of length 3 representing curr as the illegal card, 
	#and prev, prev2 are immediately preceding legal ones. 
	#Illegal tuples of length 3 are currently handled. To be extended to length of 2 & 1.
	illegal_tuple_list = list()
	board_state = master_board_state_1()
	for index, value in enumerate(board_state):
		if value[1]:
			illegal_index_list = value[1]
			for elem in illegal_index_list:
				illegal_tuple = (board_state[index - 1][0], value[0], elem)
				illegal_tuple_list.append(illegal_tuple)

	return illegal_tuple_list
#print parse_illegal_indices()

def map_card_characteristic_to_property(property):
    '''
        Return a mapping of all the card characterstic to the property
    '''
    property_dict = {'1' : 'C1' , '2' : 'C2', '3': 'C3', '4': 'C4', '5': 'C5', '6': 'C6', '7': 'C7', '8': 'C8', '9': 'C9', '10': 'C10', '11': 'C11', '12': 'C12', '13': 'C13', 'red':'C14' , 'black': 'C15', 'diamond': 'C16' , 'heart':'C17', 'spade': 'C18', 'club': 'C19', 'even': 'C20', 'odd': 'C21', 'royal': 'C22' , 'not_royal': 'C23'}
    if property and property in property_dict:
        return property_dict[property]
    else:
        return property_dict

def get_card_char_from_property(index):

    card_char_prop = map_card_characteristic_to_property();
    property = card_char_prop.get(index)
    return property

def get_card_characteristics(current):
    #color, suite, number, even/odd, royal

    royal = ['J', 'Q', 'K']
    card_char = {}
    #color = ""
    if len(current) == 2:
        card_num = current[0]
        card_suite = current[1]
    elif len(current) == 3:
        card_num = current[0]+current[1]
        card_suite = current[2]
    else:
        print current
    #See if the card is royal is not
    if card_num in royal:
        card_char['royal'] = 'royal'
    else:
        card_char['not_royal'] = 'not_royal'

    #Adding the color in the char dictionary
    if card_suite == 'H' or card_suite == 'D':
        card_char['color'] = 'red'
    else:
        card_char['color'] = 'black'

    #Adding the suite in the char dictionary
    if card_suite == 'H':
        card_char['suite'] = 'heart'
    elif card_suite == 'D':
        card_char['suite'] = 'diamond'
    elif card_suite == 'C':
        card_char['suite'] = 'club'
    else:
        card_char['suite'] = 'spade'		

    #Adding the number in the card dictionary
    if card_num == 'J':
        card_num = '11'
    elif card_num == 'Q':
        card_num = '12'
    elif card_num == 'K':
        card_num = '13'
    card_char[card_num] = card_num

    #Adding the even/odd property of the card in the char dictionary 
    card_num = int(card_num)
    if card_num % 2 == 0:
        card_char['even'] = 'even'
    else:
        card_char['odd'] = 'odd'

    
    return card_char

def initalize_characteristic_list():
	'''
		Intialize the characterstic list with zero values, which will be later used by update_card_characterstic
	'''
	return {'C1' : [], 'C2':[], 'C3': [], 'C4':[], 'C5':[], 'C6':[], 'C7':[], 'C8':[], 'C9': [], 'C10': [], 'C11': [], 'C12': [], 'C13': [], 'C14' : [], 'C15': [], 'C16': [], 'C17':[], 'C18':[], 'C19':[], 'C20':[], 'C21':[], 'C22': [], 'C23':[]}

def initialize_variable_offset():
	offset_list=[]
	count=len(board_state)
	print count
	if count >= 3:
		prev2= board_state[-1]
		prev1=board_state[-2]
		curr = board_state[-3]
		offset_list.append(prev2)
		offset_list.append(prev1)
		offset_list.append(curr)
		print "[Current,Previous1, Previous2]: ",offset_list
	elif count is 1:
		curr = board_state[-1]
		offset_list.append(curr)
		print "[Current]: ",offset_list
	elif count is 0:
		print 'Board empty'
	elif count is 2:
		curr = board_state[-2]
		prev1 = board_state[-1]
		offset_list.append(prev1)
		offset_list.append(curr)
		print "[Current,Previous1]:",offset_list
		return offset_list

def scan_and_rank_hypothesis():
    
    hypothesis_dict = {}
	#get legal indices from the the board state
    board_state = parse_board_state()

    char_dict = {}
    legal_cards = board_state['legal_cards']
    print legal_cards
    characteristic_index_list = []
    for i in xrange(0, len(legal_cards)):
        update_characteristic_list(legal_cards[i], i, char_dict)

    for i in xrange(2, len(legal_cards)):
        #Now we have individual chars in characteristic_index_list[i]
        #Decide on how to formulate hypothesis
        combined_char_indices_list = [char_dict[i], char_dict[i-1], char_dict[i-2]]

        for characteristic_tuple in itertools.product(*combined_char_indices_list):
            #print 'Tuple: ' + str(characteristic_tuple)
            if characteristic_tuple in hypothesis_dict.keys():
                hypothesis_dict[characteristic_tuple] += 1
            else:
                hypothesis_dict[characteristic_tuple] = 1
    
    print max(hypothesis_dict.iteritems(), key=operator.itemgetter(1))[0]
    ranked_hypothesis_dict = OrderedDict(sorted(hypothesis_dict.items(), key = lambda (key, value) : (value, key), reverse=True))
    print str(ranked_hypothesis_dict)
	# intersecting_set= []
	# print board_state
	# #Considering curr, prev1 and prev2 being present
	# for i in currSet.intersection(prevSet).intersection(prev2Set):
	# 	intersecting_set.append(i)
	# return intersecting_set			#To decide on the data structure for hypothesis.


def scan_and_rank_rules():
	# TODO function needs to be implemented
	return ;

def pick_next_negative_card(rule_list):
	#TODO - Get the rank of the rule from the scan_and_rank_rule()	- Dependency
	#Pick the top ranked rule
	top_rule=max(rule_list.iteritems(),key=operator.itemgetter(1))[0]
	#Get the first card from each top ranked rule and then find the intersecting list.
	#If intersection set is not null then return a card which has max intersecting property by calling get_card_from_characteristic() - Dependency
    return 

def validate_rule(current_card):
	#Check if the current card adheres to the actual rule
	#Create an instance of the rule by initializing the tree
	#Check if the rule matches the rule by calling the evaluate function of the tree
	#Return true if it does else return false
	board_state= parse_board_state()
	adheres_rule=rule.evaluate(tree, (prev2,prev1,current_card))
    return adheres_rule

def validate_and_refine_formulated_rule():
	return

def update_characteristic_list(current_card, current_card_index, char_dict):
    #Read the current card
    #Get the card characteristics by invoking get_card_characteristics()
    #Invoke the map_card_characteristics() to get the corresponding numeric index into the card characteristic list.
    #Append the characteristics list with the index of the current card.
    board_state = parse_board_state()
    
    card_characteristics = get_card_characteristics(current_card)
    for characteristic in card_characteristics:
        card_characteristic_index = map_card_characteristic_to_property(card_characteristics[characteristic])

        #char_dict[card_characteristic_index].append(board_state['legal_cards'].index(current_card))
        if current_card_index not in char_dict.keys():
            char_dict[current_card_index] = []
        char_dict[current_card_index].append(card_characteristic_index)
    return char_dict
        #char_dict[card_characteristic_index].append()
        char_dict[card_characteristic_index].append(board_state['legal_cards'].index(current_card))
    return card_characteristic_index


def get_card_from_characteristics(card_characteristics):
    # Format {'number': 9, 'suite': 'C', 'color': 'B'}
    # Format {'suite': 'C', 'color': 'B'}
    # Format {'number': 9}
    #Iterate over each of the card characteristic from the input list and compose a matching card. 
    #This will be done by creating a card with first characteristic from the characteristic list and iteratively applying filters based on subsequent characteristics.
    numeric_tuple = ('A','2','3','4','5','6','7','8','9','10','J','Q','K')
    suite_tuple = ('C','D','H','S')
    if (card_characteristics):
        if ('color' in card_characteristics and card_characteristics['color'] == 'Red') :
            suite_tuple = ('D','H')
        elif('color' in card_characteristics and card_characteristics['color'] == 'Black') :
            suite_tuple = ('C','S')
        else:
            suite_tuple = ('C','D','H','S')
        if ('suite' in card_characteristics):
            suite_tuple = (card_characteristics['suite'])
        if ('number' in card_characteristics):
            numeric_tuple = (card_characteristics['number'])

    if ('number' in card_characteristics and card_characteristics['number']) :
        rank = str(card_characteristics['number'])
    else:
        rank = random.choice(numeric_tuple)
    if ('suite' in card_characteristics and card_characteristics['suite']):
        suit = random.choice( suite_tuple )
    else:
        suit = random.choice( suite_tuple ) 
    
    card = rank + suit
    return card



def play(card):
	#Invoke validate_rule() which returns True/False if the current play is legal/illegal.
	#Update the board_state by calling update_board_state()
	#Return a boolean value based on the legality of the card. 
	card_legality = validate_rule(card)
	update_board_state(board_state,card_legality,card)
	return card_legality

scan_and_rank_hypothesis()

def validate_and_refine_formulated_rule():
	
	#@TODO: Update the code based on scan & rank hypothesis.
	#@TODO: Return Part

	#board_state = [('10S', []), ('3H', []), ('6C', ['KS', '9C']), ('6H', []), ('7D',[]), ('9S', ['AS'])]
	
	i = 0
	exception_legal_list = []
	exception_illegal_list = []

	# Red must follow black
	rule1 = Tree(orf, Tree(equal, Tree(color, 'previous'), 'R'), Tree(equal, Tree(color, 'current'), 'R'))

	legal_card = ['10S', '3H', '6H', '7D','9S','7S']
	#illegal_cards = parse_illegal_indices() #in the format prev2,prev,curr
	
	illegal_cards = [('3H', '6C', 'KS'), ('3H', '6C', '9C'), ('7D', '9S', 'AS'), ('6H','7D','9S')]

	while((i + 2) < len(legal_card)):
		my_legal_list = (legal_card[i],legal_card[i+1],legal_card[i+2])
		if rule1.evaluate((my_legal_list)) == False:
			exception_legal_list.append(my_legal_list)
		i += 1
	for tup in illegal_cards:
		my_illegal_list = (tup[0], tup[1], tup[2])
		if rule1.evaluate((my_illegal_list)) == True:
			exception_illegal_list.append(my_illegal_list)

	#print except_list
	return

def setRule(ruleExp):
    predicted_rule = ruleExp

def rule():
    #return the current rule
    return predicted_rule;

def score(board_state):
    current_score = 0
    play_counter = 0
    board_state = parse_board_state()
    illegal_index_list = parse_illegal_indices()

    if board_state:
        legal_cards = board_state['legal_cards'];
    for card in legal_cards:
        if play_counter >=20:
            current_score +=1
    current_score = current_score + 2*(len(illegal_index_list))
    scientist_rule = scientist()
    current_rule = rule()
    if scientist_rule != current_rule:
        current_score += 15
        # TODO: Validate predicted rule using validate_rule method for the current rule
        # TODO: Check if predicted rule conforms to the rule current 
    return current_score

def find_numeric_characteristic_relation(current_card, prev_card, prev2_card):
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

	#print except_list
