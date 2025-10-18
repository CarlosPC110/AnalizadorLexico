# lexer.py
import re
from token_type import TokenCodes

# Delimitadores “duros” que cortan palabras para errores de identificador
DELIMS = set([
    ' ', '\t', '\r', '\n',
    ';', '[', ']', ',', ':', '(', ')', '{', '}',
    '+', '-', '*', '/', '%', '=', '!', '&', '|', '<', '>', '"', '.'
])

def _next_word_end(linea: str, start: int) -> int:
    """
    Avanza hasta el final de la 'palabra' continua que comienza en start,
    deteniéndose en espacio, tab, salto de línea u operador/caracter especial.
    """
    j = start
    while j < len(linea) and linea[j] not in DELIMS:
        j += 1
    return j


class Token:
    def __init__(self, lexema: str, codigo: int, linea: int, columna: int):
        self.lexema = lexema
        self.codigo = codigo
        self.linea = linea
        self.columna = columna  # posición dentro de la línea

class ErrorLexico:
    def __init__(self, lexema: str, descripcion: str, linea: int, columna: int):
        self.lexema = lexema
        self.descripcion = descripcion
        self.linea = linea
        self.columna = columna

# Utilidades
LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"

def _emit_ident(linea, i, errores, num_linea):
    """
    Reconoce identificadores que empiezan con @ $ & % y luego SOLO letras.
    Longitud total (incluyendo el prefijo) entre 2 y 8.
    Si el carácter inmediatamente después del prefijo NO es letra,
    el error debe abarcar la 'palabra completa' hasta el siguiente delimitador.
    """
    inicio = i
    ctrl = linea[i]
    i += 1  # nos movemos al primer carácter después del prefijo

    # Caso 1: inmediatamente después del prefijo NO hay letra → error con palabra completa
    if i >= len(linea) or not linea[i].isalpha():
        fin = _next_word_end(linea, inicio)  # incluye cosas como @@error, @123, @#foo
        lex_err = linea[inicio:fin]
        errores.append(ErrorLexico(
            lex_err,
            "Identificador inválido: tras @/$/&/% deben venir solo letras",
            num_linea,
            inicio + 1
        ))
        return None, fin

    # Caso 2: sí hay letras → consumimos SOLO letras (regla del lenguaje)
    j = i
    while j < len(linea) and linea[j].isalpha():
        j += 1

    lex = linea[inicio:j]  # prefijo + letras

    # Validaciones de longitud 2..8 (incluye el prefijo)
    if len(lex) < 2 or len(lex) > 8:
        errores.append(ErrorLexico(
            lex,
            "Longitud de identificador inválida (2..8)",
            num_linea,
            inicio + 1
        ))
        return None, j

    # Clasificar por tipo de control
    tipo_key = {
        '@': "@identificador",
        '$': "$identificador",
        '&': "&identificador",
        '%': "%identificador",
    }.get(ctrl)

    codigo = TokenCodes.MAP[tipo_key]
    return Token(lex, codigo, num_linea, inicio + 1), j


def _emit_number(linea, i, errores, num_linea):
    """Reconoce enteros y reales con signo opcional. Si excede rango entero -> real."""
    inicio = i
    # signo opcional pegado
    if linea[i] in "+-":
        if i+1 >= len(linea) or not (linea[i+1].isdigit() or linea[i+1] == '.'):
            return None, i
        i += 1
    # parte entera
    j = i
    while j < len(linea) and linea[j].isdigit():
        j += 1
    es_real = False
    # punto decimal opcional
    if j < len(linea) and linea[j] == '.':
        es_real = True
        j += 1
        k = j
        while k < len(linea) and linea[k].isdigit():
            k += 1
        if k == j:
            errores.append(ErrorLexico(linea[inicio:k], "Real mal formado (no puede terminar en '.')", num_linea, inicio+1))
            return None, k
        j = k
    lex = linea[inicio:j]
    # Validar que no haya letras mezcladas (ej. 45.9a)
    if j < len(linea) and linea[j].isalpha():
        k = j
        while k < len(linea) and linea[k].isalpha():
            k += 1
        errores.append(ErrorLexico(linea[inicio:k], "Número con sufijo no permitido", num_linea, inicio+1))
        return None, k
    if es_real:
        return Token(lex, TokenCodes.MAP["constante_real"], num_linea, inicio+1), j
    # entero: verificar rango
    try:
        val = int(lex)
        if val < -32768 or val > 32767:
            return Token(lex, TokenCodes.MAP["constante_real"], num_linea, inicio+1), j
        return Token(lex, TokenCodes.MAP["constante_entera"], num_linea, inicio+1), j
    except ValueError:
        return None, j

def _emit_string(linea, i, errores, num_linea):
    inicio = i
    fin = linea.find('"', i+1)
    if fin == -1:
        errores.append(ErrorLexico(linea[i:], "String sin cerrar", num_linea, i+1))
        return None, len(linea)
    lex = linea[inicio:fin+1]
    return Token(lex, TokenCodes.MAP["constante_string"], num_linea, inicio+1), fin+1

# Orden por longitud para operadores multi-caracter
OPERADORES_ORD = sorted(
    list(TokenCodes.ARITMETICOS | TokenCodes.RELACIONALES | TokenCodes.LOGICOS),
    key=lambda s: len(s), reverse=True
)

def scan(codigo: str):
    tokens = []
    errores = []

    lineas = codigo.splitlines()
    for num_linea, linea in enumerate(lineas, start=1):
        i = 0
        while i < len(linea):
            ch = linea[i]

            # Espacios / tabs / BCO (lo interpretamos como espacios)
            if ch in [' ', '\t', '\r']:
                i += 1
                continue

            # Comentarios //
            if linea.startswith("//", i):
                break

            # String
            if ch == '"':
                tok, i = _emit_string(linea, i, errores, num_linea)
                if tok: tokens.append(tok)
                continue

            # Identificadores con control
            if ch in "@$&%":
                tok, i2 = _emit_ident(linea, i, errores, num_linea)
                if tok: tokens.append(tok)
                i = i2
                continue

            # Números (posible signo pegado o inicio con '.')
            if ch.isdigit() or (ch in "+-" and i+1 < len(linea) and (linea[i+1].isdigit() or linea[i+1]=='.')) or (ch=='.' and i+1 < len(linea) and linea[i+1].isdigit()):
                tok, i2 = _emit_number(linea, i, errores, num_linea)
                if tok:
                    tokens.append(tok)
                    i = i2
                    continue
                else:
                    i = max(i2, i+1)
                    continue

            # Palabras reservadas (solo letras)
            if ch.isalpha():
                j = i
                while j < len(linea) and linea[j].isalpha():
                    j += 1
                palabra = linea[i:j]
                if palabra in TokenCodes.RESERVADAS:
                    tokens.append(Token(palabra, TokenCodes.MAP[palabra], num_linea, i+1))
                else:
                    errores.append(ErrorLexico(palabra, "Palabra no reconocida", num_linea, i+1))
                i = j
                continue

            # Operadores (max munch)
            match = None
            for op in OPERADORES_ORD:
                if linea.startswith(op, i):
                    match = op
                    break
            if match:
                tokens.append(Token(match, TokenCodes.MAP[match], num_linea, i+1))
                i += len(match)
                continue

            # Caracteres especiales que generan token
            if ch in TokenCodes.ESPECIALES:
                tokens.append(Token(ch, TokenCodes.MAP[ch], num_linea, i+1))
                i += 1
                continue

            # Cualquier otro símbolo
            errores.append(ErrorLexico(ch, "Símbolo no reconocido", num_linea, i+1))
            i += 1

    return tokens, errores
