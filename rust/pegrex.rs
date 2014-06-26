use parse::re2post;
use nfa::NFA;

mod parse;
mod nfa;
mod partialNFA;

fn run(n: &mut NFA, s: String) {
    println!("{}: {}", s, n.run_string(&s));
}

fn main() {
    let s = re2post("abc|d?e".to_string());
    println!("{}", s);
    if s.is_ok() {
        let res = NFA::compile(s.unwrap());
        if res.is_ok() {
            let mut n = res.unwrap();
            println!("n = {}", n);
            run(&mut n, "abc".to_string());
            run(&mut n, "e".to_string());
            run(&mut n, "de".to_string());
        }
    }
}
