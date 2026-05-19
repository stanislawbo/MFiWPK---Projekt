from ast import expr
from email import header
from os import name


class LogicLang:
    # Ustalamy zbiór zmiennych, które będą używane w logice
    def __init__(self):
        self.variables = {}

    def is_expression(self, value: str) -> bool:
        return any(op in value for op in ["&", "|", "~", "->", "<->"])

    def assign(self, name, value):
        if name not in self.variables:
            raise ValueError(f"Zmienna '{name}' nie istnieje") 
        value = self.to_cnf(value)
        self.variables[name] = value

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

            # Deklarujemy zmienną
            if parts[0] == "var":
                if "=" not in line and len(parts) > 2:
                    raise ValueError(f"Nieprawidłowa deklaracja zmiennej: {line}")
                var_name = parts[1]
                if var_name in self.variables:
                    raise ValueError(f"Zmienna '{var_name}' już istnieje.")
                self.variables[var_name] = None

                if "=" in line:
                    _,  value = line.split("=", 1)
                    self.assign(var_name, value.strip())    
            elif "=" in line:
                name, value = line.split("=")
                name = name.strip()
                value = value.strip()
                self.assign(name, value)
                # Sprawdzamy, czy zmienna została już zadeklarowana
            else:
                raise ValueError(f"Nieznana instrukcja: {line}")
        return self
    
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
        
    def to_cnf(self, expr: str) -> str:
        expr = self.eliminate_implication(expr)
        expr = self.apply_de_morgan(expr)

        prev = None
        while prev != expr:
            prev = expr
            expr = self.distribute_or(expr)

        return expr
    
    def to_dimacs(self, expr: str) -> str:
        expr = expr.strip()

        # 1. zbierz zmienne
        vars_list = sorted(self.variables.keys())
        var_map = {v: i + 1 for i, v in enumerate(vars_list)}

        # 2. CNF → klauzule (AND dzieli)
        clauses_raw = [c.strip() for c in expr.split("&")]

        clauses = []

        for c in clauses_raw:
            c = c.replace("(", "").replace(")", "")
            literals = [l.strip() for l in c.split("|")]

            clause = []
            for lit in literals:
                if lit.startswith("~"):
                    v = lit[1:]
                    clause.append(str(-var_map[v]))
                else:
                    clause.append(str(var_map[lit]))

            clauses.append(clause)

        header = f"p cnf {len(var_map)} {len(clauses)}"

        body = []
        for cl in clauses:
            body.append(" ".join(cl) + " 0")

        return header + "\n" + "\n".join(body)


# Przykładowe użycie
logic = LogicLang()
code = """var x
var y
var z
"""
logic.run(code)
print(logic.variables)  # Output: {'x', 'y', 'z'}

# Operatory
# ~a  - negacja
# a & b - koniunkcja
# a | b - alternatywa
# a -> b - implikacja

# Jako, że negacja, koniunkcja i alternatywa są jedynymi symbolami w postaci CNF, pozostaje rozpisac alternatywe na koniunkcje i negacje.

expr = "(x | y) & (~x | z)"

print(logic.to_dimacs(expr))