import tkinter as tk
from fractions import Fraction

# --- Colores ---
COLOR_FONDO      = "#1c1c1e"
COLOR_TEXTO      = "#ffffff"
COLOR_EXPRESION  = "#888888"
COLOR_BTN_NUM    = "#2c2c2e"
COLOR_BTN_OP     = "#f5c518"
COLOR_BTN_FUNC   = "#505050"
COLOR_TEXTO_OP   = "#000000"

# --- Ventana ---
ventana = tk.Tk()
ventana.title("Calculadora")
ventana.resizable(False, False)
ventana.configure(bg=COLOR_FONDO)

ancho = 360
alto  = 680
x = (ventana.winfo_screenwidth()  // 2) - (ancho // 2)
y = (ventana.winfo_screenheight() // 2) - (alto  // 2)
ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# --- Clase botón redondeado ---
class BotonRedondo(tk.Canvas):
    def __init__(self, padre, texto, comando, bg, fg, radio=28, **kwargs):
        super().__init__(padre, bg=COLOR_FONDO, highlightthickness=0, **kwargs)
        self.comando  = comando
        self.bg       = bg
        self.fg       = fg
        self.texto    = texto
        self.radio    = radio
        self.hover_bg = self._aclarar(bg)

        self.bind("<Configure>",       self._dibujar)
        self.bind("<Button-1>",        self._al_clicar)
        self.bind("<Enter>",           self._hover_on)
        self.bind("<Leave>",           self._hover_off)

    def _aclarar(self, hex_color):
        # Aclara el color un 20% para el efecto hover
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * 0.20))
        g = min(255, int(g + (255 - g) * 0.20))
        b = min(255, int(b + (255 - b) * 0.20))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _dibujar(self, evento=None, color=None):
        self.delete("all")
        color = color or self.bg
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radio
        # Rectángulo redondeado
        self.create_arc( 0,     0,     r*2, r*2, start=90,  extent=90, fill=color, outline=color)
        self.create_arc( w-r*2, 0,     w,   r*2, start=0,   extent=90, fill=color, outline=color)
        self.create_arc( 0,     h-r*2, r*2, h,   start=180, extent=90, fill=color, outline=color)
        self.create_arc( w-r*2, h-r*2, w,   h,   start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h,   fill=color, outline=color)
        self.create_rectangle(0, r, w,   h-r, fill=color, outline=color)
        # Texto
        tam = 20 if len(self.texto) <= 2 else 16
        self.create_text(w//2, h//2, text=self.texto, fill=self.fg,
                         font=("Arial", tam, "bold"))

    def _al_clicar(self, evento=None):
        if self.comando:
            self.comando()

    def _hover_on(self, evento=None):
        self._dibujar(color=self.hover_bg)

    def _hover_off(self, evento=None):
        self._dibujar(color=self.bg)

    def config_boton(self, texto=None, comando=None, bg=None, fg=None):
        if texto:   self.texto   = texto
        if comando: self.comando = comando
        if bg:
            self.bg       = bg
            self.hover_bg = self._aclarar(bg)
        if fg:      self.fg = fg
        self._dibujar()

# --- Pantalla ---
texto_expresion = tk.StringVar(value="")

frame_pantalla = tk.Frame(ventana, bg=COLOR_FONDO, padx=16, pady=8)
frame_pantalla.pack(fill="x")

expresion_label = tk.Label(
    frame_pantalla,
    textvariable=texto_expresion,
    font=("Arial", 16),
    bg=COLOR_FONDO,
    fg=COLOR_EXPRESION,
    anchor="e",
    padx=16,
)
expresion_label.pack(fill="x")

pantalla = tk.Entry(
    frame_pantalla,
    font=("Arial", 52),
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO,
    justify="right",
    bd=0,
    highlightthickness=0,
    insertbackground=COLOR_TEXTO,
    selectbackground="#444444",
    selectforeground=COLOR_TEXTO,
)
pantalla.pack(fill="x", padx=16, pady=(0, 16))
pantalla.insert(0, "0")
pantalla.focus_set()

