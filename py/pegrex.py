# DFA could be given by a list of states, and for each state a dict where inputs are keys, states are values.
# if input isn't in current list, transition to the void state or whatever. while in void state, you just stay there.
# also have to mark which of the states are accept states

class DFA:
    # expecting a list of dictionaries. states are represented by non-negative ints.
    # we use '-1' as the 'dead' state (so we can provide partial transition functions)
    def __init__(self, alphabet, tf, init_state, accept_states):
        self.alphabet = alphabet
        self.init_state = init_state # save it so we can reset the DFA later in case we want to
                                     # test different strings from scratch
        self.state = init_state
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
        if self.state == -1:
            return

        tf = self.tf[self.state]

        try:
            self.state = tf[inp]
        except KeyError:
            self.state = -1


    def in_accept_state(self):
        return self.state in self.accept


    # read a string after resetting the DFA to its initial state
    def read(self, string):
        self.state = self.init_state

        for s in string:
            self.transition(s)

        return self.in_accept_state()


class PartialNFA:
    # tf is a list of dictionaries. each dict has keys as input symbols, values are lists of states
    # entry is a state
    def __init__(self, tf, entry):
        for e in tf:
            if None not in e:
                e[None] = []

        self.tf = tf
        self.entry = entry


# given a symbol, creates a partial NFA that accepts exactly one of those symbols
def singleton(ch):
    return PartialNFA([{ch: ['exit']}], 0)


def shift_state_transition_dict(d, n):
    for sym in d:
        d[sym] = list(map(lambda x: x + n if x != 'exit' else x, d[sym]))

def shift_transition_function(tf, n):
    for state_td in tf:
        shift_state_transition_dict(state_td, n)


# takes a list of dictionaries, each of whose entries are lists. in each of the
# lists, replace appearances of 'exit' with k
def replace_exits(tf, k):
    for d in tf:
        for s in d:
            for i in range(0, len(d[s])):
                if d[s][i] == 'exit':
                    d[s][i] = k


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
    tf = [{None: [n1.entry + 1, n2.entry + m + 1]}]

    for e in n1.tf:
        tf.append(e)

    for e in n2.tf:
        tf.append(e)

    return PartialNFA(tf, 0)


def optional(n):
    shift_transition_function(n.tf, 1)
    tf = [{None: [n.entry + 1, 'exit']}]

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

