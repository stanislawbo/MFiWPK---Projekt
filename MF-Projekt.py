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
                if len(parts) >= 3:
                    raise ValueError(f"Nieprawidłowa deklaracja zmiennej: {line}")
                var_name = parts[1]
                if var_name in self.variables:
                    raise ValueError(f"Zmienna '{var_name}' już istnieje.")
                self.variables[var_name] = None
            elif "=" in line:
                name, value = line.split("=")
                name = name.strip()
                value = value.strip()
                self.assign(name, value)
                # Sprawdzamy, czy zmienna została już zadeklarowana
            else:
                raise ValueError(f"Nieznana instrukcja: {line}")
        
    


        return self
        
# Przykładowe użycie
logic = LogicLang()
code = """var x
var y
var z
x = jeden
y = zero
z = zero"""
logic.run(code)
print(logic.variables)  # Output: {'x', 'y', 'z'}

# Operatory
# ~a  - negacja
# a & b - koniunkcja
# a | b - alternatywa
# a -> b - implikacja
# a <-> b - równoważność

# Jako, że negacja, koniunkcja i alternatywa są jedynymi symbolami w postaci CNF, pozostaje rozpisac alternatywe i równoważnosc na koniunkcje i negacje.

def eliminate_implication(expr: str) -> str:
    expr = expr.strip()
    if "->" not in expr:
        return expr
    left, right = expr.split("->")
    left = left.strip()
    right = right.strip()
    if left.startswith("~"):
        new_left = left[1:]   # ~~x nie robimy tutaj uproszczeń
    else:
        new_left = "~" + left
    return f"{new_left} | {right}"

def eliminate_iff(expr: str) -> str:
    expr = expr.strip()

    if "<->" not in expr:
        return expr

    left, right = expr.split("<->")

    left = left.strip()
    right = right.strip()

    part1 = f"({left} & {right})"
    part2 = f"(~{left} & ~{right})"

    return f"{part1} | {part2}"

# Zmienne mogą być już deklarowane, potrzeba teraz jedynie aby były one definiowane.