# main.py
from lexer import scan

def escribir_tokens(ruta, tokens):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("Lexema\tToken\tLinea\tColumna\n")
        for t in tokens:
            f.write(f"{t.lexema}\t{t.tipo}\t{t.linea}\t{t.columna}\n")

def escribir_errores(ruta, errores):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("Lexema\tDescripcion\tLinea\tColumna\n")
        for e in errores:
            f.write(f"{e.lexema}\t{e.descripcion}\t{e.linea}\t{e.columna}\n")

def main():
    with open("ejemplos/entrada.txt", "r", encoding="utf-8") as f:
        codigo = f.read()

    tokens, errores = scan(codigo)

    escribir_tokens("Tokens.txt", tokens)
    escribir_errores("Errores.txt", errores)

    print("✅ Análisis léxico completado.")
    print(f"→ {len(tokens)} tokens generados")
    print(f"→ {len(errores)} errores encontrados")

if __name__ == "__main__":
    main()
