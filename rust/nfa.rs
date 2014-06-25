use std::collections::hashmap::HashSet;
use std::collections::hashmap::HashMap;

use super::partialNFA::{PNFA, State, Exit};
use super::parse::is_op;

pub type NFAState = uint;
type NFAStates = HashSet<NFAState>;

pub type InputSymbol = char;

// For NFA's, some transitions are unlabeled, which we represent by None (hence
// the optional InputSymbol)
pub type Label = Option<InputSymbol>;

type TransitionTable = HashMap<(NFAState, Label), NFAStates>;

pub struct NFA {
    state: NFAStates,
    table: TransitionTable,
    initial: NFAState,
    accept: NFAStates,
}

impl NFA {
    fn new(table: TransitionTable, initial: NFAState, accept: NFAStates) -> NFA {
        let mut state = HashSet::new();
        state.insert(initial);
        NFA { state: state, table: table, initial: initial, accept: accept }
    }

    fn reset(&mut self) {
        self.state.clear();
        self.state.insert(self.initial);
    }

    pub fn from_partial(mut pnfa: PNFA) -> NFA {
        // create a new state, point the Exit targets to that, and make the
        // initial state the 'entry' state of the pnfa
        let m = pnfa.num_states;

        let mut table = HashMap::new();

        for (k, v) in pnfa.table.mut_iter() {
            let mut states: NFAStates = HashSet::new();

            for state in v.iter() {
                match *state {
                    State(s) => { states.insert(s); },
                    Exit => { states.insert(m); },
                }
            }

            table.insert(*k, states);
        }

        let mut accept = HashSet::new();
        accept.insert(m);

        NFA::new(table, pnfa.entry, accept)
    }

    // Takes a post-fix regular expression string and turns it into an NFA
    pub fn compile(s: String) -> Result<NFA, &str> {
        let mut stack: Vec<PNFA> = vec!();

        for c in s.as_slice().chars() {
            if !is_op(c) {
                stack.push(PNFA::single_symbol(c));

            } else if c == '.' {
                let pop1 = stack.pop();
                let pop2 = stack.pop();

                if pop1.is_none() || pop2.is_none() {
                    return Err("Insufficient number of arguments for '.'");
                }

                stack.push(PNFA::concatenate(pop2.unwrap(), pop1.unwrap()));

            } else if c == '|' {
                let pop1 = stack.pop();
                let pop2 = stack.pop();

                if pop1.is_none() || pop2.is_none() {
                    return Err("Insufficient number of arguments for '|'");
                }

                stack.push(PNFA::alternate(pop2.unwrap(), pop1.unwrap()));

            } else if c == '?' {
                let pop = stack.pop();

                if pop.is_none() {
                    return Err("Insufficient number of arguments for '?'");
                }

                stack.push(PNFA::optional(pop.unwrap()));

            } else if c == '*' {
                let pop = stack.pop();

                if pop.is_none() {
                    return Err("Insufficient number of arguments for '?'");
                }

                stack.push(PNFA::star(pop.unwrap()));
            } else if c == '+' {
                let pop = stack.pop();

                if pop.is_none() {
                    return Err("Insufficient number of arguments for '?'");
                }

                stack.push(PNFA::plus(pop.unwrap()));

            } 
        }

        match stack.pop() {
            None => Err("Something went wrong"),
            Some(s) => Ok( NFA::from_partial(s) ),
        }
    }
}
