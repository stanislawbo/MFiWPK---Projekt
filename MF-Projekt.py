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
            self.process_line(line)