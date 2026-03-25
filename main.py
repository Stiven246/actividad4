"""
╔══════════════════════════════════════════════════════════════╗
║        DETECTOR DE EMOCIONES FACIALES — APP CLAUDE          ║
║   SENA Tolima · Curso: Aplicación de Apps de IA · 2026      ║
╚══════════════════════════════════════════════════════════════╝

Descripción:
    Aplicación de escritorio en Python que detecta emociones
    faciales en imágenes estáticas usando el modelo DeepFace.
    Diseño visual con identidad propia: fondo oscuro, colores
    por emoción y gráfica de barras de confianza.

Autor generado por: Claude (Anthropic) — Actividad 4
Prerrequisitos: Python 3.8+, ver requirements.txt
"""

import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
import threading
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np

# ──────────────────────────────────────────────
# CONSTANTES DE TRADUCCIÓN Y COLORES POR EMOCIÓN
# ──────────────────────────────────────────────
TRADUCCIONES = {
    "happy":    "Feliz",
    "sad":      "Triste",
    "angry":    "Enojado",
    "fear":     "Miedo",
    "surprise": "Sorpresa",
    "disgust":  "Disgusto",
    "neutral":  "Neutral",
}

COLORES_EMOCION = {
    "happy":    "#FFD700",   # Dorado
    "sad":      "#4A90D9",   # Azul
    "angry":    "#E74C3C",   # Rojo
    "fear":     "#9B59B6",   # Violeta
    "surprise": "#F39C12",   # Naranja
    "disgust":  "#27AE60",   # Verde
    "neutral":  "#95A5A6",   # Gris
}

EMOJI_EMOCION = {
    "happy":    "😄",
    "sad":      "😢",
    "angry":    "😠",
    "fear":     "😨",
    "surprise": "😲",
    "disgust":  "🤢",
    "neutral":  "😐",
}

# Paleta de diseño
BG_DARK      = "#1A1A2E"
BG_PANEL     = "#16213E"
BG_CARD      = "#0F3460"
ACCENT       = "#E94560"
TEXT_LIGHT   = "#EAEAEA"
TEXT_MUTED   = "#8899AA"
BAR_BG       = "#0D2137"


# ──────────────────────────────────────────────
# MÓDULO DE ANÁLISIS (alta cohesión, bajo acoplamiento)
# ──────────────────────────────────────────────
class AnalizadorEmociones:
    """Encapsula toda la lógica de análisis con DeepFace."""

    def analizar(self, ruta_imagen: str) -> dict:
        """
        Analiza la emoción dominante en una imagen.

        Args:
            ruta_imagen: Ruta absoluta al archivo de imagen.

        Returns:
            dict con claves:
              - emocion_dominante (str, en inglés)
              - emociones (dict: nombre -> porcentaje)
              - region (dict: x, y, w, h del bounding box)

        Raises:
            ValueError: Si no se detecta ningún rostro.
            Exception:  Cualquier otro error de DeepFace.
        """
        from deepface import DeepFace  # Import tardío para no bloquear arranque

        resultados = DeepFace.analyze(
            img_path=ruta_imagen,
            actions=["emotion"],
            enforce_detection=True,   # Lanza excepción si no hay rostro
            silent=True,
        )

        # DeepFace devuelve lista; tomamos el primer rostro
        r = resultados[0]
        return {
            "emocion_dominante": r["dominant_emotion"],
            "emociones": r["emotion"],           # dict {str: float}
            "region": r["region"],               # {x, y, w, h}
        }


# ──────────────────────────────────────────────
# MÓDULO DE IMAGEN (dibujar bounding box)
# ──────────────────────────────────────────────
class ProcesadorImagen:
    """Dibuja el bounding box y prepara la imagen para mostrar en la GUI."""

    MAX_W = 520
    MAX_H = 400

    def dibujar_bbox(self, ruta: str, region: dict, color_hex: str) -> ImageTk.PhotoImage:
        """
        Abre la imagen, dibuja el rectángulo y la escala para la GUI.

        Returns:
            ImageTk.PhotoImage listo para insertar en un Label de Tkinter.
        """
        img = Image.open(ruta).convert("RGB")
        draw = ImageDraw.Draw(img)

        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        # Color RGB desde hex
        r_c, g_c, b_c = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)

        # Rectángulo con grosor visible
        for grosor in range(4):
            draw.rectangle(
                [x - grosor, y - grosor, x + w + grosor, y + h + grosor],
                outline=(r_c, g_c, b_c)
            )

        # Escalar manteniendo relación de aspecto
        img.thumbnail((self.MAX_W, self.MAX_H), Image.LANCZOS)
        return ImageTk.PhotoImage(img)


