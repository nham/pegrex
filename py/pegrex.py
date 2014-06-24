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


class WTF:
    def __init__(self, x):
        self.x = x
