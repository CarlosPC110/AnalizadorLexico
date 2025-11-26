# ================================================================
# ANALIZADOR SINTÁCTICO CORREGIDO - Basado Estrictamente en el PDF
# ================================================================

import re
from dataclasses import dataclass

# ================================================================
# MAP A DE TOKENS
# ================================================================
TOKEN_MAP = {
    # Palabras reservadas
    -1: "CLASE", -2: "LEER", -3: "SWITCH", -4: "POSXY", -5: "ENTERO", -6: "VAR",
    -7: "ESCRIBIR", -8: "ENCASO", -9: "LIMPIAR", -10: "REAL", -11: "VACIO",
    -12: "SI", -13: "REPITE", -14: "EJECUTAR", -15: "REGRESAR",
    -16: "METODO", -17: "SINO", -18: "MIENTRAS", -19: "CADENA", -20: "SALIR",

    # Operadores aritméticos y asignación
    -21: "MAS", -22: "MENOS", -23: "MULT", -24: "DIV", -25: "MOD",
    -26: "IGUAL", -27: "INCR", -28: "DECR", -29: "MAS_IGUAL", -30: "MENOS_IGUAL",
    -31: "DIV_IGUAL", -32: "MULT_IGUAL",

    # Operadores relacionales
    -33: "MENOR", -34: "MENOR_IGUAL", -35: "DISTINTO", -36: "MAYOR", 
    -37: "MAYOR_IGUAL", -38: "IGUALDAD",

    # Operadores lógicos
    -39: "NOT", -40: "AND", -41: "OR",

    # Delimitadores
    -42: "PUNTOYCOMA", -43: "COR_AP", -44: "COR_CI", -45: "COMA", -46: "DOS_PUNTOS",
    -47: "PAR_AP", -48: "PAR_CI", -49: "LLAVE_AP", -50: "LLAVE_CI",

    # Identificadores
    -55: "ID_ARROBA", -56: "ID_DOLAR", -57: "ID_AMP", -58: "ID_PORC",

    # Constantes
    -59: "CTE_ENT", -60: "CTE_REAL", -61: "CTE_CADENA",
}

@dataclass
class Token:
    type: str
    lexeme: str
    line: int

def cargar_tokens_desde_tabla(ruta):
    tokens = []
    with open(ruta, encoding="utf-8") as f:
        for line in f:
            # BUGFIX: Cambiar line.startswith('-') a line.startswith('---')
            # para NO saltar el token MENOS '-'
            if not line.strip() or line.startswith('---') or line.startswith('LEXEMA') or line.startswith('Lexema'):
                continue

            if len(line) < 50:
                continue

            lexema = line[0:25].strip()
            token_str = line[25:40].strip()
            linea_str = line[50:60].strip()

            if not token_str or not linea_str:
                continue

            try:
                codigo = int(token_str)
                linea = int(linea_str)
            except ValueError:
                continue

            tipo = TOKEN_MAP.get(codigo)

            if tipo is None:
                if re.fullmatch(r"\d+\.\d+", lexema):
                    tipo = "CTE_REAL"
                elif re.fullmatch(r"\d+", lexema):
                    tipo = "CTE_ENT"
                elif len(lexema) >= 2 and lexema[0] == '"' and lexema[-1] == '"':
                    tipo = "CTE_CADENA"
                elif lexema.startswith("@"):
                    tipo = "ID_ARROBA"
                elif lexema.startswith("$"):
                    tipo = "ID_DOLAR"
                elif lexema.startswith("&"):
                    tipo = "ID_AMP"
                elif lexema.startswith("%"):
                    tipo = "ID_PORC"
                elif lexema == "+":
                    tipo = "MAS"
                elif lexema == "-":
                    tipo = "MENOS"
                elif lexema == "*":
                    tipo = "MULT"
                elif lexema == "/":
                    tipo = "DIV"
                elif lexema == "%":
                    tipo = "MOD"
                elif lexema == "=":
                    tipo = "IGUAL"
                elif lexema == "++":
                    tipo = "INCR"
                elif lexema == "--":
                    tipo = "DECR"
                elif lexema == "+=":
                    tipo = "MAS_IGUAL"
                elif lexema == "-=":
                    tipo = "MENOS_IGUAL"
                elif lexema == "*=":
                    tipo = "MULT_IGUAL"
                elif lexema == "/=":
                    tipo = "DIV_IGUAL"
                elif lexema == "<":
                    tipo = "MENOR"
                elif lexema == "<=":
                    tipo = "MENOR_IGUAL"
                elif lexema == ">":
                    tipo = "MAYOR"
                elif lexema == ">=":
                    tipo = "MAYOR_IGUAL"
                elif lexema == "==":
                    tipo = "IGUALDAD"
                elif lexema == "!=":
                    tipo = "DISTINTO"
                elif lexema == "&&":
                    tipo = "AND"
                elif lexema == "||":
                    tipo = "OR"
                elif lexema == "!":
                    tipo = "NOT"
                elif lexema == ";":
                    tipo = "PUNTOYCOMA"
                elif lexema == "[":
                    tipo = "COR_AP"
                elif lexema == "]":
                    tipo = "COR_CI"
                elif lexema == ",":
                    tipo = "COMA"
                elif lexema == ":":
                    tipo = "DOS_PUNTOS"
                elif lexema == "(":
                    tipo = "PAR_AP"
                elif lexema == ")":
                    tipo = "PAR_CI"
                elif lexema == "{":
                    tipo = "LLAVE_AP"
                elif lexema == "}":
                    tipo = "LLAVE_CI"
                else:
                    tipo = f"DESCONOCIDO_{codigo}"

            tokens.append(Token(type=tipo, lexeme=lexema, line=linea))

    print(f"{len(tokens)} tokens cargados correctamente desde {ruta}\n")
    return tokens

