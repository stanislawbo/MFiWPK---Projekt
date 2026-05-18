class LogicLang:
    # Ustalamy zbiór zmiennych, które będą używane w logice
     def __init__(self):
        self.variables = set()

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
                var_name = parts[1]
                self.variables.add(var_name)
                if len(parts) >= 3:
                    raise ValueError(f"Nieprawidłowa deklaracja zmiennej: {line}")
                name = parts[1]
                
                # Sprawdzamy, czy zmienna została już zadeklarowana
                if name in self.variables:
                    raise ValueError(f"Zmienna '{name}' już istnieje.")
                
                self.variables.add(name)

            else:
                raise ValueError(f"Nieznana instrukcja: {line}")
            
            return self