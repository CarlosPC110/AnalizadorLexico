# gui_analizador_bonito.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from tkinter import ttk

from lexer import scan
from sintactic import cargar_tokens_desde_tabla, Parser


class AnalizadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico y Sintáctico")
        self.root.geometry("900x550")
        self.root.minsize(800, 480)

        # Rutas de trabajo
        self.ruta_fuente = None
        self.ruta_tokens = "Tokens.txt"
        self.ruta_errores_lex = "Errores.txt"
        self.ruta_errores_sint = "Errores_Sintácticos.txt"

        self._configurar_estilos()
        self._crear_layout()

    # ---------------- Estilos ----------------
    def _configurar_estilos(self):
        self.root.configure(bg="#1f2933")  # fondo ventana

        style = ttk.Style()
        # En algunos sistemas hace falta elegir un tema primero
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Colores base
        self.color_primario = "#2563eb"   # azul
        self.color_primario_hover = "#1d4ed8"
        self.color_panel = "#111827"      # fondo panel lateral
        self.color_contenido = "#0b1220"  # fondo área central
        self.color_texto = "#e5e7eb"      # texto claro
        self.color_borde = "#374151"

        # Frame de menú lateral
        style.configure(
            "Side.TFrame",
            background=self.color_panel
        )

        style.configure(
            "Main.TFrame",
            background=self.color_contenido
        )

        # Etiquetas
        style.configure(
            "Title.TLabel",
            background=self.color_panel,
            foreground="#f9fafb",
            font=("Segoe UI", 14, "bold")
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.color_panel,
            foreground="#9ca3af",
            font=("Consolas", 10)
        )
        style.configure(
            "Status.TLabel",
            background=self.color_contenido,
            foreground="#9ca3af",
            font=("Segoe UI", 9)
        )

        # Botones de menú
        style.configure(
            "Menu.TButton",
            background=self.color_panel,
            foreground=self.color_texto,
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0,
            anchor="w"
        )
        style.map(
            "Menu.TButton",
            background=[("active", "#111827"), ("pressed", "#020617")]
        )

        # Botón destacado (Analizar archivo)
        style.configure(
            "Primary.TButton",
            background=self.color_primario,
            foreground="#f9fafb",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[
                ("active", self.color_primario_hover),
                ("pressed", "#1e40af")
            ]
        )

    # ---------------- Layout ----------------
    def _crear_layout(self):
        # Contenedor principal (2 columnas: menú lateral + contenido)
        main = ttk.Frame(self.root, style="Main.TFrame")
        main.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(0, weight=0)  # panel lateral
        main.columnconfigure(1, weight=1)  # contenido
        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=0)

        # ------- Panel lateral (menú) -------
        side = ttk.Frame(main, style="Side.TFrame", width=260)
        side.grid(row=0, column=0, sticky="nswe")
        side.grid_propagate(False)

        # Título
        lbl_titulo = ttk.Label(
            side,
            text="Analizador de Código",
            style="Title.TLabel"
        )
        lbl_titulo.pack(anchor="w", padx=18, pady=(18, 2))

        lbl_sub = ttk.Label(
            side,
            text="Proyecto de Lenguajes y Autómatas II",
            style="Subtitle.TLabel"
        )
        lbl_sub.pack(anchor="w", padx=18, pady=(0, 16))

        # Línea decorativa
        sep = ttk.Separator(side, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=18, pady=(0, 12))

        # Botón principal (azul)
        btn1 = ttk.Button(
            side,
            text="1) Analizar (seleccionar archivo fuente)",
            style="Primary.TButton",
            command=self.analizar_archivo
        )
        btn1.pack(fill=tk.X, padx=18, pady=(0, 10))

        # Resto del menú
        btn2 = ttk.Button(
            side,
            text="2) Ver tabla de tokens",
            style="Menu.TButton",
            command=self.ver_tokens
        )
        btn3 = ttk.Button(
            side,
            text="3) Ver errores léxicos",
            style="Menu.TButton",
            command=self.ver_errores_lex
        )
        btn4 = ttk.Button(
            side,
            text="4) Analizar sintaxis",
            style="Menu.TButton",
            command=self.analizar_sintaxis
        )
        btn5 = ttk.Button(
            side,
            text="5) Salir",
            style="Menu.TButton",
            command=self.root.destroy
        )

        for btn in (btn2, btn3, btn4, btn5):
            btn.pack(fill=tk.X, padx=18, pady=4)

        # Créditos / info abajo
        side_bottom = ttk.Label(
            side,
            text="• Selecciona primero un archivo fuente\n• Luego puedes revisar tokens y errores",
            style="Subtitle.TLabel",
            justify="left"
        )
        side_bottom.pack(anchor="w", padx=18, pady=(20, 10))

        # ------- Área de contenido -------
        content = ttk.Frame(main, style="Main.TFrame")
        content.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=(0, 0))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        # Título de sección
        self.lbl_seccion = ttk.Label(
            content,
            text="Salida del analizador",
            style="Subtitle.TLabel"
        )
        self.lbl_seccion.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

        # Área de texto con scroll
        self.txt_salida = scrolledtext.ScrolledText(
            content,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg="#020617",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            borderwidth=1,
            relief="solid"
        )
        self.txt_salida.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))
        self.txt_salida.configure(state=tk.DISABLED)

        # ------- Barra de estado -------
        status_frame = ttk.Frame(main, style="Main.TFrame")
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        self.lbl_status = ttk.Label(
            status_frame,
            text="Listo.",
            style="Status.TLabel",
            anchor="w"
        )
        self.lbl_status.grid(row=0, column=0, sticky="ew", padx=16, pady=(0, 8))

    def _escribir_salida(self, texto, titulo="Salida del analizador"):
        self.txt_salida.configure(state=tk.NORMAL)
        self.txt_salida.delete(1.0, tk.END)
        self.txt_salida.insert(tk.END, texto)
        self.txt_salida.configure(state=tk.DISABLED)
        self.lbl_seccion.config(text=titulo)

    def _actualizar_status(self, texto):
        self.lbl_status.config(text=texto)

    # ---------- Opción 1: Analizar archivo ----------
    def analizar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona archivo fuente",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        self.ruta_fuente = ruta

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                codigo = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return

        self._actualizar_status("Analizando léxicamente el archivo seleccionado...")

        # Analizador léxico
        tokens, errores = scan(codigo)

        # Escribir Tokens.txt
        try:
            with open(self.ruta_tokens, "w", encoding="utf-8") as f:
                f.write(f"{'Lexema':<25}{'Token':<15}{'PTS':<10}{'Línea':<10}\n")
                for t in tokens:
                    if t.codigo in [-55, -56, -57, -58]:
                        pts = -2
                    else:
                        pts = -1
                    f.write(f"{t.lexema:<25}{t.codigo:<15}{pts:<10}{t.linea:<10}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escribir Tokens.txt:\n{e}")
            self._actualizar_status("Error al escribir Tokens.txt.")
            return

        # Escribir Errores.txt
        try:
            with open(self.ruta_errores_lex, "w", encoding="utf-8") as f:
                f.write(f"{'Lexema':<25}{'Descripción':<80}{'Línea':<10}\n")
                for e in errores:
                    f.write(f"{e.lexema:<25}{e.descripcion:<80}{e.linea:<10}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escribir Errores.txt:\n{e}")
            self._actualizar_status("Error al escribir Errores.txt.")
            return

        resumen = (
            "✔ Análisis léxico completado\n\n"
            f"Archivo fuente   : {os.path.basename(ruta)}\n"
            f"Tokens generados : {len(tokens)}\n"
            f"Errores léxicos  : {len(errores)}\n\n"
            f"Se generaron los archivos:\n"
            f"  • {os.path.abspath(self.ruta_tokens)}\n"
            f"  • {os.path.abspath(self.ruta_errores_lex)}\n"
        )

        self._escribir_salida(resumen, titulo="Resumen del análisis léxico")
        self._actualizar_status("Análisis léxico completado correctamente.")
        messagebox.showinfo("Éxito", "Análisis léxico completado.\nSe generaron Tokens.txt y Errores.txt.")

    # ---------- Opción 2: Ver tabla de tokens ----------
    def ver_tokens(self):
        if not os.path.exists(self.ruta_tokens):
            messagebox.showwarning(
                "Tokens.txt no encontrado",
                "Aún no se ha generado la tabla de tokens.\n"
                "Primero usa la opción 1) Analizar."
            )
            return
        try:
            with open(self.ruta_tokens, "r", encoding="utf-8") as f:
                contenido = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer Tokens.txt:\n{e}")
            return

        self._escribir_salida(contenido, titulo="Tabla de tokens (Tokens.txt)")
        self._actualizar_status("Mostrando contenido de Tokens.txt.")

    # ---------- Opción 3: Ver errores léxicos ----------
    def ver_errores_lex(self):
        if not os.path.exists(self.ruta_errores_lex):
            messagebox.showwarning(
                "Errores.txt no encontrado",
                "Aún no se ha generado la tabla de errores léxicos.\n"
                "Primero usa la opción 1) Analizar."
            )
            return
        try:
            with open(self.ruta_errores_lex, "r", encoding="utf-8") as f:
                contenido = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer Errores.txt:\n{e}")
            return

        self._escribir_salida(contenido, titulo="Errores léxicos (Errores.txt)")
        self._actualizar_status("Mostrando contenido de Errores.txt.")

    # ---------- Opción 4: Analizar sintaxis ----------
    def analizar_sintaxis(self):
        if not os.path.exists(self.ruta_tokens):
            messagebox.showwarning(
                "Tokens.txt no encontrado",
                "Primero debes generar la tabla de tokens (opción 1)."
            )
            return

        self._actualizar_status("Realizando análisis sintáctico...")

        try:
            tokens = cargar_tokens_desde_tabla(self.ruta_tokens)
            parser = Parser(tokens)
            parser.parse()  # genera Errores_Sintácticos.txt
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis sintáctico:\n{e}")
            self._actualizar_status("Error durante el análisis sintáctico.")
            return

        # Mostrar resultado
        if os.path.exists(self.ruta_errores_sint):
            try:
                with open(self.ruta_errores_sint, "r", encoding="utf-8") as f:
                    contenido = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer Errores_Sintácticos.txt:\n{e}")
                self._actualizar_status("Error al leer Errores_Sintácticos.txt.")
                return

            titulo = "Errores sintácticos (Errores_Sintácticos.txt)"
            if "SIN ERRORES" in contenido.upper():
                titulo = "Análisis sintáctico sin errores"
            self._escribir_salida(contenido, titulo=titulo)
        else:
            if not getattr(parser, "errores", []):
                self._escribir_salida("Análisis sintáctico completado SIN ERRORES.\n",
                                      titulo="Análisis sintáctico sin errores")
            else:
                texto = "ANÁLISIS SINTÁCTICO\n\n" + "\n".join(parser.errores)
                self._escribir_salida(texto, titulo="Errores sintácticos")

        self._actualizar_status("Análisis sintáctico finalizado.")
        messagebox.showinfo("Listo", "Análisis sintáctico terminado.\nRevisa la salida en la ventana.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorGUI(root)
    root.mainloop()
