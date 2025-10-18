# main.py
from lexer import scan


def main():
    ruta_fuente = "ejemplos/entrada.txt"
    with open(ruta_fuente, "r", encoding="utf-8") as f:
        codigo = f.read()

    tokens, errores = scan(codigo)

    # Tabla de tokens: Lexema, Token (código), Línea
    with open("Tokens.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<20}{'Token':<10}{'Línea':<8}\n")
        for t in tokens:
            f.write(f"{t.lexema:<20}{t.codigo:<10}{t.linea:<8}\n")


# Tabla de errores: Lexema, Descripción breve, Línea
    with open("Errores.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<25}{'Descripción':<80}{'Línea':<10}\n")
        for e in errores:
            f.write(f"{e.lexema:<25}{e.descripcion:<80}{e.linea:<10}\n")

    print("Análisis léxico completado.")

if __name__ == "__main__":
    main()
