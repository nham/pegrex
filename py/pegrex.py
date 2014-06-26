from parse import ops, re2post
import sys

# from a postfix regular expression, compile an NFA
# maintains a stack of PartialNFAs
def compile_NFA(s):
    stack = []

    for c in s:
        if c not in ops():
            stack.append(single_symbol(c))
        else:
            if c == '|':
                pop2 = stack.pop()
                pop1 = stack.pop()
                stack.append(alternate(pop1, pop2))
            elif c == '.':
                pop2 = stack.pop()
                pop1 = stack.pop()
                stack.append(concatenate(pop1, pop2))
            elif c == '?':
                stack.append(optional(stack.pop()))
            elif c == '*':
                stack.append(star(stack.pop()))
            elif c == '+':
                stack.append(plus(stack.pop()))
            else: 
                raise Exception("'{}' operator unrecognized".format(c))

    return complete_partial(stack.pop())




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
def single_symbol(ch):
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

    p.tf.append({None: {}})
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
        self.init_state = init_state # save it so we can reset the DFA later in case 
                                     # we want to test different strings from scratch
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

        # if we're in no state, we obviously can't transition anywhere
        if self.state == {}:
            return

        def add_from_unlabeled(states):
            # first take all unlabeled transitions until state stops changing
            def take_unlabeled(state):
                return self.tf[state][None]

            new_states = states.union(*list(map(take_unlabeled, states)))

            while new_states != states:
                states = new_states
                new_states = states.union(*list(map(take_unlabeled, states)))

            return new_states


        # get a list of sets of next states
        def apply_input(state):
            state_dict = self.tf[state]

            if inp in state_dict:
                return state_dict[inp]
            else:
                return {}


        new_states = add_from_unlabeled(self.state)
        next_states = list(map(apply_input, new_states))
        self.state = set().union(*next_states)


    def in_accept_state(self):
        for state in self.state:
            if state in self.accept:
                return True

        return False

    # read a string after resetting the DFA to its initial state
    def read(self, string):
        self.state = {self.init_state}

        for s in string:
            self.transition(s)

        return self.in_accept_state()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: pegrex <regex>")
        sys.exit(1)

    n = compile_NFA(re2post(sys.argv[1]))
    print("compiled '{}'".format(sys.argv[1])

    run = lambda x: print("Run it on '{}': accept = {}".format(x, n.read(x)))
    run('abc')
    run('e')
    run('de')
