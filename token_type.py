# token_type.py

class TokenCodes:
    # Mapa de lexema -> código de token (según Tokens.docx)
    MAP = {
        "clase": -1, "leer": -2, "switch": -3, "posxy": -4, "entero": -5, "var": -6,
        "escribir": -7, "encaso": -8, "limpiar": -9, "real": -10, "vacio": -11, "si": -12,
        "repite": -13, "ejecutar": -14, "regresar": -15, "metodo": -16, "sino": -17,
        "mientras": -18, "cadena": -19, "salir": -20,
        "+": -21, "-": -22, "*": -23, "/": -24, "%": -25, "=": -26, "++": -27, "--": -28,
        "+=": -29, "-=": -30, "/=": -31, "*=": -32,
        "<": -33, "<=": -34, "!=": -35, ">": -36, ">=": -37, "==": -38,
        "!": -39, "&&": -40, "||": -41,
        ";": -42, "[": -43, "]": -44, ",": -45, ":": -46, "(": -47, ")": -48, "{": -49, "}": -50,
        "@identificador": -55, "$identificador": -56, "&identificador": -57, "%identificador": -58,
        "constante_entera": -59, "constante_real": -60, "constante_string": -61
    }

    # Conjuntos útiles
    RESERVADAS = {k for k,v in MAP.items() if v <= -1 and v >= -20}
    ARITMETICOS = {"+","-","*","/","%","=","++","--","+=","-=","/=","*="}
    RELACIONALES = {"<","<=","!=" ,">",">=","=="}
    LOGICOS = {"!","&&","||"}
    ESPECIALES = {";","[","]",",",":","(",")","{","}"}
    NO_GENERAN = {'"', '.', 'BCO', 'TAB'}