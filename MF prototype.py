counter = 1
def declare_variable(variable_name):
    """
    Deklaracja zmiennej, której można później używać w formułach logicznych
    :param variable_name: Nazwa zmiennej
    :return:
    """
    global counter
    Logical.variables[variable_name] = counter
    counter += 1

class Logical:
    variables = {}
    def __init__(self, left = None, op = None, right = None, name = None, clauses = []):
        """
        Definicja wyrażenia logicznego
        :param left: Lewa strona wyrażenia (pusta w przypadku negacji i wyrażeń będących jedną zmienną)
        :param op: Operator, jeden z &, |, =>, ~ (puste w przypadku wyrażeń będących jedną zmienną)
        :param right: Prawa strona wyrażenia (negowana formuła w przypadku negacji i zmienna dla wyrażeń będących jedną zmienną)
        :param name: Nazwa formuły, potrzebna tylko dla pojedynczych zmiennych, do ich wypisywania
        :param clauses: Klauzule, które wchodzą w skład formuły
        """

        if op not in ('&', '|', '=>', '~', None):
            print('System: Nieznany operator')

        elif op is None:  # Wyrażenia będące pojedynczą zmienną
            declare_variable(self)
            self.left = None
            self.op = None
            self.right = self
            self.name = name
            self.clauses = [self]

        elif op == '~':  # Negacje wyrażeń
            self.left = None
            self.op = op
            self.right = right
            self.name = name
            self.clauses = clauses

        elif op in ('|', '&', '=>'):  # Koniunkcje, alternatywy i implikacje
            self.left = left
            self.op = op
            self.right = right
            self.name = name
            self.clauses = clauses

        else:
            print('Error: Something went wrong. Formula not created')

    def __str__(self, cnf = False):
        """
        Definicja sposobu wypisywania formuł
        :param cnf: Czy formuła jest w postaci CNF; domyślnie False
        :return: Formuła w postaci napisu
        """
        # Need to fix extra parentheses in multi-level formulas
        if cnf:
            cnf_form = self.clauses[0]
            for clause in self.clauses[1]:
                cnf_form = cnf_form | clause
            return cnf_form

        if self.op is None:  # Pojedyncze zmienne wypisujemy jako ich atrybuty "name"
            return self.name
        if self.op == '~':  # W przypadku negacji...
            if self.right.op == '~':  # jeżeli negowane wyrażenie samo w sobie jest negacją, wyrzucamy obie te negacje...
                return str(self.right.right)
            return f'~{self.right}'  # a jeżeli nie, to przed napisem formuły doklejamy znak ~

        return f'({self.left} {self.op} {self.right})'  # W pozostałych przypadkach rekurencyjnie wypisujemy lewą i prawą
                                                        # stronę formuły z operatorem pomiędzy nimi

    def __repr__(self):  # Wypisywanie zmiennych w tablicach, np. w atrybucie clauses
        return str(self)

    def __and__(self, other):
        """
        Nadpisanie operatora "&" jako spójnika logicznego "and"
        :param other: Druga formuła, która ma zostać połączona z pierwszą za pomocą spójnika "&"
        :return: Koniunkcja obu formuł
        """
        if self == T:  # Koniunkcja z prawdą nie zmienia wartości formuły
            return other

        if len(self.clauses) > 0 and len(other.clauses) > 0:  # Jeżeli obie formuły są w postaci CNF, to ich koniunkcja również
            return Logical(self, '&', other, clauses = (self.clauses + other.clauses))  # a klauzule koniunkcji to klauzule
                                                                                            # z obu formuł
        return Logical(self, '&', other)  # W pozostałych przypadkach zwraca koniunkcję bez dodatków

    def __or__(self, other):
        """
        Nadpisanie operatora "|" jako spójnika logicznego "or"
        :param other: Druga formuła, która ma zostać połączona z pierwszą za pomocą spójnika "|"
        :return: Alternatywa obu formuł
        """
        if self == F:  # Alternatywa z fałszem nie zmienia wartości formuły
            return other

        if len(self.clauses) == len(other.clauses) == 1:  # Alternatywa klauzul jest jedną klauzulą
            return Logical(self, '|', other, clauses = [Logical(self.clauses[0], '|', other.clauses[0])])

        return Logical(self, '|', other)  # W pozostałych przypadkach zwraca alternatywę bez dodatków

    def __rshift__(self, other):
        """
        Nadpisanie operatora ">>" jako spójnika logicznego modelującego implikację
        :param other: Następnik implikacji
        :return: Implikacja obu formuł
        """
        return Logical(self, '=>', other)

    def __invert__(self):
        """
        Nadpisanie operatora "~" jako spójnika logicznego modelującego implikację
        :return: Negacja formuły
        """
        if self in Logical.variables:  # Jeżeli negujemy zmienną, to jej negacja jest również klauzulą
            return Logical(None, '~', self, clauses = [Logical(None, '~', self.clauses[0])])
        
        elif self.op == '~' and self.right in Logical.variables:  # Jeżeli negujemy negację zmiennej, zwraca tę zmienną
            return self.right
        
        return self.right if self.op == '~' else Logical(None, '~', self)  # W pozostałych przypadkach zwracamy negację
                                                                                    # z uwzględnieniem przypadku podwójnej negacji

    def eliminate_implication(self):
        """
        Funkcja zamieniająca w formule wszystkie implikacje za pomocą alternatyw
        :return: Równoważna postać formuły bez użycia operatora implikacji
        """
        if self.op is None:  # Zwracamy zmienne
            return self
        elif self.op == '&':  # Koniunkcje, alternatywy i negacje traktujemy rekurencyjnie
            return Logical.eliminate_implication(self.left) & Logical.eliminate_implication(self.right)
        elif self.op == '|':
            return Logical.eliminate_implication(self.left) | Logical.eliminate_implication(self.right)
        elif self.op == '~':
            return ~Logical.eliminate_implication(self.right)
        
        # W pozostałym przypadku (implikacja), zastępujemy formułę "X => Y" przez "~X | Y" i rekurencyjnie przechodzimy głebiej
        return ~Logical.eliminate_implication(self.left) | Logical.eliminate_implication(self.right)

    def distribute_or(self):
        """
        Funkcja korzystająca z praw rozdzielności dla koniunkcji formuł w postaci CNF
        :return: Formuła wejściowa w równoważnej postaci CNF
        """
        if len(self.clauses) == 1:  # Dodane, żeby pozbyć się błędu, potencjalnie niepotrzebne w przyszłości
            return self
        res = T  # Startujemy z pustej formuły...
        for cl in self.left.clauses:
            for cr in self.right.clauses:
                new_clause = cl | cr  # i dla każdej pary klauzul z lewej i prawej części dorzucamy
                res &= new_clause     # ich alternatywę do wyniku
        return res

    def remove_negation(self):
        """
        Funkcja przerzucająca w formule negacje na poziom pojedynczych zmiennych
        :return: Równoważna postać formuły wejściowej, z negacjami tylko bezpośrednio przy zmiennych
        """
        if self.op != '~':  # Usuwamy podwójne negacje
            return self
        elif self.right.op is None:  # Jeżeli negacja zmiennej, zwracamy ją
            return self
        elif self.right.op == '&':  # Dla koniunkcji i alternatywy stosujemy prawa de Morgana
            return ~self.right.left | ~self.right.right
        elif self.right.op == '|':
            return ~self.right.left & ~self.right.right
        else:
            raise Exception('Błąd: Niepoprawna formuła. Spróbuj najpierw usunąć implikacje')# Mak

    def to_cnf(self):
        """
        Funkcja przekształcająca formułę do postaci CNF
        :return: Równoważna formuła w postaci CNF
        """
        no_impl = Logical.eliminate_implication(self)  # Usuwamy implikacje z formuły
        # Przechodzi rekurencyjnie po formule
        if no_impl.op == '&':  # Jeżeli jest ona koniunkcją, wystarczy obie strony sprowadzić do postaci CNF
            return Logical.to_cnf(no_impl.left) & Logical.to_cnf(no_impl.right)
        elif no_impl.op == '|':  # Jeżeli jest alternatywą, to obie strony sprowadza do postaci CNF i łączy prawem rozdzielności
            return Logical.distribute_or(Logical.to_cnf(no_impl.left) | Logical.to_cnf(no_impl.right))
        elif no_impl.op == '~':  # Jeżeli jest negacją, to...
            if no_impl.right.op is None:  # albo jest negacją zmiennej i w takim przypadku zwraca tę negację, ...
                return no_impl
            return Logical.to_cnf(Logical.remove_negation(no_impl))  # albo sprowadza do CNF po przełożeniu negacji na niższy poziom
        else:
            return no_impl  # Zwracamy pojedyncze zmienne

