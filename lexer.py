# lexer.py
import re
from token_type import TokenType

class Token:
    def __init__(self, lexema, tipo, linea, columna):
        self.lexema = lexema
        self.tipo = tipo
        self.linea = linea
        self.columna = columna  # posición dentro de la línea

class ErrorLexico:
    def __init__(self, lexema, descripcion, linea, columna):
        self.lexema = lexema
        self.descripcion = descripcion
        self.linea = linea
        self.columna = columna

def scan(codigo):
    tokens = []
    errores = []
    lineas = codigo.split("\n")

    for num_linea, linea in enumerate(lineas, start=1):
        i = 0
        while i < len(linea):
            ch = linea[i]

            # Ignorar espacios o tabs
            if ch.isspace():
                i += 1
                continue

            # Comentarios //
            if linea[i:i+2] == "//":
                break  # ignorar resto de la línea

            # Constante string "..."
            if ch == '"':
                fin = linea.find('"', i+1)
                if fin == -1:
                    errores.append(ErrorLexico(linea[i:], "String sin cerrar", num_linea, i+1))
                    break
                tokens.append(Token(linea[i:fin+1], "ConstanteString", num_linea, i+1))
                i = fin + 1
                continue

            # Identificadores con prefijo @ $ & %
            if ch in "@$&%":
                patron = r"[@$&%][A-Za-z]{1,7}"
                match = re.match(patron, linea[i:])
                if match:
                    lex = match.group()
                    tokens.append(Token(lex, "Identificador", num_linea, i+1))
                    i += len(lex)
                    continue
                else:
                    errores.append(ErrorLexico(ch, "Identificador inválido", num_linea, i+1))
                    i += 1
                    continue

            # Constantes numéricas
            if re.match(r"[0-9]", ch):
                patron_num = r"-?\d+(\.\d+)?"
                match = re.match(patron_num, linea[i:])
                if match:
                    lex = match.group()
                    tipo = "ConstanteReal" if "." in lex else "ConstanteEntera"
                    tokens.append(Token(lex, tipo, num_linea, i+1))
                    i += len(lex)
                    continue

            # Palabras reservadas o desconocidas
            patron_pal = r"[A-Za-z_][A-Za-z0-9_]*"
            match = re.match(patron_pal, linea[i:])
            if match:
                lex = match.group()
                if lex in TokenType.RESERVADAS:
                    tokens.append(Token(lex, "PalabraReservada", num_linea, i+1))
                else:
                    errores.append(ErrorLexico(lex, "Palabra no reconocida", num_linea, i+1))
                i += len(lex)
                continue

            # Operadores
            posibles_ops = TokenType.ARITMETICOS | TokenType.RELACIONALES | TokenType.LOGICOS
            encontrado = None
            for op in sorted(posibles_ops, key=len, reverse=True):
                if linea.startswith(op, i):
                    encontrado = op
                    break
            if encontrado:
                tokens.append(Token(encontrado, "Operador", num_linea, i+1))
                i += len(encontrado)
                continue

            # Caracteres especiales
            if ch in TokenType.ESPECIALES:
                tokens.append(Token(ch, "CaracterEspecial", num_linea, i+1))
                i += 1
                continue

            # Si no coincide con nada
            errores.append(ErrorLexico(ch, "Símbolo no reconocido", num_linea, i+1))
            i += 1

    return tokens, errores
