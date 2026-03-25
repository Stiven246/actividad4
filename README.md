# 🧠 Detector de Emociones Faciales — App Claude
**SENA Tolima · Curso: Aplicación de Apps de IA · Actividad 4 · 2026**

Aplicación de escritorio en Python que detecta la emoción facial dominante en imágenes estáticas usando el modelo **DeepFace**. Interfaz oscura con colores dinámicos por emoción y gráfica animada de confianza.

---

## 📋 Requisitos previos

| Componente | Versión mínima |
|---|---|
| Python | 3.8 |
| pip | 22+ |
| Conexión a internet | Solo la primera ejecución (~500 MB de modelos) |

---

## 🚀 Instalación paso a paso (Windows)

```bash
# 1. Clona o descarga este repositorio
git clone https://github.com/TU_USUARIO/emotion-detector-TUNOMBRE.git
cd emotion-detector-TUNOMBRE

# 2. Crea y activa el entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Ejecuta la aplicación
python main.py
```

### Para macOS / Linux:
```bash
source venv/bin/activate   # en lugar del paso de activate de Windows
```

---

## ▶️ Uso

1. Haz clic en **"📂 Cargar Foto"** y selecciona una imagen JPG o PNG.
2. Haz clic en **"🔍 Analizar Emoción"**.
3. Espera unos segundos (la primera vez descarga ~500 MB de modelos).
4. Observa:
   - La imagen con un rectángulo de colores alrededor del rostro detectado.
   - La emoción dominante traducida al español con emoji.
   - Las barras de confianza para las 7 emociones universales.

---

## 💡 Consejos para mejores resultados

- Usa fotos con el **rostro de frente**, bien iluminado.
- El rostro debe ocupar **al menos el 30%** de la imagen.
- Evita imágenes con resolución menor a 200×200 px.
- Formatos compatibles: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

---

## 🗂️ Estructura del proyecto

```
app_claude/
├── main.py           # Código principal de la aplicación
├── requirements.txt  # Dependencias Python
├── README.md         # Este archivo
└── .gitignore        # Excluye venv y modelos de DeepFace
```

---

## ⚠️ Errores comunes

| Error | Solución |
|---|---|
| `Face could not be detected` | La foto no tiene rostro visible. Prueba con otra imagen. |
| `ModuleNotFoundError: deepface` | Activa el entorno virtual y reinstala: `pip install -r requirements.txt` |
| La app tarda mucho la primera vez | Normal: está descargando ~500 MB de modelos. Espera con internet estable. |
| `_tkinter.TclError` | Asegúrate de tener Tkinter instalado (`python -m tkinter` para verificar). |

---

## 📦 Dependencias principales

- **DeepFace** — Análisis facial con modelos preentrenados (VGG-Face, ArcFace, etc.)
- **Pillow** — Manipulación y visualización de imágenes en Tkinter
- **OpenCV** — Procesamiento interno de DeepFace
- **TF-Keras** — Backend de los modelos de deep learning

---

## 📄 Licencia

Proyecto educativo — SENA Regional Tolima, Centro de Industria y Construcción.
