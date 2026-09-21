"""=============================================================================
LA HUACA AI - ASISTENTE VIRTUAL POR VOZ PARA RESTAURANTE
Tarea Académica 2 - Herramientas de Desarrollo Profesional TIC

Tecnologías:
- Streamlit (UI/UX Adaptada al Frontend de La Huaca, Modo Compacto & Sin Sidebar)
- Groq API:
    * Whisper-large-v3 (Transcripción de Voz a Texto)
    * Qwen/Qwen3.8-27b & OpenAI GPT-OSS (LLM con Function Calling)
- SQLite + SQLModel (Base de datos real del restaurante)
=============================================================================
"""

import os
import sys
import json
import hashlib
from datetime import date, time, datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from sqlmodel import Session

# Asegurar path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Importar conexión real y servicios de backend
from app.database import engine
from app.services.restaurant_service import (
    get_menu,
    get_opening_hours,
    request_table_reservation,
)

# Cargar variables de entorno (.env)
load_dotenv()

# =============================================================================
# 1. CONFIGURACIÓN DE PÁGINA (MODO COMPACTO PARA WIDGET Y MODAL)
# =============================================================================
st.set_page_config(
    page_title="La Huaca AI",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS con la paleta de colores del Frontend (Vino Tinto, Oro y Crema)
st.markdown(
    """
    <style>
    /* Ocultar barra lateral y botones de colapso de Streamlit */
    [data-testid="stSidebar"], 
    [data-testid="collapsedControl"],
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Contenedor principal centrado con ancho equilibrado para pestaña completa y modal */
    .block-container {
        padding: 0.8rem 1rem 1.2rem 1rem !important;
        max-width: 740px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: 100% !important;
    }

    [data-testid="stBottomBlockContainer"] {
        max-width: 740px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.8rem !important;
    }

    div[data-testid="stChatInput"] {
        margin-top: 0 !important;
    }

    /* Encabezado limpio sin borde interno */
    .chat-header-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 6px;
        margin-bottom: 0 !important;
    }

    /* Separadores */
    .chat-separator {
        width: 100%;
        height: 1px;
        background-color: #e6d8c8;
        padding: 0 !important;
    }

    .chat-separator-top {
        margin-top: 10px !important;
        margin-bottom: 14px !important;
    }

    .chat-separator-bottom {
        margin-top: -10px !important;
        margin-bottom: 0 !important;
    }

    /* Forzar diseño 2x2 para las sugerencias rápidas en cualquier pantalla/modal */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-bottom: 0px !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: 50% !important;
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }
    .chat-brand-icon {
        font-size: 1.8rem;
        line-height: 1;
    }
    .hero-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #5c1220 !important; /* Vino tinto corporativo */
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.15 !important;
    }
    .hero-subtitle {
        font-size: 0.8rem !important;
        color: #6b5c52 !important; /* Texto atenuado café */
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* Badges con color oro y vino tinto */
    .badge-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.55rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(217, 164, 65, 0.15);
        color: #5c1220;
        border: 1px solid rgba(92, 18, 32, 0.2);
        margin-right: 0.3rem;
    }

    /* Botones de sugerencia rápida estilo frontend */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #5c1220 !important;
        border: 1px solid #e6d8c8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 0.35rem 0.5rem !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        overflow: hidden !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #fbf1e7 !important;
        border-color: #5c1220 !important;
        color: #5c1220 !important;
    }

    /* Burbujas de chat estilizadas y ordenadas */
    div[data-testid="stChatMessage"] {
        padding: 0.5rem 0.75rem !important;
        border-radius: 10px !important;
        margin-bottom: 0.35rem !important;
    }

    /* Transcripción destacada */
    .transcription-tag {
        background-color: #fbf1e7;
        border-left: 3px solid #d9a441;
        padding: 0.4rem 0.7rem;
        font-size: 0.85rem;
        color: #5c1220;
        border-radius: 4px;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# 2. DEFINICIÓN DE TOOLS PARA FUNCTION CALLING (GROQ)
# =============================================================================
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "consultar_menu",
            "description": "Consulta la carta de platos peruanos en la base de datos real. Retorna nombres, descripciones, precios y categorías.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": ["string", "null"],
                        "description": "Filtro opcional por categoría: 'Entradas', 'Platos de Fondo', 'Postres', 'Bebidas'. Si se omite o es null, devuelve toda la carta.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_horario",
            "description": "Consulta los horarios de atención y días de apertura y cierre del restaurante en la base de datos SQLite.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dia_semana": {
                        "type": ["string", "null"],
                        "description": "Día de la semana a consultar (ej: 'lunes', 'viernes', 'domingo' o 'monday', 'friday'). Si se omite o es null, devuelve todos los días.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "solicitar_reserva_mesa",
            "description": "Registra una reserva formal de mesa en la base de datos. Requiere OBLIGATORIAMENTE los 5 datos solicitados al cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_cliente": {
                        "type": "string",
                        "description": "Nombre completo de la persona que realiza la reserva.",
                    },
                    "telefono": {
                        "type": "string",
                        "description": "Número de celular o teléfono de contacto.",
                    },
                    "fecha": {
                        "type": "string",
                        "description": "Fecha de la reserva en formato 'YYYY-MM-DD' (ej: '2026-09-22').",
                    },
                    "hora": {
                        "type": "string",
                        "description": "Hora de la reserva en formato 24 horas 'HH:MM' (ej: '13:30', '20:00').",
                    },
                    "numero_personas": {
                        "type": "integer",
                        "description": "Cantidad de comensales (mínimo 1, máximo 20).",
                    },
                },
                "required": [
                    "nombre_cliente",
                    "telefono",
                    "fecha",
                    "hora",
                    "numero_personas",
                ],
            },
        },
    },
]

DIAS_TRADUCCION = {
    "lunes": "monday",
    "martes": "tuesday",
    "miercoles": "wednesday",
    "miércoles": "wednesday",
    "jueves": "thursday",
    "viernes": "friday",
    "sabado": "saturday",
    "sábado": "saturday",
    "domingo": "sunday",
}

# =============================================================================
# 3. EJECUCIÓN REAL DE FUNCIONES DE NEGOCIO (SQLITE DATABASE)
# =============================================================================
def ejecutar_consultar_menu(categoria: str = None) -> list:
    with Session(engine) as session:
        return get_menu(session, category_name=categoria)

def ejecutar_consultar_horario(dia_semana: str = None) -> list:
    day_query = None
    if dia_semana:
        cleaned = dia_semana.strip().lower()
        day_query = DIAS_TRADUCCION.get(cleaned, cleaned)
    with Session(engine) as session:
        return get_opening_hours(session, day_of_week=day_query)

def ejecutar_solicitar_reserva(
    nombre_cliente: str,
    telefono: str,
    fecha: str,
    hora: str,
    numero_personas: int,
) -> dict:
    try:
        res_date = datetime.strptime(fecha.strip(), "%Y-%m-%d").date()
        hora_clean = hora.strip()
        if len(hora_clean.split(":")) == 2:
            res_time = datetime.strptime(hora_clean, "%H:%M").time()
        else:
            res_time = datetime.strptime(hora_clean, "%H:%M:%S").time()

        with Session(engine) as session:
            reserva = request_table_reservation(
                session=session,
                customer_name=nombre_cliente.strip(),
                phone=telefono.strip(),
                reservation_date=res_date,
                reservation_time=res_time,
                guests=int(numero_personas),
            )
            return {
                "resultado": "EXITO",
                "codigo_reserva": f"RES-{reserva.id:04d}",
                "cliente": reserva.customer_name,
                "telefono": reserva.phone,
                "fecha": reserva.reservation_date.strftime("%Y-%m-%d"),
                "hora": reserva.reservation_time.strftime("%H:%M"),
                "personas": reserva.guests,
                "estado": reserva.status,
                "mensaje": "Reserva registrada y confirmada exitosamente en el sistema.",
            }
    except ValueError as val_err:
        return {
            "resultado": "RECHAZADA",
            "motivo": str(val_err),
            "instruccion_asistente": "Explica cordialmente al cliente por qué no se pudo registrar y ofrécele opciones válidas.",
        }
    except Exception as err:
        return {
            "resultado": "ERROR",
            "motivo": f"Error inesperado al procesar la reserva: {str(err)}",
        }

def ejecutar_tool(nombre_funcion: str, argumentos: dict) -> dict:
    if nombre_funcion == "consultar_menu":
        categoria = argumentos.get("categoria")
        platos = ejecutar_consultar_menu(categoria)
        return {"platos_encontrados": platos, "total": len(platos)}
    elif nombre_funcion == "consultar_horario":
        dia_semana = argumentos.get("dia_semana")
        horarios = ejecutar_consultar_horario(dia_semana)
        return {"horarios_atencion": horarios}
    elif nombre_funcion == "solicitar_reserva_mesa":
        return ejecutar_solicitar_reserva(
            nombre_cliente=argumentos.get("nombre_cliente", ""),
            telefono=argumentos.get("telefono", ""),
            fecha=argumentos.get("fecha", ""),
            hora=argumentos.get("hora", ""),
            numero_personas=argumentos.get("numero_personas", 1),
        )
    else:
        return {"error": f"Herramienta '{nombre_funcion}' desconocida."}

# =============================================================================
# 4. SYSTEM PROMPT PROFESIONAL
# =============================================================================
def generar_system_prompt() -> str:
    hoy = date.today()
    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
    }
    dia_actual_es = dias_es.get(hoy.strftime("%A"), hoy.strftime("%A"))
    fecha_actual_str = f"{dia_actual_es}, {hoy.strftime('%Y-%m-%d')}"

    return f"""Eres "La Huaca AI", el anfitrión virtual por voz del restaurante peruano "La Huaca".
Tu atención es educada, ágil, natural y sumamente concisa.

### CONTEXTO TEMPORAL ACTUAL:
- Fecha de hoy: {fecha_actual_str}.
- Interpreta términos como "hoy", "mañana", "el viernes" en base a esta fecha.

### HERRAMIENTAS DISPONIBLES:
1. `consultar_menu`:
   - Invócala para consultar la carta real: entradas, platos criollos de fondo, postres, bebidas y precios.
   - Parámetro opcional: `categoria` ('Entradas', 'Platos de Fondo', 'Postres', 'Bebidas').
2. `consultar_horario`:
   - Invócala para conocer los días y horarios de apertura y cierre.
   - Parámetro opcional: `dia_semana` (ej. 'lunes', 'sábado', 'domingo').
3. `solicitar_reserva_mesa`:
   - Invócala para registrar una reserva formal cuando tengas los 5 datos: `nombre_cliente`, `telefono`, `fecha` (YYYY-MM-DD), `hora` (HH:MM) y `numero_personas`.

### SOLICITUD DE DATOS DE RESERVA (TODO EN UN SOLO MENSAJE Y SIN FORMATOS TÉCNICOS):
- Si el cliente desea reservar una mesa y faltan datos, NUNCA pidas los datos uno por uno en mensajes separados.
- Solicita de inmediato TODOS los datos que faltan EN UN SOLO MENSAJE amigable, breve y en viñetas:
  "¡Con gusto le ayudo con su reserva! Por favor indíqueme:
  - Su nombre completo
  - Número de teléfono
  - Fecha y hora deseada
  - Cantidad de personas"
- Si el cliente ya adelantó parte de los datos (por ejemplo dijo que es para mañana a las 3), reconoce lo brindado y pide únicamente en una sola lista los que falten.
- PROHIBIDO agregar ejemplos técnicos o formatos entre paréntesis como "(ej: 2026-09-22)", "(formato 24h)", "(ej: 987654321)", etc. Pídelos siempre con lenguaje natural y limpio.
- Solo ejecuta `solicitar_reserva_mesa` cuando dispongas de los 5 datos completos.

### PRESENTACIÓN DE PLATOS (ACLARAR QUE SON "ALGUNOS PLATOS"):
- Cuando pregunten por la carta, entradas o platos de fondo, presenta una selección corta de 3 a 4 opciones.
- OBLIGATORIO: Indica SIEMPRE explícitamente que se trata de ALGUNOS platos destacados (ej: "Aquí le comparto algunos de nuestros platos más destacados de la carta:" o "Estas son algunas de nuestras entradas recomendadas:").
- Cada plato debe presentarse en una sola línea concisa con viñeta:
  - **Nombre del plato** (S/ Precio) — Descripción muy breve en una sola frase.
- Cierra con una frase corta: "Si desea conocer más opciones de nuestra carta, con gusto le muestro más alternativas."

### CONFIDENCIALIDAD INTERNA (CERO JERGA TÉCNICA):
- NUNCA menciones: "base de datos", "SQLite", "servidor", "IDs", "tools", "funciones", "tablas", "JSON" ni "sistema informático".
- Al confirmar una reserva, hazlo cordialmente mostrando los datos acordados en viñetas:
  - **Cliente:** [Nombre]
  - **Fecha y Hora:** [Fecha y Hora]
  - **Comensales:** [Cantidad de personas]
  - **Código:** [Código amigable]
- Si una reserva no se puede realizar, explica con cortesía el motivo como política del restaurante (ej: fuera de horario de atención).

### REGLA DE BREVEDAD ESTRICTA:
- Respuestas MUY CORTAS y directas al grano.
- Máximo 1 o 2 líneas de texto antes de una lista.
- Usa SIEMPRE viñetas con guiones (-) y saltos de línea limpios.
- PROHIBIDO redactar párrafos extensos, introducciones redundantes o rodeos.

### CERO ALUCINACIONES:
- NUNCA inventes platos, precios ni horarios que no figuren en las herramientas.
- NUNCA confirmes una reserva sin el resultado positivo de `solicitar_reserva_mesa`.
"""

# =============================================================================
# 5. INTEGRACIÓN CON GROQ API (WHISPER + LLM FUNCTION CALLING)
# =============================================================================
def obtener_cliente_groq(api_key: str):
    if not api_key:
        return None
    return Groq(api_key=api_key)

def transcribir_audio_groq(client: Groq, audio_bytes: bytes, filename: str = "audio.wav") -> str:
    try:
        transcripcion = client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            language="es",
            response_format="json",
            temperature=0.0,
        )
        return transcripcion.text.strip()
    except Exception as e:
        st.error(f"Error al transcribir audio: {str(e)}")
        return ""

def generar_respuesta_asistente(
    client: Groq,
    user_prompt: str,
    model_name: str = "qwen/qwen3.8-27b",
):
    system_message = {"role": "system", "content": generar_system_prompt()}
    messages_payload = [system_message] + st.session_state.groq_history + [{"role": "user", "content": user_prompt}]

    modelos_candidatos = [model_name]
    for alt in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
        if alt not in modelos_candidatos:
            modelos_candidatos.append(alt)

    with st.chat_message("assistant", avatar="👨‍🍳"):
        final_reply = None
        for modelo_actual in modelos_candidatos:
            try:
                with st.spinner("Pensando..."):
                    response = client.chat.completions.create(
                        model=modelo_actual,
                        messages=messages_payload,
                        tools=TOOLS_SCHEMA,
                        tool_choice="auto",
                        temperature=0.3,
                        max_tokens=350,
                    )

                    response_message = response.choices[0].message
                    tool_calls = response_message.tool_calls

                if tool_calls:
                    messages_payload.append(response_message)
                    with st.status("🔍 Consultando base de datos...", expanded=False) as status_box:
                        for tool_call in tool_calls:
                            func_name = tool_call.function.name
                            func_args = json.loads(tool_call.function.arguments or "{}")

                            status_box.update(label=f"🔧 Consultando `{func_name}` en SQLite...", state="running")
                            resultado_tool = ejecutar_tool(func_name, func_args)

                            with st.expander(f"🔍 Herramienta: **{func_name}**", expanded=False):
                                st.write("**Parámetros:**", func_args)
                                st.write("**Respuesta SQLite:**", resultado_tool)

                            messages_payload.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(resultado_tool, ensure_ascii=False),
                                }
                            )

                        status_box.update(label="✨ Generando respuesta...", state="running")
                        second_response = client.chat.completions.create(
                            model=modelo_actual,
                            messages=messages_payload,
                            temperature=0.3,
                            max_tokens=350,
                        )
                        final_reply = second_response.choices[0].message.content
                        status_box.update(label="✅ Consulta completada", state="complete", expanded=False)
                else:
                    final_reply = response_message.content

                # Consulta completada exitosamente con este modelo
                break

            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "rate_limit" in err_msg.lower():
                    # Si superó la cuota, intentar con el siguiente modelo disponible en Groq
                    continue
                else:
                    final_reply = f"Disculpe, ocurrió un inconveniente con el servidor: {err_msg}"
                    break

        if not final_reply:
            final_reply = "Disculpe, el servicio de IA está temporalmente con alta demanda. Por favor, reintente en unos instantes."

        st.markdown(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    st.session_state.groq_history.append({"role": "user", "content": user_prompt})
    st.session_state.groq_history.append({"role": "assistant", "content": final_reply})

# =============================================================================
# 6. INICIALIZACIÓN DE ESTADO (st.session_state)
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! Bienvenidos a **La Huaca**. Soy tu asistente gastronómico por voz. ¿En qué puedo ayudarte hoy? Puedes consultarme por la carta, los horarios o programar una reserva.",
        }
    ]

if "groq_history" not in st.session_state:
    st.session_state.groq_history = []

# Cargar API Key
groq_api_key = os.getenv("GROQ_API_KEY", "")
if not groq_api_key and "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]

client_groq = obtener_cliente_groq(groq_api_key)
modelo_seleccionado = "qwen/qwen3.8-27b"

# =============================================================================
# 7. ENCABEZADO ERGONÓMICO Y ACCIONES RÁPIDAS
# =============================================================================
st.markdown(
    """
    <div class="chat-header-bar">
        <span class="chat-brand-icon">🍽️</span>
        <div style="flex: 1;">
            <h1 class="hero-title">La Huaca AI</h1>
            <div class="hero-subtitle">Asistente gastronómico por voz · En línea</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Separador superior
st.markdown('<div class="chat-separator chat-separator-top"></div>', unsafe_allow_html=True)

# Sugerencias rápidas en formato 2x2
sugerencia_seleccionada = None

# Fila 1 de sugerencias
r1_c1, r1_c2 = st.columns(2)
with r1_c1:
    if st.button("🍲 Ver Entradas", key="btn_entradas", use_container_width=True):
        sugerencia_seleccionada = "¿Qué entradas tienen en su carta y cuáles son los precios?"
with r1_c2:
    if st.button("🥩 Platos de Fondo", key="btn_criollos", use_container_width=True):
        sugerencia_seleccionada = "¿Cuáles son los platos criollos o de fondo que ofrecen?"

# Fila 2 de sugerencias
r2_c1, r2_c2 = st.columns(2)
with r2_c1:
    if st.button("🕒 Horarios de Atención", key="btn_horarios", use_container_width=True):
        sugerencia_seleccionada = "¿Cuáles son sus horarios de atención?"
with r2_c2:
    if st.button("📅 Reservar Mesa", key="btn_reservar", use_container_width=True):
        sugerencia_seleccionada = "Hola, deseo reservar una mesa en el restaurante, por favor."

# Separador inferior
st.markdown('<div class="chat-separator chat-separator-bottom"></div>', unsafe_allow_html=True)

# Si se presionó una sugerencia rápida, agregar de inmediato el mensaje al chat y activar la IA
if sugerencia_seleccionada:
    if not client_groq:
        st.error("Por favor proporciona tu Groq API Key en el archivo .env")
    else:
        st.session_state.messages.append({"role": "user", "content": sugerencia_seleccionada})
        st.session_state.pendiente_groq = {"prompt": sugerencia_seleccionada}
        st.rerun()

# =============================================================================
# 8. HISTORIAL DE CONVERSACIÓN
# =============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👨‍🍳" if msg["role"] == "assistant" else "👤"):
        if msg["role"] == "user" and msg.get("audio"):
            st.markdown(f"🎙️ **Nota de Voz:** *\"{msg['content']}\"*")
            st.audio(msg["audio"])
        else:
            st.markdown(msg["content"])

# Si hay una respuesta pendiente por generar por la IA
if "pendiente_groq" in st.session_state and st.session_state.pendiente_groq:
    datos_pendientes = st.session_state.pop("pendiente_groq")
    generar_respuesta_asistente(
        client_groq,
        datos_pendientes["prompt"],
        model_name=modelo_seleccionado
    )
    st.rerun()

# =============================================================================
# 9. BARRA DE ENTRADA ESTILO WHATSAPP (CLIP + TEXTO + MICRÓFONO)
# =============================================================================
entrada_usuario = st.chat_input(
    "Escribe un mensaje o usa el micrófono ",
    accept_file=True,
    file_type=["wav", "mp3", "m4a", "ogg"],
    accept_audio=True,
    key="chat_input_voice",
)

if entrada_usuario:
    if not client_groq:
        st.error("Por favor ingresa tu Groq API Key en el archivo .env")
    else:
        audio_grabado = getattr(entrada_usuario, "audio", None) if not isinstance(entrada_usuario, dict) else entrada_usuario.get("audio")
        archivos_adjuntos = getattr(entrada_usuario, "files", None) if not isinstance(entrada_usuario, dict) else entrada_usuario.get("files")
        texto_ingresado = getattr(entrada_usuario, "text", "") if not isinstance(entrada_usuario, dict) else entrada_usuario.get("text", "")
        if isinstance(entrada_usuario, str):
            texto_ingresado = entrada_usuario

        # Grabación directa por micrófono
        if audio_grabado:
            audio_bytes = audio_grabado.getvalue()
            with st.spinner("🎧 Transcribiendo audio con Whisper..."):
                texto_transcrito = transcribir_audio_groq(
                    client_groq, audio_bytes, filename=getattr(audio_grabado, "name", "voz.wav")
                )
            if texto_transcrito:
                st.session_state.messages.append({"role": "user", "content": texto_transcrito, "audio": audio_bytes})
                st.session_state.pendiente_groq = {"prompt": texto_transcrito}
                st.rerun()

        # Archivo subido mediante el clip 📎
        elif archivos_adjuntos and len(archivos_adjuntos) > 0:
            archivo_audio = archivos_adjuntos[0]
            audio_bytes = archivo_audio.getvalue()
            with st.spinner("🎧 Transcribiendo archivo con Whisper..."):
                texto_transcrito = transcribir_audio_groq(
                    client_groq, audio_bytes, filename=archivo_audio.name
                )
            if texto_transcrito:
                st.session_state.messages.append({"role": "user", "content": texto_transcrito, "audio": audio_bytes})
                st.session_state.pendiente_groq = {"prompt": texto_transcrito}
                st.rerun()

        # Mensaje de texto escrito
        elif texto_ingresado and texto_ingresado.strip():
            st.session_state.messages.append({"role": "user", "content": texto_ingresado.strip()})
            st.session_state.pendiente_groq = {"prompt": texto_ingresado.strip()}
            st.rerun()