class Parser:
    ID_TYPES = ("ID_ARROBA", "ID_DOLAR", "ID_AMP", "ID_PORC")
    CTE_TYPES = ("CTE_ENT", "CTE_REAL", "CTE_CADENA")
    OP_ARIT_TYPES = ("MAS", "MENOS", "MULT", "DIV", "MOD", "INCR", "DECR", 
                    "MAS_IGUAL", "MENOS_IGUAL", "DIV_IGUAL", "MULT_IGUAL")
    OP_REL_TYPES = ("MENOR", "MENOR_IGUAL", "MAYOR", "MAYOR_IGUAL", "IGUALDAD", "DISTINTO")
    OP_LOG_TYPES = ("AND", "OR")

    def __init__(self, tokens):
        self.tokens = tokens + [Token("EOF", "EOF", -1)]
        self.pos = 0
        self.current = self.tokens[0]
        self.errores = []
        self.en_panico = False

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]

    def consume(self, lex=None, type_=None, msg="Error de sintaxis"):
        ok = False
        if lex is not None and self.current.lexeme == lex:
            ok = True
        if type_ is not None and self.current.type == type_:
            ok = True

        if ok:
            self.advance()
            return True
        else:
            self.reportar_error(msg)
            return False

    def check_lex(self, *lexemes):
        return self.current.lexeme in lexemes

    def check_type(self, *types_):
        return self.current.type in types_

    def reportar_error(self, msg):
        if not self.en_panico:
            texto = f"[L{self.current.line}] {msg} — encontrado '{self.current.lexeme}'"
            self.errores.append(texto)

    def sincronizar(self, *sync_tokens):
        self.en_panico = True
        while self.current.lexeme not in sync_tokens and self.current.type != "EOF":
            self.advance()
        self.en_panico = False

    # ============================================================
    # PROGRAMA PRINCIPAL - Página 1
    # ============================================================
    def parse(self):
        self.PROG()
        self.mostrar_reporte()

    def PROG(self):
        self.consume(lex="clase", msg="Se esperaba 'clase'")
        self.consume(type_="ID_ARROBA", msg="Se esperaba identificador de clase (@id)")
        self.consume(lex="{", msg="Falta '{' después de clase")

        while self.check_lex("var"):
            self.VAR()

        while self.check_lex("metodo"):
            self.METODO()

        self.consume(lex="}", msg="Falta '}' al final de la clase")

    # ============================================================
    # VARIABLES - Página 1
    # ============================================================
    def VAR(self):
        self.consume(lex="var", msg="Se esperaba 'var'")
        self.ID_ARREGLO(msg="Se esperaba identificador de variable")
        while self.check_lex(","):
            self.advance()
            self.ID_ARREGLO(msg="Falta identificador después de ','")
        self.consume(lex=";", msg="Falta ';' al final de la declaración de variable")

    def ID_ARREGLO(self, msg="Se esperaba identificador"):
        if not self.check_type(*self.ID_TYPES):
            self.reportar_error(msg)
            return
        self.advance()

        if self.check_lex("["):
            self.advance()
            self.EXP_ARIT()
            while self.check_lex(","):
                self.advance()
                self.EXP_ARIT()
            self.consume(lex="]", msg="Falta ']' en índice de arreglo")

    # ============================================================
    # METODOS - Página 1
    # ============================================================
    def METODO(self):
        self.consume(lex="metodo", msg="Se esperaba 'metodo'")

        if self.check_lex("entero", "real", "cadena", "vacio"):
            self.advance()
        else:
            self.reportar_error("Tipo de retorno inválido, se esperaba 'entero', 'real', 'cadena' o 'vacio'")

        self.consume(type_="ID_ARROBA", msg="Falta nombre del método (@id)")
        self.consume(lex="(", msg="Falta '(' en definición de método")

        if not self.check_lex(")"):
            self.PARAM()

        self.consume(lex=")", msg="Falta ')' en definición de método")
        self.consume(lex="{", msg="Falta '{' en cuerpo del método")

        while self.check_lex("var"):
            self.VAR()

        while self.es_inicio_estatuto():
            self.ESTATUTO()

        self.consume(lex="}", msg="Falta '}' al final del método")

    def PARAM(self):
        self.ID_ARREGLO(msg="Se esperaba identificador de parámetro")
        while self.check_lex(","):
            self.advance()
            self.ID_ARREGLO(msg="Se esperaba identificador de parámetro")

    # ============================================================
    # ESTATUTOS - Página 2
    # ============================================================
    def es_inicio_estatuto(self):
        return (self.check_type(*self.ID_TYPES) or
                self.check_lex("leer", "escribir", "si", "mientras", "repite",
                             "switch", "ejecutar", "salir", "regresar"))

    def ESTATUTO(self):
        if self.check_type(*self.ID_TYPES):
            self.ASIGNA()
        elif self.check_lex("leer"):
            self.LEER()
        elif self.check_lex("escribir"):
            self.ESCRIBIR()
        elif self.check_lex("si"):
            self.SI()
        elif self.check_lex("mientras"):
            self.MIENTRAS()
        elif self.check_lex("repite"):
            self.REPITE()
        elif self.check_lex("switch"):
            self.SWITCH()
        elif self.check_lex("ejecutar"):
            self.EJECUTAR()
        elif self.check_lex("salir"):
            self.SALIR()
        elif self.check_lex("regresar"):
            self.REGRESAR()
        else:
            self.reportar_error("Estatuto no reconocido")
            self.sincronizar(";", "}")

    def ASIGNA(self):
        self.ID_ARREGLO(msg="Se esperaba identificador en asignación")
        
        # Check for assignment operator or increment/decrement
        if self.check_lex("=", "+=", "-=", "*=", "/="):
            self.advance()  # consume assignment operator
            self.EXP_ARIT()
            self.consume(lex=";", msg="Falta ';' al final de la asignación")
        elif self.check_lex("++", "--"):
            self.advance()  # consume ++ or --
            self.consume(lex=";", msg="Falta ';' al final de la expresión")
        else:
            self.reportar_error("Falta operador de asignación (=, +=, -=, *=, /=, ++ o --)")

    # ============================================================
    # EXPRESIONES ARITMÉTICAS - Página 2
    # ============================================================
    def EXP_ARIT(self):
        self.OPERANDO()
        while self.current.type in self.OP_ARIT_TYPES:
            self.advance()
            self.OPERANDO()

    def OPERANDO(self):
        if self.check_lex("("):
            self.advance()
            self.EXP_ARIT()
            self.consume(lex=")", msg="Falta ')' en expresión")
        elif self.check_type(*self.ID_TYPES):
            # Check if it's a method call (ID_ARROBA followed by '(')
            if self.current.type == "ID_ARROBA" and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].lexeme == "(":
                # Method call
                self.advance()  # consume method name
                self.consume(lex="(", msg="Falta '(' en llamada a método")
                if not self.check_lex(")"):
                    self.EXP_ARIT()
                    while self.check_lex(","):
                        self.advance()
                        self.EXP_ARIT()
                self.consume(lex=")", msg="Falta ')' en llamada a método")
            else:
                # Regular identifier or array access
                self.ID_ARREGLO()
        elif self.check_type(*self.CTE_TYPES):
            self.advance()
        else:
            self.reportar_error("Se esperaba identificador, constante o '(' en expresión aritmética")

    # ============================================================
    # LEER - Página 3
    # ============================================================
    def LEER(self):
        self.consume(lex="leer")
        self.consume(lex="(", msg="Falta '(' en 'leer'")
        self.ID_ARREGLO(msg="Falta identificador válido en 'leer'")
        self.consume(lex=")", msg="Falta ')' en 'leer'")
        self.consume(lex=";", msg="Falta ';' al final de 'leer'")

    # ============================================================
    # ESCRIBIR - Página 4
    # ============================================================
    def ESCRIBIR(self):
        self.consume(lex="escribir")
        self.consume(lex="(", msg="Falta '(' en 'escribir'")
        # Permitir escribir() vacio
        if not self.check_lex(")"):
            self.EXP_ARIT()
            while self.check_lex(","):
                self.advance()
                self.EXP_ARIT()
        self.consume(lex=")", msg="Falta ')' en 'escribir'")
        self.consume(lex=";", msg="Falta ';' al final de 'escribir'")

    # ============================================================
    # ESTRUCTURAS DE CONTROL - Página 4
    # ============================================================
    def SI(self):
        self.consume(lex="si")
        self.consume(lex="(", msg="Falta '(' en 'si'")
        self.CONDICION()
        self.consume(lex=")", msg="Falta ')' en 'si'")
        self.consume(lex="{", msg="Falta '{' en bloque 'si'")
        while self.es_inicio_estatuto():
            self.ESTATUTO()
        self.consume(lex="}", msg="Falta '}' al final del bloque 'si'")

        if self.check_lex("sino"):
            self.advance()
            self.consume(lex="{", msg="Falta '{' en bloque 'sino'")
            while self.es_inicio_estatuto():
                self.ESTATUTO()
            self.consume(lex="}", msg="Falta '}' al final de bloque 'sino'")

    def REPITE(self):
        self.consume(lex="repite")
        self.consume(lex="{", msg="Falta '{' en 'repite'")
        while self.es_inicio_estatuto():
            self.ESTATUTO()
        self.consume(lex="}", msg="Falta '}' en 'repite'")
        self.consume(lex="mientras", msg="Falta 'mientras' después de 'repite'")
        self.consume(lex="(", msg="Falta '(' en condición de 'repite'")
        self.CONDICION()
        self.consume(lex=")", msg="Falta ')' en condición de 'repite'")
        self.consume(lex=";", msg="Falta ';' al final de 'repite'")

    def MIENTRAS(self):
        self.consume(lex="mientras")
        self.consume(lex="(", msg="Falta '(' en 'mientras'")
        self.CONDICION()
        self.consume(lex=")", msg="Falta ')' en 'mientras'")
        self.consume(lex="{", msg="Falta '{' en 'mientras'")
        while self.es_inicio_estatuto():
            self.ESTATUTO()
        self.consume(lex="}", msg="Falta '}' al final de 'mientras'")

    # ============================================================
    # EJECUTAR Y SWITCH - Página 5
    # ============================================================
    def EJECUTAR(self):
        self.consume(lex="ejecutar")
        self.ID_ARREGLO(msg="Se esperaba identificador de variable destino en 'ejecutar'")
        self.consume(lex="=", msg="Falta '=' en 'ejecutar'")
        self.consume(type_="ID_ARROBA", msg="Falta nombre del método (@id) en 'ejecutar'")
        self.consume(lex="(", msg="Falta '(' en llamada a método")

        if not self.check_lex(")"):
            self.EXP_ARIT()
            while self.check_lex(","):
                self.advance()
                self.EXP_ARIT()

        self.consume(lex=")", msg="Falta ')' en llamada a método")
        self.consume(lex=";", msg="Falta ';' al final de 'ejecutar'")

    def SWITCH(self):
        self.consume(lex="switch")
        self.consume(lex="(", msg="Falta '(' en 'switch'")
        # Según diagrama PDF: solo acepta id& (ID_AMP)
        if not self.check_type("ID_AMP"):
            self.reportar_error("Se esperaba identificador con '&' en switch")
        else:
            self.advance()
        self.consume(lex=")", msg="Falta ')' en 'switch'")
        self.consume(lex="{", msg="Falta '{' en 'switch'")

        while self.check_lex("encaso"):
            self.advance()
            if not self.check_type("CTE_ENT"):
                self.reportar_error("Se esperaba constante entera después de 'encaso'")
            else:
                self.advance()
            self.consume(lex=":", msg="Falta ':' después de 'encaso'")
            while self.es_inicio_estatuto():
                self.ESTATUTO()

        if self.check_lex("default"):
            self.advance()
            self.consume(lex=":", msg="Falta ':' después de 'default'")
            while self.es_inicio_estatuto():
                self.ESTATUTO()

        self.consume(lex="}", msg="Falta '}' al final de 'switch'")

    # ============================================================
    # CONDICIONES - Página 5
    # ============================================================
    def CONDICION(self):
        if self.check_lex("!"):
            self.advance()

        self.EXP_ARIT()

        if self.current.type in self.OP_REL_TYPES:
            self.advance()
        else:
            self.reportar_error("Se esperaba operador relacional")

        self.EXP_ARIT()

        while self.current.type in self.OP_LOG_TYPES:
            self.advance()
            if self.check_lex("!"):
                self.advance()
            self.EXP_ARIT()
            if self.current.type in self.OP_REL_TYPES:
                self.advance()
            else:
                self.reportar_error("Se esperaba operador relacional")
            self.EXP_ARIT()

    # ============================================================
    # REGRESAR Y SALIR - Página 6
    # ============================================================
    def REGRESAR(self):
        self.consume(lex="regresar")
        self.consume(lex="(", msg="Falta '(' en 'regresar'")
        if not self.check_lex(")"):
            self.EXP_ARIT()
        self.consume(lex=")", msg="Falta ')' en 'regresar'")
        self.consume(lex=";", msg="Falta ';' al final de 'regresar'")

    def SALIR(self):
        self.consume(lex="salir")
        self.consume(lex=";", msg="Falta ';' al final de 'salir'")

    def mostrar_reporte(self):
        if not self.errores:
            print("Analisis sintactico completado SIN ERRORES\n")
        else:
            print(f"\n{'='*60}")
            print(f"ANúLISIS SINTÁCTICO - {len(self.errores)} error(es) encontrado(s)")
            print(f"{'='*60}\n")
            for err in self.errores:
                print(err)
            print()

        with open("Errores_Sintácticos.txt", "w", encoding="utf-8") as f:
            if not self.errores:
                f.write("Análisis sintáctico completado SIN ERRORES\n")
            else:
                f.write(f"ANÁLISIS SINTÁCTICO - {len(self.errores)} error(es) encontrado(s)\n")
                f.write("=" * 60 + "\n\n")
                for err in self.errores:
                    f.write(err + "\n")

def main():
    import sys

    if len(sys.argv) < 2:
        print("Uso: python analizador_sintactico.py <tokens.txt>")
        sys.exit(1)

    ruta = sys.argv[1]

    try:
        tokens = cargar_tokens_desde_tabla(ruta)
        parser = Parser(tokens)
        parser.parse()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
