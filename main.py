# main.py
from lexer import scan
import sys


def main():
    # Default file if no argument provided
    if len(sys.argv) > 1:
        ruta_fuente = sys.argv[1]
    else:
        ruta_fuente = "ejemplos/prueba5.txt"
        
    with open(ruta_fuente, "r", encoding="utf-8") as f:
        codigo = f.read()

    tokens, errores = scan(codigo)

    # Tabla de tokens: Lexema, Token (código), Línea
    with open("Tokens.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<25}{'Token':<15}{'PTS':<10}{'Línea':<10}\n")
        for t in tokens:
            # Identificar si es un identificador (según el código de token)
            if t.codigo in [-55, -56, -57, -58]:
                pts = -2
            else:
                pts = -1
            f.write(f"{t.lexema:<25}{t.codigo:<15}{pts:<10}{t.linea:<10}\n")

    # Tabla de errores: Lexema, Descripción breve, Línea
    with open("Errores.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<25}{'Descripción':<80}{'Línea':<10}\n")
        for e in errores:
            f.write(f"{e.lexema:<25}{e.descripcion:<80}{e.linea:<10}\n")

    print("Análisis léxico completado.")


if __name__ == "__main__":
    main()
