import random

counter = 1
def declare_variable(variable_name):
    """
    Creates a new variable to use in logical formulas
    :param variable_name: Variable name
    :return: Null
    """
    global counter
    Logical.variables[variable_name] = counter
    counter += 1

class Logical:
    variables = {}
    def __init__(self, left = None, op = None, right = None, name = None, clauses = []):
        if op is None:
            declare_variable(self)
            self.left = None
            self.op = None
            self.right = self
            self.name = name
            self.clauses = [self]

        elif op not in ('&', '|', '=>', '~'):
            print('Can\'t create formulas without operators / unknown operator')

        elif op == '~':
            self.left = None
            self.op = op
            self.right = right
            self.name = name
            self.clauses = clauses

        elif op in ('|', '&', '=>'):
            self.left = left
            self.op = op
            self.right = right
            self.name = name
            self.clauses = clauses

        else:
            print('Error: Something went wrong. Formula not created')

    def __str__(self, cnf = False):
        # Need to fix extra parentheses in multi-level formulas
        if cnf:
            cnf_form = self.clauses[0]
            for clause in self.clauses[1]:
                cnf_form = cnf_form | clause
            return cnf_form

        if self.op is None:
            return self.name
        if self.op == '~':
            if self.right.op == '~':
                return str(self.right.right)
            return f'~{self.right}'
            return f'~{self.right}' if self.right.right == self.right else f'~({self.right})'
        return f'({self.left} {self.op} {self.right})'

    def __repr__(self):
        return str(self)

    def __and__(self, other):
        if self == T:
            return other
        if len(self.clauses) > 0 and len(other.clauses) > 0:
            return Logical(self, '&', other, clauses = (self.clauses + other.clauses))
        return Logical(self, '&', other)

    def __or__(self, other):
        if self == F:
            return other
        if len(self.clauses) == len(other.clauses) == 1:
            return Logical(self, '|', other, clauses = [Logical(self.clauses[0], '|', other.clauses[0])])
        return Logical(self, '|', other)

    def __rshift__(self, other):
        return Logical(self, '=>', other)

    def __invert__(self):
        if self in Logical.variables:
            return Logical(None, '~', self, clauses = [Logical(None, '~', self.clauses[0])])
        elif self.op == '~' and self.right in Logical.variables:
            return Logical(None, None, self.right, name = self.right.right.name, clauses = [Logical(None, None, None, self.right.clauses[0])])
        return self.right if self.op == '~' else Logical(None, '~', self)

    def eliminate_implication(self):
        if self.op is None:
            return self
        elif self.op == '&':
            return Logical.eliminate_implication(self.left) & Logical.eliminate_implication(self.right)
        elif self.op == '|':
            return Logical.eliminate_implication(self.left) | Logical.eliminate_implication(self.right)
        elif self.op == '~':
            return ~Logical.eliminate_implication(self.right)
        return ~Logical.eliminate_implication(self.left) | Logical.eliminate_implication(self.right)

    def distribute_or(self):
        if len(self.clauses) == 1:
            return self
        # Requires the formula to be in a form CNF | CNF
        res = T
        for cl in self.left.clauses:
            for cr in self.right.clauses:
                new_clause = cl | cr
                res &= new_clause
        return res

    def distribute_orr(self):
        # Requires the formula to be in a form CNF | CNF
        # Błąd z podwajaniem jedynej pary klauzul, jeżelijest tylko jedna
        print('Formula to distribute or:', self)
        res = self.left.clauses[0] | self.right.clauses[0]
        clauses = [self.left.clauses[0] | self.right.clauses[0]]
        for i in range(len(self.left.clauses)):
            for j in range(len(self.right.clauses)):
                if (i == 0 and j == 0) or (i == len(self.left.clauses) - 1 and j == len(self.right.clauses) - 1):
                    continue
                res = res & (self.left.clauses[i] | self.right.clauses[j])
                clauses.append(self.left.clauses[i] | self.right.clauses[j])
        clauses.append(self.left.clauses[-1] | self.right.clauses[-1])
        return Logical(res, '&', self.left.clauses[-1] | self.right.clauses[-1], clauses = clauses)

    def remove_negation(self):
        # Requires the formula to be in a form ~(x | y) or ~(x & y)
        if self.op != '~':
            return self
        elif self.right.op is None:
            return self
        elif self.right.op == '&':
            return ~self.right.left | ~self.right.right
        elif self.right.op == '|':
            return ~self.right.left & ~self.right.right
        else:
            print(self)
            raise Exception('Can\'t handle that formula')

    def to_cnf(self):
        no_impl = Logical.eliminate_implication(self)
        # Going from outer-most symbol, if it's a:
        # > & - leave as it is, convert left and right to cnf
        if no_impl.op == '&':
            return Logical.to_cnf(no_impl.left) & Logical.to_cnf(no_impl.right)
        elif no_impl.op == '|':
            return Logical.distribute_or(Logical.to_cnf(no_impl.left) | Logical.to_cnf(no_impl.right))
        elif no_impl.op == '~':
            if no_impl.right.op is None:
                return no_impl
            return Logical.to_cnf(Logical.remove_negation(no_impl))
        else:
            return no_impl

