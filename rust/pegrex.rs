use parse::re2post;

mod parse;
mod partialNFA;


fn main() {
    println!("{}", re2post("abc|d?e".to_string()));

}
