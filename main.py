# main.py
from lexer import scan

def main():
    ruta_fuente = "ejemplos/entrada.txt"
    with open(ruta_fuente, "r", encoding="utf-8") as f:
        codigo = f.read()

    tokens, errores = scan(codigo)

    # Guardar tokens en archivo
    with open("Tokens.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<20}{'Token':<25}{'Línea':<10}{'Columna':<10}\n")
        for t in tokens:
            f.write(f"{t.lexema:<20}{t.tipo:<25}{t.linea:<10}{t.columna:<10}\n")

    # Guardar errores en archivo separado
    with open("Errores.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Lexema':<20}{'Descripción':<35}{'Línea':<10}{'Columna':<10}\n")
        for e in errores:
            f.write(f"{e.lexema:<20}{e.descripcion:<35}{e.linea:<10}{e.columna:<10}\n")

    print("Análisis léxico completado con éxito.")

if __name__ == "__main__":
    main()
