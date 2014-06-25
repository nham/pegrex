use std::collections::hashmap::HashMap;
use std::collections::hashmap::HashSet;
use super::nfa::{NFAState, Label};

#[deriving(PartialEq, Eq, Clone, Hash)]
pub enum PNFATarget {
    State(NFAState),
    Exit,
}

type PNFATargetSet = HashSet<PNFATarget>;

type TransitionTable = HashMap<(NFAState, Label), PNFATargetSet>;

// By convention a Partial NFA with n states uses the first n natural numbers
// as state symbols. When combining two NFAs, we need to shift those state numbers
fn create_shifted_table(table: &TransitionTable, n: uint) -> TransitionTable {
    fn shift_key(v: (uint, Label), k: uint) -> (uint, Label) {
        (v.val0() + k, v.val1())
    }

    fn shift_val(targets: &PNFATargetSet, k: uint) -> PNFATargetSet {
        let mut new_set = HashSet::new();
        for target in targets.iter() {
            match *target {
                Exit => { new_set.insert(Exit); },
                State(s) => { new_set.insert(State(s + k)); },
            }
        }

        new_set
    }

    let mut new = HashMap::new();

    for (k, v) in table.iter() {
        new.insert(shift_key(*k, n), shift_val(v, n));
    }

    new
}

fn redirect_exit_targets(table: &mut TransitionTable, n: NFAState) {
    for (k, v) in table.mut_iter() {
        if v.contains(&Exit) {
            v.remove(&Exit);
            v.insert(State(n));
        }
    }
}

// add contents of second table to the first. this makes the second table
// unusable as it actually moves the contents of the second table and doesn't
// merely clone them
fn add_table(table1: &mut TransitionTable, table2: TransitionTable) {
    for (k, v) in table2.move_iter() {
        table1.insert(k,v);
    }
}

#[deriving(PartialEq, Eq, Clone)]
pub struct PNFA {
    pub table: TransitionTable,
    pub entry: NFAState,
    pub num_states: uint,
}

impl PNFA {
    fn new(table: TransitionTable, entry: NFAState) -> PNFA {
        let mut max: NFAState = 0u;

        for &(state, _) in table.keys() {
            if state > max {
                max = state;
            }

        }

        PNFA { table: table, entry: entry, num_states: max }
    }

    /*
    fn transition(&self, st: NFAState, input: char) -> Result<NFAState, &str> {
        if !self.table.contains_key(&(st, input)) {
            Err("Either input state is invalid or symbol is not recognized")
        } else {
            let next = self.table.find(&(st, input)).unwrap();
            Ok(*next)
        }
    }
    */

    pub fn single_symbol(s: char) -> PNFA {
        let mut t = HashMap::new();
        let mut set = HashSet::new();
        set.insert(Exit);
        t.insert((0u, Some(s)), set);
        PNFA::new(t, 0u)
    }

    pub fn concatenate(mut n1: PNFA, n2: PNFA) -> PNFA {
        let m = n1.num_states;
        let new_n2_table = create_shifted_table(&(n2.table), m);
        redirect_exit_targets(&mut(n1.table), n2.entry + m);

        add_table(&mut n1.table, new_n2_table);
        n1.num_states += n2.num_states;

        n1
    }

    pub fn alternate(n1: PNFA, n2: PNFA) -> PNFA {
        let mut table: TransitionTable = HashMap::new();
        let m = n1.num_states;

        add_table(&mut table, create_shifted_table(&(n1.table), 1u));
        add_table(&mut table, create_shifted_table(&(n2.table), m + 1u));

        let mut set = HashSet::new();
        set.insert(State(n1.entry + 1u));
        set.insert(State(n2.entry + m + 1u));

        table.insert((0u, None), set);

        PNFA::new(table, 0u)
    }


    pub fn optional(n: PNFA) -> PNFA {
        let mut table: TransitionTable = HashMap::new();
        add_table(&mut table, create_shifted_table(&(n.table), 1u));

        let mut set = HashSet::new();
        set.insert(State(n.entry + 1u));
        set.insert(Exit);

        table.insert((0u, None), set);

        PNFA::new(table, 0u)
    }
}


