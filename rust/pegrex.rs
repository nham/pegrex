use parse::re2post;
use nfa::NFA;

mod parse;
mod nfa;
mod partialNFA;


fn main() {
    let s = re2post("abc|d?e".to_string());
    println!("{}", s);
    if s.is_ok() {
        let n = NFA::compile(s.unwrap());
    }
}
