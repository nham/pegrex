def ops():
    return ['|', '.', '?', '+', '*']

def re2post(s):
    operator_stack = []
    operand_stack = []


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
        if c not in ops():
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


