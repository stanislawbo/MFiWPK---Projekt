counter = -1

def declare_variable(variable):
    """
    Deklaracja zmiennej, której można później używać w formułach logicznych
    :param variable: Nazwa zmiennej
    :return:
    """
    global counter
    Logical.variables[variable.name] = counter
    counter += 1

_PREC = {None: 4, '~': 3, '&': 2, '|': 1, '=>': 0}

class Logical:
    variables = {}
    def __init__(self, left = None, op = None, right = None, name = None, clauses = None):
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
            self.left = None
            self.op = None
            self.right = self
            self.name = name
            self.clauses = [self]
            declare_variable(self)

        elif op == '~':  # Negacje wyrażeń
            self.left = None
            self.op = op
            self.right = right
            self.name = name
            if self.right.op is None:
                self.clauses = [self]
            else:
                self.clauses = [] if clauses is None else clauses

        elif op == '|':
            if left == F:
                self.left = right.left
                self.op = right.op
                self.right = right.right
                self.name = right.name
                self.clauses = right.clauses
            elif right == F:
                self.left = left.left
                self.op = left.op
                self.right = left.right
                self.name = left.name
                self.clauses = left.clauses

            else:
                self.left = left
                self.op = '|'
                self.right = right
                self.name = name
                if len(left.clauses) == len(right.clauses) == 1:
                    self.clauses = [self]
                else:
                    self.clauses = []

        elif op in ('&', '=>'):  # Koniunkcje i implikacje
            self.left = left
            self.op = op
            self.right = right
            self.name = name
            self.clauses = [] if clauses is None else clauses

        else:
            print('Error: Something went wrong. Formula not created')

    def __str__(self):
        if self.op is None:
            return self.name
        if self.op == '~':
            if self.right.op == '~':
                return str(self.right.right)
            r = str(self.right)
            if self.right.op in ('&', '|', '=>'):
                r = f'({r})'
            return f'~{r}'

        cp = _PREC[self.op]
        l_str = f'({self.left})' if _PREC.get(self.left.op, 4) < cp else str(self.left)
        r_str = f'({self.right})' if _PREC.get(self.right.op, 4) < cp else str(self.right)

        return f'{l_str} {self.op} {r_str}'  # W pozostałych przypadkach rekurencyjnie wypisujemy lewą i prawą
                                                    # stronę formuły z operatorem pomiędzy nimi

    def __repr__(self):  # Wypisywanie zmiennych w tablicach, np. w atrybucie clauses
        return str(self)

    def string(self, cnf = False):
        """
        Definicja sposobu wypisywania formuł z możliwością wypisania w postaci CNF (bez zbędnych nawiasów)
        :param cnf: Czy formuła jest w postaci CNF; domyślnie False
        :return: Formuła w postaci napisu
        """
        if cnf:
            s = str(self.clauses[0])
            for clause in self.clauses[1:]:
                s += ('&' + str(clause))
            s = s.replace('(', '').replace(')', '').replace('&', ') & (')
            s = '(' + s + ')'
            print(s)
        else:
            str(self)

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
        return Logical(self, '|', other)

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
        return self.right if self.op == '~' else Logical(None, '~', self)  # Zwracamy odpowiednią formułę z uwzględnieniem przypadku podwójnej negacji

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
        Funkcja korzystająca z praw rozdzielności dla alternatywy formuł w postaci CNF
        :return: Formuła wejściowa w równoważnej postaci CNF
        """
        if self.op != '|':  # Przyjmuje tylko alternatywy
            print('System: Formuła musi być alternatywą')
            return self

        # elif len(self.clauses) == 1:  # Dodane, żeby pozbyć się błędu, potencjalnie niepotrzebne w przyszłości
        #     return self
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
        if self.op == '~':  # W przypadku, gdy formuła jest zanegowana ...
            if self.right.op == '~':  # Usuwamy podwójne negacje
                return Logical.remove_negation(self.right)
            if self.right.op is None:  # Jeżeli negacja zmiennej, zwracamy tę negację
                return self
            elif self.right.op == '&':  # Dla koniunkcji i alternatywy stosujemy prawa de Morgana i schodzimy rekurencyjnie
                return Logical.remove_negation(~self.right.left) | Logical.remove_negation(~self.right.right)
            elif self.right.op == '|':
                return Logical.remove_negation(~self.right.left) & Logical.remove_negation(~self.right.right)
            elif self.right.op == '=>':
                return Logical.remove_negation(self.right.left) & Logical.remove_negation(~self.right.right)
            else:
                raise Exception('Błąd: Niepoprawna formuła. Spróbuj najpierw usunąć implikacje')

        else:  # Jeżeli formuła nie jest zanegowana ...
            if self.op is None:  # Jeżeli to zmienna, zwracamy ją
                return self
            elif self.op == '&':  # Dla koniunkcji i alternatywy schodzimy rekurencyjnie
                return Logical.remove_negation(self.left) & Logical.remove_negation(self.right)
            elif self.op == '|':
                return Logical.remove_negation(self.left) | Logical.remove_negation(self.right)
            elif self.op == '=>':
                return Logical.remove_negation(~self.left) | Logical.remove_negation(self.right)
            else:
                raise Exception('Błąd: Niepoprawna formuła. Spróbuj najpierw usunąć implikacje')

    def to_cnf_body(self):
        """
        Funkcja pomocnicza do funkcji to_cnf. Przyjmuje jako argument formułę bez implikacji, w której negacje
        występują jedynie przy zmiennych. Zwraca jej postać CNF
        :return: Równoważna formuła w postaci CNF
        """
        if self.op == '&':  # Jeżeli jest ona koniunkcją, wystarczy obie strony sprowadzić do postaci CNF
            return Logical.to_cnf_body(self.left) & Logical.to_cnf_body(self.right)
        elif self.op == '|':  # Jeżeli jest alternatywą, to obie strony sprowadza do postaci CNF i łączy prawem rozdzielności
            return Logical.distribute_or(Logical.to_cnf_body(self.left) | Logical.to_cnf_body(self.right))
        else:  # Zwracamy pojedyncze zmienne lub ich negacje
            return self

    def to_cnf(self):
        """
        Funkcja przekształcająca formułę do postaci CNF
        :return: Równoważna formuła w postaci CNF
        """
        formula = Logical.remove_negation(Logical.eliminate_implication(self))
        return Logical.to_cnf_body(formula)

    def literals(self):
        if len(self.clauses) != 1:
            print(f"Błąd: Podana formuła ({self}) nie jest klauzulą")
            return set()
        elif self.op is None or self.op == '~':
            return {self}
        else:
            return Logical.literals(self.right).union(Logical.literals(self.left))

    def to_dimacs(self):
        if self.clauses == []:
            print("Błąd: Formuła nie jest w postaci CNF")
        else:
            simplified = Logical.simplify_clauses(self)
            dimacs_body = ""
            total_literals = set()
            for clause in simplified.clauses:
                literals = Logical.literals(clause)
                dimacs_body += "\n"
                for l in literals:
                    if l.op is None:
                        dimacs_body += str(Logical.variables[l.name]) + " "
                        if l.name not in total_literals:
                            total_literals.add(l.name)
                    elif l.op == '~':
                        dimacs_body += str(-Logical.variables[(~l).name]) + " "
                        if (~l).name not in total_literals:
                            total_literals.add((~l).name)
                dimacs_body += "0"
            dimacs_header = f"p cnf {len(self.clauses)} {len(total_literals)}"
            dimacs_content = dimacs_header + dimacs_body
            with open("dimacs.txt", "w") as f:
                f.write(dimacs_content)
            
    def simplify_clauses(self):
        """
        Upraszcza klauzule CNF:
        - usuwa klauzule zawierające zmienną i jej negację (tautologie)
        - usuwa duplikaty literałów w klauzuli
        """
        new_clauses = []
        for clause in self.clauses:
            literals = Logical.literals(clause)
            tautology = False
            # zbierz wszystkie literały z klauzuli
            new_clause = F
            for l in literals:
                if ~l in literals:
                    tautology = True
                    break
                new_clause |= l

            if not tautology:
                new_clauses.append(new_clause)

        self.clauses = new_clauses  # usuń puste
        return self
            

T = Logical(name = 'True')
F = Logical(name = 'False')
w, x, y, z = Logical(name = 'w'), Logical(name = 'x'), Logical(name = 'y'), Logical(name = 'z')

print('Test 0:', Logical.to_cnf(x))
print('Test 0.(9)8:', Logical.to_cnf((x | y) & z))
print('Test 0.(9):', Logical.to_cnf((x & y) | z))
print('Test 1:', Logical.to_cnf(~(x | (y & z))))
print('Test 2:', Logical.to_cnf((x & y) | (~x & z)))
print('Test 3:', Logical.to_cnf(x >> (y >> z)))

while True:
    cmd_full = input('')  # Wczytywanie inputu użytkownika z konsoli ...
    cmd = cmd_full.split()  # i dzielenie na części rozdzielone spacjami

    if cmd[0] == 'var':  # Jeżeli pierwszą częścią jest słowo kluczowe "var", użytkownik chce zadeklarować zmienne
        if len(cmd) == 2:
            if not cmd[1].isidentifier() or cmd[1] in ('and', 'or', 'not', 'True', 'False', 'T', 'F'):
                print('Błąd: Niepoprawna nazwa zmiennej')
            else:
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
            exec(f'Logical.string({cmd[1]}, True)')
        elif len(cmd) == 2:  # W przeciwnym przypadku wypisuje ją normalnie
            exec(f'print({cmd[1]})')
        else:  # Niepoprawna składnia prowadzi do błędu
            print('System: Błąd składni')

    elif cmd[0] == 'end':  # Jeżeli polecenie to "end", użytkownik chce zakończyć pracę z programem
        print('System: Ending current run')
        break

    elif len(cmd) > 2 and cmd[1] == '=':  # W tym przypadku użytkownik chce utworzyć formułę logiczną
        formula = ''.join(cmd[2:]).replace('=>', '>>')  # Podmieniamy w inpucie "=>" na ">>"
        try:  # Wykonujemy podmieniony input jako polecenie, żeby stworzyć formułę
            exec(f'{cmd[0]} = {formula}')
            print('System: Utworzono formułę')
        except NameError as e:
            missing = str(e).split("'", 2)[1]
            print(f'Błąd: Zmienna {missing} nie jest zadeklarowana')
        except SyntaxError:
            print('Błąd: Sprawdź nawiasy')
        except TypeError:
            print('Błąd: Niepoprawny operator')
    
    elif cmd[:2] == ['to', 'cnf'] and len(cmd) == 3:
        exec(f'{cmd[2]} = Logical.to_cnf({cmd[2]})')
        print('System: Zapisano formułę w postaci CNF')

    elif cmd[:2] == ['to', 'dimacs'] and len(cmd) == 3:
        exec(f'Logical.to_dimacs({cmd[2]})')
        print('System: Zapisano formułę do pliku')

    elif cmd[0] in ['help', '?'] and len(cmd) == 1:  # Jeżeli polecenie to "help" lub "?", wyświetla pomoc dotyczącą możliwych poleceń
        print('Użyj \'var <nazwa zmiennej>\', żeby zadeklarować zmienną')
        print('Użyj \'var <nazwa zmiennej z indeksem> for <indeks> n to m\', żeby zadeklarować kilka zmiennych naraz\n'
              '    Przykład: var x_i for i 1 to 5')
        print('Użyj \'print <nazwa zmiennej / formuły>\', żeby ją wypisać')
        print('Użyj \'end\', żeby zamknąć program')

    else:
        print('System: Nieznane polecenie')

"""
Do zrobienia:
 > dodać możliwość wywołania to_cnf przez użytkownika
 > dodanie funkcji tłumaczącej formuły w postaci CNF do formatu dimacs
  
 > Na koniec:
  - testy poprawności działania
  - zaktualizować polecenie "help"
  - zrobić plik .exe?
"""