T = Logical(name = 'True')
F = Logical(name = 'False')
x, y, z = Logical(name = 'x'), Logical(name = 'y'), Logical(name = 'z')

print(~(~y))

while True:
    cmd_full = input('')  # Wczytywanie inputu użytkownika z konsoli ...
    cmd = cmd_full.split()  # i dzielenie na części rozdzielone spacjami
    
    if cmd[0] == 'var':  # Jeżeli pierwszą częścią jest słowo kluczowe "var", użytkownik chce zadeklarować zmienne
        if len(cmd) == 2:  # Jeżeli użytkownik deklaruje tylko jedną zmienną, nadajemy jej nazwę taką, jak podał użytkownik
            exec(f'{cmd[1]} = Logical(name = \'{cmd[1]}\')')
            print(f'System: Zadeklarowano zmienną {cmd[1]}')
            
        elif cmd[2] == 'for' and cmd[5] == 'to' and len(cmd) == 7:  # Jeżeli użytkownik chce zadeklarować kilka zmiennych naraz ...
            range_l = int(cmd[4])  # zczytujemy granice indeksownia
            range_h = int(cmd[6])
            if range_h < range_l:  # Sprawdzenie poprawności zakresu
                print('System: Niepoprawny zakres')
                continue
            idx = cmd[3]  # To słowo służy jako indeks i będzie nadpisane liczbami z podanego zakresu
            idx_in_var = cmd[1].find(idx)
            if idx_in_var == -1:  # Podany indeks musi być obecny w nazwie zmiennej
                print('System: Variable not indexed with given string')
                continue
            # Jeżeli wszystko pasuje, tworzymy tablicę nazw zmiennych ...
            vars = [cmd[1][:idx_in_var] + str(i) + cmd[1][idx_in_var + len(cmd[3]):] for i in range(range_l, range_h + 1)]
            for var in vars:  # i deklarujemy każdą z osobna
                exec(f'{var} = Logical(name = \'{var}\')')
            print(f'System: Zadeklarowano zmienne {vars[0]}, ..., {vars[-1]}')
            
        else:  # Niepoprawna składnia prowadzi do błędu
            print('System: Niepoprawna składnia')

    elif cmd[0] == 'print':  # Jeżeli polecenie zaczyna się od słowa kluczowego "print", użytkownik chce wypisać formułę
        if len(cmd) == 3 and cmd[2] == 'cnf':  # Jeżeli chce, wypisuje ją w postaci CNF
            exec(f'print({cmd[1]}, True)')
        elif len(cmd) == 2:  # W przeciwnym przypadku wypisuje ją normalnie
            exec(f'print({cmd[1]})')
        else:  # Niepoprawna składnia prowadzi do błędu
            print('System: Błąd składni')

    elif cmd[0] == 'end':  # Jeżeli polecenie to "end", użytkownik chce zakończyć pracę z programem
        print('System: Ending current run')
        break

    elif len(cmd) > 2 and cmd[1] == '=':  #  tym przypadku, użytkownik chce utorzyć formułę logiczną
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

    elif cmd[0] in ['help', '?'] and len(cmd) == 1:  # Jeżeli polecenie to "help" lub "?", wyświetla pomoc dotyczącą możliwych poleceń
        print('Użyj \'var <nazwa zmiennej>\', żeby zadeklarować zmienną')
        print('Użyj \'var <nazwa zmiennej z indeksem> for <indeks> n to m\', żeby zadeklarować kilka zmiennych naraz\n'
              '    Przykład: var x_i for i 1 to 5')
        print('Użyj \'print <nazwa zmiennej / formuły>\', żeby ją wypisać')
        print('Użyj \'end\', żeby zamknąć program')

    else:
        print('System: Nieznane polecenie')
        
"""
Do zrobienia
 > rekurencyjna wersja remove_negation
 > usunięcie powielonych nawiasów przy wypisywaniu formuł
 > poprawne wypisywanie formuł w postaci CNF
 > dodać implikacje do remove_negation
 > zoptymalizować tworzenie formuł po inpucie użytkownika
"""
