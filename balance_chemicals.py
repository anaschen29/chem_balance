
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NON_INTS = ALPHABET + " ()"

###
# dict helper functions
###

def scale_dict(dictionnary, scalar):
    if not dictionnary:
        return {}
    return {k:scalar*dictionnary[k] for k in dictionnary.keys()}

def add_dict(dict1, dict2):
    total_keys = list(dict1.keys()) + list(dict2.keys())
    return {k:dict1.get(k, 0) + dict2.get(k,0) for k in total_keys}

####
# parsing and tokenizing
####

def tokenize(expression):
    """
    Tokenizes an expression.
    """
    token_list = []
    length = len(expression)
    ignore = False
    for index in range(length):
        value = expression[index]
        if value in UPPER:
            ignore = False
        if index > 0 and value.isdigit() and not expression[index-1].isdigit():
            ignore = False
        elif value in " ()":
            ignore = False
            if value in "()":
                token_list.append(value)
            continue
        elif value == "+":
            token_list.append("+")
            continue
        if not ignore:
            if value not in NON_INTS:
                number = int(value)
                ignore=True
                to_append = value
                for i in range(index+1, length):
                    expr = expression[i]
                    if expr.isdigit():
                        to_append += expr
                    else:
                        break
                token_list.append(to_append)
            else:
                if value.isupper():
                    if index < length-1:
                        next_char = expression[index+1]
                        if next_char.islower() and next_char in ALPHABET:
                            ignore=True
                            token_list.append(value+next_char)
                        else:
                            token_list.append(value)
                    else:
                        token_list.append(value)

    return token_list




def parse(tokens):
    """
    Parsing function.
    """
    length = len(tokens)
    def parsing_helper(index):
        parsed_list = []
        if index >= len(tokens):
            return []
        value = tokens[index]
        if value.isdigit():
            parsed_list.append(int(value))
            parsed_list += parsing_helper(index+1)
        elif value == "+":
            parsed_list.append(value)
            parsed_list+=parsing_helper(index+1)
        elif value == "(":
            first_closing_index = 0
            count = 1
            for i in range(index+1, length):
                if tokens[i] == "(":
                    count +=1
                elif tokens[i] == ")":
                    count -= 1
                if count == 0:
                    first_closing_index = i
                    break
            sub_list = tokens[index+1:first_closing_index]
            conclusion = parse(sub_list)
            parsed_list.append(conclusion)
            parsed_list += parsing_helper(first_closing_index+1)
        else:
            parsed_list.append(value)
            parsed_list+=parsing_helper(index+1)

        return parsed_list

    return parsing_helper(0)


def max_dictionnarize(parsed_list):
    """
    Dictionnarizes an expression
    """
    current_dict = dict()
    length = len(parsed_list)
    for index in range(length):
        value = parsed_list[index]
        if value != "+":
            old_dict = {}
            scaling = 1
            not_int =False
            if isinstance(value, list):
                old_dict = max_dictionnarize(value)
                not_int = True
            elif isinstance(value, str):
                old_dict = {value : 1}
                not_int = True
            if index != length-1:
                next_el = parsed_list[index+1]
                if isinstance(next_el, int):
                    scaling *= next_el
            if not_int:
                current_dict = add_dict(current_dict, scale_dict(old_dict, scaling))

    return current_dict

def dict_from_dict(dictionnary):
    """
    From big dictionnary give small dictionnary.
    {"SO4" : 2, "H2O": 5} -----> {"S":8, "O":13, "H":10}

    """
    if not dictionnary:
        return {}
    to_return = {}
    for key in dictionnary.keys():
        small_dict = max_dictionnarize(parse(tokenize(key)))
        scaling = dictionnary[key]
        to_return = add_dict(to_return, scale_dict(small_dict, scaling))
    return to_return

def expr_dict(expression):
    """
    Given a parsed list, return a dict with 1's everywhere and keys as elements separated
    by +.
    """
    total_list = expression.replace(" ", "").split("+")
    return {key : 1 for key in total_list}

def hash(lhs_dict, rhs_dict):
    return (tuple(lhs_dict.items()), tuple(rhs_dict.items()))

def victory(state):
    lhs_dict = dict_from_dict({k:v for (k,v) in state[0]})
    rhs_dict = dict_from_dict({k:v for (k,v) in state[1]})
    return lhs_dict == rhs_dict

def get_neighbors(state):

    neighbors = set()
    for pair in state[0]:
        k = pair[0]
        v = pair[1]
        neighboring_lhs = tuple(((n,m) if (n,m) != (k,v) else (n,m+1)) for (n,m) in state[0])
        right_hand_side_copy = tuple((k,v) for (k,v) in state[1])
        neighbors.add((neighboring_lhs, right_hand_side_copy))
    for pair in state[1]:
        k = pair[0]
        v = pair[1]
        neighboring_rhs = tuple(((n,m) if (n,m) != (k,v) else (n,m+1)) for (n,m) in state[1])
        left_hand_side_copy = tuple((k,v) for (k,v) in state[0])
        neighbors.add((left_hand_side_copy, neighboring_rhs))

    return neighbors

def balance(expression):
    """
    Balancing function.
    Expression : Chemical expression w/ no coefficients.
    """

    splitting_field = expression.split("=")
    left_hand_side, right_hand_side = splitting_field[0], splitting_field[1]
    initial_state = hash(expr_dict(left_hand_side), expr_dict(right_hand_side))

    agenda = [initial_state]
    visited = {initial_state}

    while agenda:
        last_state = agenda.pop(0)
        if victory(last_state):
            return last_state
        for neighbor in get_neighbors(last_state):
            if neighbor not in visited:
                agenda.append(neighbor)
                visited.add(neighbor)

    return None


print(balance("Li3PO4 + CaCl2 + GaBr3 + Na2CO3 + Pb(OH)2 + HCl = H2O + PbCl2 + Ga2(CO3)3 + NaBr + Ca3(PO4)2 + LiCl"))
