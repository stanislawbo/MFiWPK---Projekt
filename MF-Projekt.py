from ast import expr
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
        if self.is_expression(value):
            print(f"[DEBUG] {name} jest wyrażeniem")
        else:
            print(f"[DEBUG] {name} jest wartością")
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
        while "->" in expr:
            left, right = expr.split("->")
            left = left.strip()
            right = right.strip()
        if left.startswith("~"):
            new_left = left[1:]   # ~~x nie robimy tutaj uproszczeń
        else:
            new_left = "~" + left
        expr = f"({new_left} | {right})"
        return expr

    def apply_de_morgan(expr: str) -> str:
        expr = expr.strip()

        # ~(A & B)
        if expr.startswith("~(") and expr.endswith(")"):
            inside = expr[2:-1].strip()

        # koniunkcja
        if "&" in inside:
            left, right = inside.split("&", 1)
            return f"~{left.strip()} | ~{right.strip()}"

        # alternatywa
        if "|" in inside:
            left, right = inside.split("|", 1)
            return f"~{left.strip()} & ~{right.strip()}"

        return expr

    def distribute_or(expr: str) -> str:
        expr = expr.strip()

        # A | (B & C)
        if "|" in expr and "&" in expr:
            left, right = expr.split("|", 1)

        left = left.strip()
        right = right.strip()

        # tylko przypadek: (B & C)
        if right.startswith("(") and right.endswith(")") and "&" in right:
            inside = right[1:-1]
            b, c = inside.split("&", 1)

            return f"({left} | {b.strip()}) & ({left} | {c.strip()})"

        return expr
        


# Przykładowe użycie
logic = LogicLang()
code = """var x
var y
var z = x & y
x = jeden
y = zero"""
logic.run(code)
print(logic.variables)  # Output: {'x', 'y', 'z'}

# Operatory
# ~a  - negacja
# a & b - koniunkcja
# a | b - alternatywa
# a -> b - implikacja
# a <-> b - równoważność

# Jako, że negacja, koniunkcja i alternatywa są jedynymi symbolami w postaci CNF, pozostaje rozpisac alternatywe i równoważnosc na koniunkcje i negacje.
# Zmienne mogą być już deklarowane, potrzeba teraz jedynie aby były one definiowane.