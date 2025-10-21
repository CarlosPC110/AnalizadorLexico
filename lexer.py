# lexer.py
import re
from token_type import TokenCodes

# Delimitadores que cortan palabras para errores de identificador
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
    Identificadores:
      - Deben iniciar con @, $, & o %.
      - Después del prefijo, SOLO letras [A-Za-z].
      - Longitud total (incluido el prefijo) entre 2 y 8.
      - Si tras las letras hay cualquier carácter no delimitador (p. ej. dígitos, '_'),
        se reporta UN error con la palabra completa, p.ej. $abc9, %__ , @abc9.
    Siempre avanza el índice.
    """
    inicio = i
    ctrl = linea[i]
    i += 1  # carácter después del prefijo

    # Delimitadores “duros”
    DELIMS = set([
        ' ', '\t', '\r', '\n',
        ';', '[', ']', ',', ':', '(', ')', '{', '}',
        '+', '-', '*', '/', '%', '=', '!', '&', '|', '<', '>', '"', '.'
    ])

    # 1) Si NO hay letra tras el prefijo → error en UNA sola pieza
    if i >= len(linea) or not linea[i].isalpha():
        fin = i
        # consumir repeticiones del mismo prefijo (p. ej. @@, $$, &&, %%)
        while fin < len(linea) and linea[fin] == ctrl:
            fin += 1
        # consumir hasta delimitador duro
        while fin < len(linea) and linea[fin] not in DELIMS:
            fin += 1
        if fin <= inicio:
            fin = inicio + 1
        errores.append(ErrorLexico(
            linea[inicio:fin],
            "Identificador inválido: tras @/$/&/% deben venir solo letras",
            num_linea,
            inicio + 1
        ))
        return None, fin

    # 2) Consumir SOLO letras
    j = i
    while j < len(linea) and linea[j].isalpha():
        j += 1

    # 3) Si hay algo pegado NO-delimitador tras las letras → error UNA sola pieza
    k = j
    if k < len(linea) and linea[k] not in DELIMS:
        while k < len(linea) and linea[k] not in DELIMS:
            k += 1
        errores.append(ErrorLexico(
            linea[inicio:k],
            "Identificador inválido: contiene caracteres no permitidos tras las letras",
            num_linea,
            inicio + 1
        ))
        return None, k

    # 4) Validar longitud total
    lex = linea[inicio:j]
    if len(lex) < 2 or len(lex) > 8:
        errores.append(ErrorLexico(
            lex,
            "Longitud de identificador inválida (2..8)",
            num_linea,
            inicio + 1
        ))
        return None, j

    # 5) Clasificar
    tipo_key = {
        '@': "@identificador",
        '$': "$identificador",
        '&': "&identificador",
        '%': "%identificador",
    }[ctrl]

    codigo = TokenCodes.MAP[tipo_key]
    return Token(lex, codigo, num_linea, inicio + 1), j




def _emit_number(linea, i, errores, num_linea):
    """
    Números:
      - Signo opcional (+/-) PEGADO.
      - Enteros o reales (un solo punto). Pueden iniciar con punto si luego hay dígito.
      - NO pueden terminar en punto.
      - Si hay múltiples puntos en la MISMA 'palabra', se reporta un único error con el lexema completo.
      - Si hay letras pegadas (p.ej. 45.9kg), error 'Número con sufijo no permitido'.
      - Entero fuera de [-32768, 32767] se clasifica como real.
    Siempre avanza el índice para evitar ciclos.
    """
    inicio = i

    # Si empieza con signo, validar que siga dígito o '.'
    if linea[i] in "+-":
        if i + 1 >= len(linea) or not (linea[i + 1].isdigit() or linea[i + 1] == '.'):
            # No es número, consume SOLO el signo para evitar ciclo
            return None, i + 1
        i += 1

    j = i
    dot_count = 0

    # Caso de inicio con '.': debe venir un dígito
    if j < len(linea) and linea[j] == '.':
        dot_count += 1
        j += 1
        if j >= len(linea) or not linea[j].isdigit():
            # ".<no-dígito>" -> real mal formado (termina en '.')
            errores.append(ErrorLexico(linea[inicio:j], "Real mal formado (no puede terminar en '.')", num_linea, inicio + 1))
            return None, j

    # Consumir dígitos/puntos (controlando múltiples puntos)
    while j < len(linea) and (linea[j].isdigit() or linea[j] == '.'):
        if linea[j] == '.':
            dot_count += 1
            if dot_count > 1:
                # Consumir el resto continuo de dígitos/puntos para reportar un solo error
                k = j + 1
                while k < len(linea) and (linea[k].isdigit() or linea[k] == '.'):
                    k += 1
                lex_err = linea[inicio:k]
                errores.append(ErrorLexico(lex_err, "Número real mal formado", num_linea, inicio + 1))
                return None, k
        j += 1

    lex = linea[inicio:j]

    # Si justo después hay letras (sufijo), capturarlas para un error único
    if j < len(linea) and linea[j].isalpha():
        k = j
        while k < len(linea) and linea[k].isalpha():
            k += 1
        errores.append(ErrorLexico(linea[inicio:k], "Número con sufijo no permitido", num_linea, inicio + 1))
        return None, k

    # Si tiene un solo punto, no puede terminar en '.'
    if dot_count == 1 and lex.endswith('.'):
        errores.append(ErrorLexico(lex, "Real mal formado (no puede terminar en '.')", num_linea, inicio + 1))
        return None, j

    # Decidir entero vs real
    if dot_count == 0:
        # Entero: verificar rango
        try:
            val = int(lex)
            if val < -32768 or val > 32767:
                return Token(lex, TokenCodes.MAP["constante_real"], num_linea, inicio + 1), j
            return Token(lex, TokenCodes.MAP["constante_entera"], num_linea, inicio + 1), j
        except ValueError:
            # por robustez (no debería ocurrir si solo hay dígitos)
            errores.append(ErrorLexico(lex, "Entero mal formado", num_linea, inicio + 1))
            return None, j
    else:
        # Real válido (un solo punto y no termina en '.')
        return Token(lex, TokenCodes.MAP["constante_real"], num_linea, inicio + 1), j



def _emit_string(linea, i, errores, num_linea):
    inicio = i
    fin = linea.find('"', i+1)
    if fin == -1:
        errores.append(ErrorLexico(linea[i:], " String sin cerrar", num_linea, i+1))
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
            prev_i = i  # <- AGREGAR (para la garantía de avance)
            # 1 Espacios / tabs / BCO (lo interpretamos como espacios)
            if ch in [' ', '\t', '\r']:
                i += 1
                continue

            # 2 Comentarios //
            if linea.startswith("//", i):
                break

            # 3 String
            if ch == '"':
                tok, i = _emit_string(linea, i, errores, num_linea)
                if tok: tokens.append(tok)
                continue
            
            # --- Punto suelto: NO genera token ni error, se ignora ---
            if ch == '.' and not (i + 1 < len(linea) and linea[i + 1].isdigit()):
                i += 1
                continue

            
            # === Prefijos de identificador con reglas específicas ===
            # Objetivo:
            # - % + letra  -> identificador (%identificador)
            # - % solo     -> operador '%'
            # - & + &      -> operador '&&' (lo dejamos al bloque de operadores)
            # - & + letra  -> identificador (&identificador)
            # - & + otro   -> error de identificador (una sola pieza)
            # - @ / $      -> siempre van a _emit_ident (válido o error, pero en UNA sola pieza)
                # === Prefijos de identificador con reglas específicas ===
            if ch in "@$&%":
                nxt = linea[i + 1] if (i + 1) < len(linea) else ""

                # Delimitadores "duros" para decidir si hay "algo pegado" al prefijo
                DELIMS_LOCAL = set([
                    ' ', '\t', '\r', '\n',
                    ';', '[', ']', ',', ':', '(', ')', '{', '}',
                    '+', '-', '*', '/', '%', '=', '!', '&', '|', '<', '>', '"', '.'
                ])

                # ----- CASO '%' -----
                if ch == '%':
                    if nxt.isalpha():
                        # % + letra => identificador válido de reales
                        tok, i2 = _emit_ident(linea, i, errores, num_linea)
                        if tok: tokens.append(tok)
                        i = i2
                        continue
                    elif nxt and nxt not in DELIMS_LOCAL:
                        # % seguido de NO-letra y NO-delimitador (p.ej. "_", "1", etc.) => error de identificador (UNA pieza)
                        tok, i2 = _emit_ident(linea, i, errores, num_linea)
                        # _emit_ident ya agrega el error y avanza hasta el siguiente delimitador
                        i = i2
                        continue
                    else:
                        # % solo (o seguido de delimitador) => operador aritmético
                        tokens.append(Token('%', TokenCodes.MAP['%'], num_linea, i + 1))
                        i += 1
                        continue

                # ----- CASO '&' -----
                if ch == '&':
                    if nxt == '&':
                        # Dejar que el bloque de OPERADORES consuma "&&"
                        pass
                    elif nxt.isalpha():
                        tok, i2 = _emit_ident(linea, i, errores, num_linea)
                        if tok: tokens.append(tok)
                        i = i2
                        continue
                    elif nxt and nxt not in DELIMS_LOCAL:
                        # & seguido de no-letra/no-delimitador (p.ej. "_", "1") => error UNA pieza
                        tok, i2 = _emit_ident(linea, i, errores, num_linea)
                        i = i2
                        continue
                    else:
                        # '&' solo no es operador en el lenguaje → error identificador inválido (avanza 1)
                        errores.append(ErrorLexico('&', "Identificador inválido: tras @/$/&/% deben venir solo letras", num_linea, i + 1))
                        i += 1
                        continue

                # ----- CASOS '@' y '$' -----
                if ch in "@$":
                    tok, i2 = _emit_ident(linea, i, errores, num_linea)
                    if tok: tokens.append(tok)
                    i = i2
                    continue

            
            # 4) NÚMEROS (dígito | signo pegado + dígito/punto | '.' + dígito)
            if ch.isdigit() or (ch in "+-" and i+1 < len(linea) and (linea[i+1].isdigit() or linea[i+1]=='.')) or (ch=='.' and i+1 < len(linea) and linea[i+1].isdigit()):
                tok, i2 = _emit_number(linea, i, errores, num_linea)
                if tok: tokens.append(tok)
                i = i2
                continue

            # 5) OPERADORES (max-munch)  ← SIEMPRE ANTES QUE IDENTIFICADORES CON PREFIJO
            match = None
            for op in OPERADORES_ORD:
                if linea.startswith(op, i):
                    match = op
                    break
            if match:
                tokens.append(Token(match, TokenCodes.MAP[match], num_linea, i+1))
                i += len(match)
                continue

            # 6) PALABRAS RESERVADAS (solo letras)
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

            # 9) CARACTERES ESPECIALES QUE GENERAN TOKEN
            if ch in TokenCodes.ESPECIALES:
                tokens.append(Token(ch, TokenCodes.MAP[ch], num_linea, i+1))
                i += 1
                continue

            # 10) SÍMBOLO NO RECONOCIDO
            errores.append(ErrorLexico(ch, "Símbolo no reconocido", num_linea, i+1))
            i += 1

            # 11) ANTI-CICLO (por seguridad extra)
            if i == prev_i:
                i += 1                
                
    return tokens, errores
