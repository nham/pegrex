
// We're assuming that everything that's needed is actally on the stacks.
// If not, unwrap() will fail at runtime.
fn apply_top(sstack: &mut Vec<String>, cstack: &mut Vec<char>) {
    let pop1 = sstack.pop().unwrap();
    let mut pop2 = sstack.pop().unwrap().append(pop1.as_slice());
    pop2.push_char(cstack.pop().unwrap());
    sstack.push(pop2);
}

fn apply_all(sstack: &mut Vec<String>, cstack: &mut Vec<char>) {
    while !cstack.is_empty() {
        apply_top(sstack, cstack);
    }
}


pub fn is_op(c: char) -> bool {
    c == '.' || c == '|' || c == '?' || c == '*' || c == '+'
}

pub fn re2post(s: &String) -> Result<String, &str> {
    let mut operator_stack: Vec<char> = vec!();
    let mut operand_stack: Vec<String> = vec!();

    for c in s.as_slice().chars() {
        if !is_op(c) {

            // check if we should insert concat op first
            if operand_stack.len() - operator_stack.len() > 0 {
                while {
                    let size = operator_stack.len();
                    size > 0 && *operator_stack.get(size - 1) != '|'
                } {
                    apply_top(&mut operand_stack, &mut operator_stack);
                }

                operator_stack.push('.');

            }

            operand_stack.push(c.to_str())

        } else {
            // We assume that we cannot see '.' here
            if c != '|' {
                match operand_stack.pop() {
                    Some(mut operand) => { 
                        operand.push_char(c); 
                        operand_stack.push(operand);
                    },

                    None => { 
                        return Err("Input expression is malformed");
                    }
                }
            } else {
                apply_all(&mut operand_stack, &mut operator_stack);
                operator_stack.push(c);
            }
        }
    }

    apply_all(&mut operand_stack, &mut operator_stack);
    Ok(operand_stack.pop().unwrap()) // not sure if this could actually fail
}

