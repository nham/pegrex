def re2post(s):
    operator_stack = []
    operand_stack = []

    ops = ['|', '?', '+', '*']

    peektop = lambda stack: stack[len(stack) - 1]

    def apply_top():
        tmp1 = operand_stack.pop()
        tmp2 = operand_stack.pop()
        operand_stack.append( tmp2 + tmp1 + operator_stack.pop() )

    def apply_all():
        while len(operator_stack) > 0:
            apply_top()


    # concatenation is expressed by placing two expressions next to each other,
    # so we need to insert concatenation operators to use the shunt-yard algorithm

    for c in s:
        if c not in ops:
            # as long as we use unary ops, the stacks are the same size
            # using the first binary op increases size difference by 1,
            # but subsequent binary ops merely preserve the difference of 1
            # so we can check whether pushing this operand would cause the
            # difference to become large to determine if a '.' should be inserted
            if len(operand_stack) - len(operator_stack) > 0:
                # pop operators of not-less-than precedence, then push '.'
                while len(operator_stack) > 0 and peektop(operator_stack) != '|':
                    apply_top()

                operator_stack.append('.')

            operand_stack.append(c)
        else:
            if c != '|':
                tmp = operand_stack.pop()
                operand_stack.append(tmp + c)
            else:
                apply_all()
                operator_stack.append(c)


    # apply remaining operators
    apply_all()

    return operand_stack.pop()



class PartialNFA:
    # tf is a list of dictionaries. each dict has keys as input symbols, values are sets of states
    # entry is a state (non-negative int)
    def __init__(self, tf, entry):
        for e in tf:
            if None not in e:
                e[None] = {}

        self.tf = tf
        self.entry = entry


# given a symbol, creates a partial NFA that accepts exactly one of those symbols
def singleton(ch):
    return PartialNFA([{ch: {'exit'}}], 0)


def shift_state_transition_dict(d, n):
    for sym in d:
        d[sym] = set(map(lambda x: x + n if x != 'exit' else x, d[sym]))

def shift_transition_function(tf, n):
    for state_td in tf:
        shift_state_transition_dict(state_td, n)

# takes a list of dictionaries, each of whose entries are sets. in each of the
# sets, replace appearances of 'exit' with k
def replace_exits(tf, k):
    for d in tf:
        for s in d:
            if 'exit' in d[s]:
                d[s].remove('exit')
                d[s].add(k)


# concatenate two partial NFAs together
def concatenate(n1, n2):
    m = len(n1.tf)
    # shift the entries in the n2 transition table first by the number of states
    # in n1. then we can just append them (in order) to n1.tf
    shift_transition_function(n2.tf, m)

    replace_exits(n1.tf, n2.entry + m)

    for e in n2.tf:
        n1.tf.append(e)

    return PartialNFA(n1.tf, n1.entry)

# alternates two partial NFAs together
def alternate(n1, n2):
    m = len(n1.tf)
    shift_transition_function(n1.tf, 1)
    shift_transition_function(n2.tf, m+1)
    tf = [{None: {n1.entry + 1, n2.entry + m + 1}}]

    for e in n1.tf:
        tf.append(e)

    for e in n2.tf:
        tf.append(e)

    return PartialNFA(tf, 0)


def optional(n):
    shift_transition_function(n.tf, 1)
    tf = [{None: {n.entry + 1, 'exit'}}]

    for e in n.tf:
        tf.append(e)

    return PartialNFA(tf, 0)


def star(n):
    shift_transition_function(n.tf, 1)
    tf = [{None: [n.entry + 1, 'exit']}]

    replace_exits(n.tf, 0)

    for e in n.tf:
        tf.append(e)

    return PartialNFA(tf, 0)


def plus(n):
    m = len(n.tf)

    tf = n.tf.copy()
    replace_exits(tf, m)
    tf.append({None: [n.entry, 'exit']})

    return PartialNFA(tf, n.entry)


# What distinguishes a "partial NFA" from a complete one is merely a) the lack
# of initial/acceptance states and b) the presence of transitions to 'exit' states
def complete_partial(p):
    pass
    alphabet = set()
    for d in p.tf:
        for k in d:
            if k is not None:
                alphabet.add(k)

    p.tf.add({None: {}})
    m = len(p.tf) - 1
    replace_exits(p.tf, m)

    return NFA(alphabet, p.tf, p.entry, {m})


class NFA:
    # alphabet - set of symbols
    # tf - transition function, a list of dictionaries where each key is an input symbol, value is the set of states to transition to
    # init_state - non-negative integer representing a symbol
    # accept_states: set of non-negative integers
    def __init__(self, alphabet, tf, init_state, accept_states):
        self.alphabet = alphabet
        self.init_state = init_state # save it so we can reset the DFA later in case we want to
                                     # test different strings from scratch
        self.state = {init_state}

        self.accept = accept_states

        try:
            for e in tf:
                if not isinstance(e, dict):
                    raise TypeError
        except TypeError:
            raise

        self.tf = tf


    def transition(self, inp):
        if inp not in self.alphabet:
            raise TypeError("Input symbol not in alphabet")

        # if we're in the 'dead' state, stay there
        if self.state == {}:
            return

        # get a list of lists of next states
        next_states = set(map(lambda st: self.tf[st][inp], self.state))

        self.state = set().union(*next_states)


    def in_accept_state(self):
        return self.state in self.accept


    # read a string after resetting the DFA to its initial state
    def read(self, string):
        self.state = {self.init_state}

        for s in string:
            self.transition(s)

        return self.in_accept_state()

