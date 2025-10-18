# token_type.py

class TokenType:
    # Palabras reservadas
    RESERVADAS = {
        "clase", "var", "vacio", "metodo", "leer", "escribir", "switch", "encaso",
        "si", "sino", "mientras", "repite", "posxy", "limpiar", "ejecutar",
        "regresar", "entero", "real", "cadena", "salir"
    }

    # Operadores
    ARITMETICOS = {"+", "-", "*", "/", "%", "=", "++", "--", "+=", "-=", "*=", "/="}
    RELACIONALES = {"<", "<=", "!=", ">", ">=", "=="}
    LOGICOS = {"!", "&&", "||"}

    # Caracteres especiales (generan token)
    ESPECIALES = {";", "[", "]", ",", ":", "(", ")", "{", "}"}

    # No generan token
    NO_GENERAN = {'"', '.', 'BCO', 'TAB'}