# Línea separadora
separador = tk.Frame(ventana, bg="#3a3a3c", height=1)
separador.pack(fill="x", padx=12)

# --- Helpers ---
def get_pantalla():
    return pantalla.get()

def set_pantalla(valor):
    pantalla.delete(0, tk.END)
    pantalla.insert(0, valor)
    pantalla.icursor(tk.END)
    pantalla.xview(tk.END)
    ajustar_fuente()

def ajustar_fuente():
    largo = len(get_pantalla())
    if largo <= 9:    tam = 52
    elif largo <= 12: tam = 40
    elif largo <= 16: tam = 30
    else:             tam = 22
    pantalla.config(font=("Arial", tam))

# --- Lógica ---
def al_pulsar(valor):
    actual = get_pantalla()
    if actual == "0" or actual == "Error":
        set_pantalla(valor)
    else:
        pos = pantalla.index(tk.INSERT)
        pantalla.insert(pos, valor)
        pantalla.xview(tk.INSERT)
        ajustar_fuente()

def borrar_ultimo():
    actual = get_pantalla()
    if len(actual) <= 1:
        set_pantalla("0")
    else:
        pos = pantalla.index(tk.INSERT)
        if pos > 0:
            pantalla.delete(pos - 1, pos)
            ajustar_fuente()

def borrar_todo():
    set_pantalla("0")
    texto_expresion.set("")

def negativo():
    actual = get_pantalla()
    try:
        numero = float(actual)
        resultado = -numero
        if resultado == int(resultado):
            set_pantalla(str(int(resultado)))
        else:
            set_pantalla(str(resultado))
    except:
        pass