# ──────────────────────────────────────────────
# INTERFAZ GRÁFICA PRINCIPAL
# ──────────────────────────────────────────────
class AppDetectorEmociones(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Detector de Emociones · SENA Tolima 2026")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        self._analizador   = AnalizadorEmociones()
        self._procesador   = ProcesadorImagen()
        self._ruta_actual  = None        # Ruta de la imagen cargada
        self._photo_ref    = None        # Referencia para evitar GC de PhotoImage
        self._analizando   = False       # Bandera anti-doble-clic

        self._construir_ui()
        self._centrar_ventana(950, 680)

    # ── Construcción de la UI ────────────────────
    def _construir_ui(self):
        """Construye todos los widgets de la interfaz."""
        self._crear_header()
        contenedor = tk.Frame(self, bg=BG_DARK)
        contenedor.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._crear_panel_imagen(contenedor)
        self._crear_panel_resultados(contenedor)
        self._crear_barra_estado()

    def _crear_header(self):
        header = tk.Frame(self, bg=BG_PANEL, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🧠  DETECTOR DE EMOCIONES FACIALES",
                 bg=BG_PANEL, fg=TEXT_LIGHT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=16)

        tk.Label(header, text="SENA · Aplicación de Apps de IA · 2026",
                 bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

    def _crear_panel_imagen(self, padre):
        panel = tk.Frame(padre, bg=BG_PANEL, width=560)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        panel.pack_propagate(False)

        # Zona de previsualización
        self._canvas_img = tk.Label(
            panel, bg=BG_CARD, cursor="hand2",
            text="📂  Haz clic en 'Cargar Foto'\npara comenzar",
            fg=TEXT_MUTED, font=("Segoe UI", 12),
            width=52, height=22, relief="flat"
        )
        self._canvas_img.pack(padx=12, pady=(12, 8), fill="both", expand=True)

        # Botones
        btn_frame = tk.Frame(panel, bg=BG_PANEL)
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        self._btn_cargar = tk.Button(
            btn_frame, text="📂  Cargar Foto",
            command=self._cargar_imagen,
            bg="#0F3460", fg=TEXT_LIGHT,
            font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2",
            activebackground="#1a4a80", activeforeground=TEXT_LIGHT,
            padx=16, pady=10
        )
        self._btn_cargar.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._btn_analizar = tk.Button(
            btn_frame, text="🔍  Analizar Emoción",
            command=self._iniciar_analisis,
            bg=ACCENT, fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2",
            activebackground="#c0392b", activeforeground="white",
            padx=16, pady=10, state="disabled"
        )
        self._btn_analizar.pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _crear_panel_resultados(self, padre):
        panel = tk.Frame(padre, bg=BG_PANEL, width=360)
        panel.pack(side="right", fill="both", padx=(8, 0), pady=8)
        panel.pack_propagate(False)

        tk.Label(panel, text="RESULTADO",
                 bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 0))

        # Card de emoción dominante
        self._card_emocion = tk.Frame(panel, bg=BG_CARD, height=100)
        self._card_emocion.pack(fill="x", padx=12, pady=(4, 8))
        self._card_emocion.pack_propagate(False)

        self._lbl_emoji = tk.Label(self._card_emocion, text="❓",
                                    bg=BG_CARD, fg=TEXT_LIGHT,
                                    font=("Segoe UI", 36))
        self._lbl_emoji.pack(side="left", padx=16)

        info_frame = tk.Frame(self._card_emocion, bg=BG_CARD)
        info_frame.pack(side="left", fill="both", expand=True)

        self._lbl_emocion = tk.Label(info_frame, text="Sin analizar",
                                      bg=BG_CARD, fg=TEXT_MUTED,
                                      font=("Segoe UI", 18, "bold"))
        self._lbl_emocion.pack(anchor="w", pady=(14, 0))

        self._lbl_confianza = tk.Label(info_frame, text="Confianza: —",
                                        bg=BG_CARD, fg=TEXT_MUTED,
                                        font=("Segoe UI", 10))
        self._lbl_confianza.pack(anchor="w")

        # Sección de barras de confianza
        tk.Label(panel, text="DISTRIBUCIÓN DE EMOCIONES",
                 bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(4, 0))

        self._frame_barras = tk.Frame(panel, bg=BG_PANEL)
        self._frame_barras.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self._barras_widgets = {}
        for emocion in TRADUCCIONES:
            fila = tk.Frame(self._frame_barras, bg=BG_PANEL)
            fila.pack(fill="x", pady=2)

            lbl = tk.Label(fila, text=TRADUCCIONES[emocion],
                           bg=BG_PANEL, fg=TEXT_MUTED,
                           font=("Segoe UI", 9), width=9, anchor="w")
            lbl.pack(side="left")

            barra_bg = tk.Frame(fila, bg=BAR_BG, height=16)
            barra_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))
            barra_bg.pack_propagate(False)

            barra_fill = tk.Frame(barra_bg, bg=COLORES_EMOCION[emocion], height=16, width=0)
            barra_fill.place(x=0, y=0, relheight=1)

            lbl_pct = tk.Label(fila, text="0%",
                               bg=BG_PANEL, fg=TEXT_MUTED,
                               font=("Segoe UI", 9), width=5, anchor="e")
            lbl_pct.pack(side="right")

            self._barras_widgets[emocion] = (barra_bg, barra_fill, lbl_pct)

    def _crear_barra_estado(self):
        self._estado_var = tk.StringVar(value="Listo. Carga una foto para comenzar.")
        bar = tk.Frame(self, bg=BG_PANEL, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Label(bar, textvariable=self._estado_var,
                 bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=12, pady=4)

    # ── Lógica de carga y análisis ───────────────
    def _cargar_imagen(self):
        """Abre el diálogo de archivo y muestra la imagen seleccionada."""
        tipos = [("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp"),
                 ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(title="Seleccionar foto", filetypes=tipos)
        if not ruta:
            return

        self._ruta_actual = ruta
        self._estado_var.set(f"Imagen cargada: {Path(ruta).name}")
        self._btn_analizar.config(state="normal")

        # Mostrar previsualización
        try:
            img = Image.open(ruta).convert("RGB")
            img.thumbnail((520, 400), Image.LANCZOS)
            self._photo_ref = ImageTk.PhotoImage(img)
            self._canvas_img.config(image=self._photo_ref, text="")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer la imagen:\n{e}")

        # Limpiar resultados anteriores
        self._resetear_resultados()

    def _iniciar_analisis(self):
        """Lanza el análisis en un hilo separado para no bloquear la GUI."""
        if self._analizando or not self._ruta_actual:
            return

        self._analizando = True
        self._btn_analizar.config(state="disabled", text="⏳  Analizando...")
        self._estado_var.set("Analizando imagen… esto puede tardar unos segundos.")

        hilo = threading.Thread(target=self._ejecutar_analisis, daemon=True)
        hilo.start()

    def _ejecutar_analisis(self):
        """Corre en hilo secundario; llama a DeepFace y regresa al hilo principal."""
        try:
            datos = self._analizador.analizar(self._ruta_actual)
            self.after(0, self._mostrar_resultados, datos)
        except Exception as e:
            mensaje = self._interpretar_error(str(e))
            self.after(0, self._mostrar_error, mensaje)
        finally:
            self.after(0, self._finalizar_analisis)

    def _mostrar_resultados(self, datos: dict):
        """Actualiza la UI con los resultados del análisis (hilo principal)."""
        emocion_key  = datos["emocion_dominante"]
        emociones    = datos["emociones"]
        region       = datos["region"]
        color        = COLORES_EMOCION.get(emocion_key, ACCENT)
        nombre_es    = TRADUCCIONES.get(emocion_key, emocion_key.capitalize())
        emoji        = EMOJI_EMOCION.get(emocion_key, "❓")
        pct_dominante = emociones.get(emocion_key, 0)

        # Imagen con bounding box
        try:
            foto = self._procesador.dibujar_bbox(self._ruta_actual, region, color)
            self._photo_ref = foto
            self._canvas_img.config(image=foto, text="")
        except Exception:
            pass  # Si falla el bbox, mantenemos la imagen original

        # Card de emoción dominante
        self._card_emocion.config(bg=color + "33")  # 20% opacidad hex
        self._lbl_emoji.config(text=emoji, bg=color + "33")
        self._lbl_emocion.config(text=nombre_es, fg=color, bg=color + "33")
        self._lbl_confianza.config(
            text=f"Confianza: {pct_dominante:.1f}%", fg=TEXT_LIGHT, bg=color + "33"
        )

        # Barras de porcentaje
        self._after_barras_animadas(emociones)

        self._estado_var.set(
            f"✅  Emoción detectada: {nombre_es}  ({pct_dominante:.1f}% de confianza)"
        )

    def _after_barras_animadas(self, emociones: dict, paso: int = 0):
        """Anima las barras de confianza incrementalmente."""
        MAX_PASOS = 20
        if paso > MAX_PASOS:
            return

        factor = paso / MAX_PASOS  # 0.0 → 1.0

        for emocion_key, (barra_bg, barra_fill, lbl_pct) in self._barras_widgets.items():
            pct = emociones.get(emocion_key, 0) * factor
            ancho_total = barra_bg.winfo_width()
            if ancho_total < 2:
                ancho_total = 200  # fallback antes del primer render
            ancho_fill = int(ancho_total * pct / 100)
            barra_fill.place(x=0, y=0, width=ancho_fill, relheight=1)
            lbl_pct.config(text=f"{pct:.1f}%")

        self.after(16, self._after_barras_animadas, emociones, paso + 1)

    def _mostrar_error(self, mensaje: str):
        """Muestra un error amigable sin cerrar la aplicación."""
        self._resetear_resultados()
        messagebox.showwarning("Sin resultado", mensaje)
        self._estado_var.set("⚠️  " + mensaje)

    def _finalizar_analisis(self):
        """Restaura botones al terminar (éxito o error)."""
        self._analizando = False
        self._btn_analizar.config(state="normal", text="🔍  Analizar Emoción")

    def _resetear_resultados(self):
        """Limpia el panel de resultados."""
        self._card_emocion.config(bg=BG_CARD)
        self._lbl_emoji.config(text="❓", bg=BG_CARD)
        self._lbl_emocion.config(text="Sin analizar", fg=TEXT_MUTED, bg=BG_CARD)
        self._lbl_confianza.config(text="Confianza: —", fg=TEXT_MUTED, bg=BG_CARD)
        for _, (barra_bg, barra_fill, lbl_pct) in self._barras_widgets.items():
            barra_fill.place(width=0)
            lbl_pct.config(text="0%")

    # ── Utilidades ───────────────────────────────
    @staticmethod
    def _interpretar_error(msg: str) -> str:
        """Traduce mensajes de error técnicos a texto amigable."""
        msg_lower = msg.lower()
        if "face could not be detected" in msg_lower or "no face" in msg_lower:
            return (
                "No se detectó ningún rostro en la imagen.\n\n"
                "Sugerencias:\n"
                "• Usa una foto con el rostro de frente y bien iluminado.\n"
                "• El rostro debe ocupar al menos el 30% de la imagen.\n"
                "• Evita imágenes muy pequeñas o con baja resolución."
            )
        if "cannot identify image file" in msg_lower:
            return "El archivo seleccionado no es una imagen válida."
        return f"Error al analizar la imagen:\n{msg}"

    def _centrar_ventana(self, ancho: int, alto: int):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - ancho) // 2
        y = (sh - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = AppDetectorEmociones()
    app.mainloop()
