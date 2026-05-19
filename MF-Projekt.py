# Operatory
# ~a  - negacja
# a & b - koniunkcja
# a | b - alternatywa
# a -> b - implikacja

import code


class LogicLang:
    # Ustalamy zbiór zmiennych, które będą używane w logice
    def __init__(self):
        self.variables = {}

    # Sprawdzamy czy dana wartość jest wyrażeniem logicznym
    def is_expression(self, value: str) -> bool:
        return any(op in value for op in ["&", "|", "~", "->"])
    
    # Przypisujemy wartość do zmiennej, sprawdzając czy jest to wyrażenie logiczne i konwertujemy ją do CNF
    def assign(self, name, value):
        if name not in self.variables:
            raise ValueError(f"Zmienna '{name}' nie istnieje") 
        value = self.to_cnf(value)
        self.variables[name] = value

        if value not in ("zero", "jeden") and not self.is_expression(value):
            raise ValueError("Dozwolone tylko zero, jeden albo wyrażenie logiczne")

    # Uruchamiamy kod, dzieląc go na linie i przetwarzając każdą linię, obsługując deklaracje zmiennych i przypisania
    def run(self, code: str):
        # Dzielimy kod na linie i przetwarzamy każdą linię
        lines = code.splitlines()
        # splitlines() dzieli tekst na linie, tworząc listę linii

        for line in lines:
            line = line.strip()
            # strip() usuwa białe znaki z początku i końca linii
            if not line:
                continue  # Pomijamy puste linie

            parts = line.split()

            # 🔥 DODANE: przypisanie poza var
            if "=" in line and parts[0] != "var":
                name, value = line.split("=", 1)
                self.assign(name.strip(), value.strip())
                continue

            # Deklarujemy zmienną
            if parts[0] == "var":
                # Gwarantujemy, że deklaracja jest poprawna (np. "var x" lub "var x = expression")
                if "=" not in line and len(parts) > 2:
                    raise ValueError(f"Nieprawidłowa deklaracja zmiennej: {line}")

                var_name = parts[1]

                if var_name in self.variables:
                    raise ValueError(f"Zmienna '{var_name}' już istnieje.")

                # Tutaj możemy przypisać None lub inną wartość domyślną, ponieważ zmienna została zadeklarowana, ale nie przypisano jej jeszcze wartości
                self.variables[var_name] = None

                # Jeżeli linia zawiera przypisanie, to zadajemy jej wartość/formułę logiczną
                if "=" in line:
                    _, value = line.split("=", 1)
                    self.assign(var_name, value.strip())

            else:
                raise ValueError(f"Nieznana instrukcja: {line}")

        return self
    
    # Funkcja zamieniająca implikację x -> y na ~x | y
    def eliminate_implication(self, expr: str) -> str:
        expr = expr.strip()

        if "->" not in expr:
            return expr

        left, right = expr.split("->", 1)

        left = left.strip()
        right = right.strip()

        if left.startswith("~"):
            new_left = left[1:]
        else:
            new_left = "~" + left

        return f"({new_left} | {right})"

    # Funkcja stosująca prawa de Morgana do wyrażenia logicznego, tzn. ~(x & y) = ~x | ~y oraz ~(x | y) = ~x & ~y 
    def apply_de_morgan(self, expr: str) -> str:
        expr = expr.strip()

        if expr.startswith("~(") and expr.endswith(")"):
            inside = expr[2:-1].strip()

            if "&" in inside:
                left, right = inside.split("&", 1)
                return f"~{left.strip()} | ~{right.strip()}"

            if "|" in inside:
                left, right = inside.split("|", 1)
                return f"~{left.strip()} & ~{right.strip()}"

        return expr

    # Funkcja stosująca prawa dustrybucji, tzn. x | (y & z) = (x | y) & (x | z) oraz x & (y | z) = (x & y) | (x & z)
    def distribute_or(self, expr: str) -> str:
        expr = expr.strip()

        if "|" in expr and "&" in expr:
            left, right = expr.split("|", 1)

            left = left.strip()
            right = right.strip()

            if right.startswith("(") and right.endswith(")") and "&" in right:
                inside = right[1:-1]
                b, c = inside.split("&", 1)

                return f"({left} | {b.strip()}) & ({left} | {c.strip()})"

        return expr
    
    # Funkcja konwertująca wyrażenie logiczne do postaci CNF, eliminując implikacje, stosując prawa de Morgana i prawa dystrybucji
    def to_cnf(self, expr: str) -> str:
        prev = None

        while prev != expr:
            prev = expr

            expr = self.eliminate_implication(expr)
            expr = self.apply_de_morgan(expr)
            expr = self.distribute_or(expr)

        return expr
    
    # Funkcja konwertująca wyrażenie logiczne w postaci CNF do formatu DIMACS, który jest standardowym formatem dla problemów SAT
    def to_dimacs(self, expr: str) -> str:
        expr = expr.strip()

        # Zbieramy zmienne
        vars_list = sorted(self.variables.keys())
        var_map = {v: i + 1 for i, v in enumerate(vars_list)}

        # Dzielimy całość na klauzule, które są oddzielone operatorem & - and
        clauses_raw = [c.strip() for c in expr.split("&")]

        clauses = []

        # Dla każdej klauzuli dzielimy ją na literały, które są oddzielone operatorem | - or
        for c in clauses_raw:
            c = c.replace("(", "").replace(")", "")
            literals = [l.strip() for l in c.split("|")]

            clause = []
            # Dla każdego literału sprawdzamy, czy jest negacją (zaczyna się od ~) i mapujemy go na odpowiednią liczbę całkowitą zgodnie z mapowaniem zmiennych
            for lit in literals:
                if lit.startswith("~"):
                    v = lit[1:]
                    clause.append(str(-var_map[v]))
                else:
                    clause.append(str(var_map[lit]))

            clauses.append(clause)

        # Tworzymy nagłówek w formacie DIMACS, który zawiera liczbę zmiennych i liczbę klauzul
        header = f"p cnf {len(var_map)} {len(clauses)}"
        
        body = []
        for cl in clauses:
            body.append(" ".join(cl) + " 0")

        return header + "\n" + "\n".join(body)


# Przykładowe użycie
logic = LogicLang()
code = """ var x
x = zero
var y
y = jeden
var z """
logic.run(code)
print(logic.variables)  # Output: {'x', 'y', 'z'}

expr = "(x | y) & (~x | z)"

print(logic.to_dimacs(expr))