def formatear_resultado(numero):
    if numero == int(numero):
        return str(int(numero))
    signo   = "-" if numero < 0 else ""
    abs_num = abs(numero)
    frac    = Fraction(abs_num).limit_denominator(10**7)
    num, den = frac.numerator, frac.denominator
    temp = den
    while temp % 2 == 0: temp //= 2
    while temp % 5 == 0: temp //= 5
    if temp == 1:
        return signo + f"{abs_num:.10f}".rstrip("0").rstrip(".")
    parte_entera = num // den
    resto = num % den
    decimales, restos_vistos = [], {}
    while resto != 0 and resto not in restos_vistos and len(decimales) < 20:
        restos_vistos[resto] = len(decimales)
        resto *= 10
        decimales.append(str(resto // den))
        resto %= den
    if resto == 0:
        return (signo + f"{parte_entera}.{''.join(decimales)}").rstrip("0").rstrip(".")
    inicio    = restos_vistos[resto]
    fija      = ''.join(decimales[:inicio])
    periodica = ''.join(decimales[inicio:])
    if len(periodica) > 3 or len(fija) + len(periodica) > 6:
        return signo + f"{round(abs_num, 5):.5f}".rstrip("0").rstrip(".")
    return f"{signo}{parte_entera}.{fija}{''.join(d + chr(772) for d in periodica)}"

def calcular():
    actual = get_pantalla()
    try:
        expresion = actual.replace("×","*").replace("÷","/").replace("^","**")
        resultado = eval(expresion)
        texto_expresion.set(actual + " =")
        set_pantalla(formatear_resultado(resultado))
    except:
        set_pantalla("Error")

# --- Teclado ---
def tecla_presionada(evento):
    tecla = evento.keysym
    char  = evento.char
    if tecla in ("Left", "Right", "Home", "End"):
        return
    if char in "0123456789.":          al_pulsar(char)
    elif char == "+":                  al_pulsar("+")
    elif char == "-":                  al_pulsar("-")
    elif char in ("*", "x", "X"):     al_pulsar("×")
    elif char == "/":                  al_pulsar("÷")
    elif char in ("(",")","%","^"):    al_pulsar(char)
    elif tecla in ("Return","KP_Enter") or char == "=": calcular()
    elif tecla == "BackSpace":         borrar_ultimo()
    elif tecla in ("Escape","Delete"): borrar_todo()
    ajustar_fuente()
    return "break"

pantalla.bind("<Key>", tecla_presionada)

# --- Panel 2nd ---
modo_secundario     = False
referencias_botones = {}

botones_alternos = {
    (0, 1): ("+/-", lambda: negativo(),      "(", lambda: al_pulsar("(")),
    (0, 2): ("⌫",   lambda: borrar_ultimo(), ")", lambda: al_pulsar(")")),
    (1, 3): ("×",   lambda: al_pulsar("×"), "%", lambda: al_pulsar("%")),
    (2, 3): ("-",   lambda: al_pulsar("-"), "^", lambda: al_pulsar("^")),
}

def toggle_2nd():
    global modo_secundario
    modo_secundario = not modo_secundario
    for (fila, col), (t1, c1, t2, c2) in botones_alternos.items():
        btn = referencias_botones[(fila, col)]
        if modo_secundario:
            btn.config_boton(texto=t2, comando=c2, fg=COLOR_TEXTO_OP, bg=COLOR_BTN_OP)
        else:
            bg = COLOR_BTN_FUNC if col < 3 else COLOR_BTN_OP
            fg = COLOR_TEXTO    if col < 3 else COLOR_TEXTO_OP
            btn.config_boton(texto=t1, comando=c1, bg=bg, fg=fg)

# --- Botones ---
frame_botones = tk.Frame(ventana, bg=COLOR_FONDO, padx=12, pady=16)
frame_botones.pack(fill="both", expand=True)

botones = [
    ("AC",  0, 0, COLOR_BTN_FUNC, COLOR_TEXTO),
    ("+/-", 0, 1, COLOR_BTN_FUNC, COLOR_TEXTO),
    ("⌫",   0, 2, COLOR_BTN_FUNC, COLOR_TEXTO),
    ("÷",   0, 3, COLOR_BTN_OP,   COLOR_TEXTO_OP),
    ("7",   1, 0, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("8",   1, 1, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("9",   1, 2, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("×",   1, 3, COLOR_BTN_OP,   COLOR_TEXTO_OP),
    ("4",   2, 0, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("5",   2, 1, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("6",   2, 2, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("-",   2, 3, COLOR_BTN_OP,   COLOR_TEXTO_OP),
    ("1",   3, 0, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("2",   3, 1, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("3",   3, 2, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("+",   3, 3, COLOR_BTN_OP,   COLOR_TEXTO_OP),
    ("2nd", 4, 0, COLOR_BTN_FUNC, COLOR_TEXTO),
    ("0",   4, 1, COLOR_BTN_NUM,  COLOR_TEXTO),
    (".",   4, 2, COLOR_BTN_NUM,  COLOR_TEXTO),
    ("=",   4, 3, COLOR_BTN_OP,   COLOR_TEXTO_OP),
]

for (texto, fila, col, bg, fg) in botones:
    if texto == "=":      cmd = calcular
    elif texto == "AC":   cmd = borrar_todo
    elif texto == "⌫":   cmd = borrar_ultimo
    elif texto == "+/-":  cmd = negativo
    elif texto == "2nd":  cmd = toggle_2nd
    else:                 cmd = lambda v=texto: al_pulsar(v)

    btn = BotonRedondo(
        frame_botones,
        texto=texto,
        comando=cmd,
        bg=bg,
        fg=fg,
    )
    btn.grid(row=fila, column=col, padx=5, pady=5, sticky="nsew")

    if (fila, col) in botones_alternos:
        referencias_botones[(fila, col)] = btn

for i in range(5):
    frame_botones.rowconfigure(i, weight=1)
for j in range(4):
    frame_botones.columnconfigure(j, weight=1)

ventana.mainloop()