T = Logical(name = 'True')
F = Logical(name = 'False')
x, y, z = Logical(name = 'x'), Logical(name = 'y'), Logical(name = 'z')
# phi = Logical(A, '=>', K, name = 'phi')
# print('phi = (x & y) => (z | ~x)')
# phi = x | y >> (z & ~x)
# print('phi =', phi)
#
print('Test 0:', Logical.to_cnf(x))
print('Test 0.(9)8:', Logical.to_cnf((x | y) & z))
print('Test 0.(9):', Logical.to_cnf((x & y) | z))
print('Test 1:', Logical.to_cnf(~(x | (y & z))))
print('Test 2:', Logical.to_cnf((x & y) | (~x & z)))
print('Test 3:', Logical.to_cnf(x >> (y >> z)))
print('Test 3.1:', Logical.to_cnf(x >> (~y >> z)))
# print((~x).clauses, (~y | z).clauses)

while True:
    cmd_full = input('')
    cmd = cmd_full.split()
    if cmd[0] == 'var':
        if len(cmd) == 2:
            exec(f'{cmd[1]} = Logical(name = \'{cmd[1]}\')')
            print(f'System: Declared variable {cmd[1]}')
        elif cmd[2] == 'for' and cmd[5] == 'to' and len(cmd) == 7:
            range_l = int(cmd[4])
            range_h = int(cmd[6])
            if range_h < range_l:
                print('System: Incorrect range')
                continue
            idx = cmd[3]
            idx_in_var = cmd[1].find(idx)
            if idx_in_var == -1:
                print('System: Variable not indexed with given string')
                continue
            vars = [cmd[1][:idx_in_var] + str(i) + cmd[1][idx_in_var + len(cmd[3]):] for i in
                    range(range_l, range_h + 1)]
            for var in vars:
                exec(f'{var} = Logical(name = \'{var}\')')
            print(f'System: Declared variables {vars[0]} to {vars[-1]}')

    elif cmd[0] == 'print':
        if len(cmd) == 3 and cmd[2] == 'cnf':
            exec(f'print({cmd[1]}, True)')
        elif len(cmd) == 2:
            exec(f'print({cmd[1]})')
        else:
            print('Error')

    elif cmd[0] == 'end':
        print('System: Ending current run')
        break

    elif len(cmd) > 2 and cmd[1] == '=':
        ''' ----------========== To prawie na pewno da się lepiej ==========---------- '''
        formula = ''.join(cmd[2:]).replace('=>', '>>')
        print(formula)
        bracket_count = 0
        correct_formula = False
        for i in range(len(formula)):
            if formula[i] == '(':
                bracket_count += 1
            elif formula[i] == ')':
                bracket_count -= 1

            if bracket_count == 0:
                correct_formula = True
                formula_left = formula[:i + 1]
                if formula[i + 1] in ('&', '|'):
                    formula_op = formula[i + 1]
                    formula_right = formula[i + 2:]
                elif formula[i + 1 : i + 3] == '>>':
                    formula_op = '=>'
                    formula_right = formula[i + 3:]
                break
        if not correct_formula:
            print('Error: Check parenthesis')
            break
        # print(formula_left, formula_op, formula_right)
        line = f'{cmd[0]} = Logical({formula_left}, \'{formula_op}\', {formula_right})'
        print(line)
        try:
            exec(line)
            print('Created a formula')
        except NameError as e:
            missing = str(e).split("'", 2)[1]
            print(f'Error: Variable {missing} not declared')

    elif cmd[0] in ['help', '?'] and len(cmd) == 1:
        print('Use \'var <variable_name>\' to declare variables')
        print('Use \'var <indexed_variable_name> for <idx> n to m\' to declare many variables at once\n'
              '    Example: var x_i for i 1 to 5')
        print('Use \'print <variable / formula name>\' to print it')
        print('Use \'end\' to terminate the program')

    else:
        #exec(cmd_full)
        print('System: Unknown command')
