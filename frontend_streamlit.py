# frontend_streamlit.py
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from my_agent.agent import graph
import json
import re

def extract_json_from_message(message_content: str) -> dict:
    """Extrae el JSON de la respuesta del agente."""
    try:
        # Buscar contenido entre ``` o ```json
        json_match = re.search(r'```(?:json)?\s*({[^`]*})\s*```', message_content)
        if json_match:
            return json.loads(json_match.group(1))
        return {}
    except:
        return {}

def update_stats_panel(messages):
    """Actualiza el panel de estadísticas basado en el último resumen disponible."""
    # Buscar el último mensaje que contenga JSON
    last_stats = {}
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            stats = extract_json_from_message(msg.content)
            if stats:
                last_stats = stats
                break
    
    if last_stats:
        try:
            # Total gastado
            total = sum(expense['amount'] for expense in last_stats.get('expenses', []))
            st.metric(
                label="Total gastado", 
                value=f"${total:.2f}"
            )
            
            # Totales por categoría
            st.subheader("🏷️ Categorías")
            categories_total = {}
            for expense in last_stats.get('expenses', []):
                cat = expense['category']
                amount = expense['amount']
                categories_total[cat] = categories_total.get(cat, 0) + amount
            
            # Calcular el máximo para normalizar las barras de progreso
            max_amount = max(categories_total.values()) if categories_total else 1
            
            # Mostrar barras de progreso para cada categoría
            for cat, amount in categories_total.items():
                progress = amount / max_amount
                st.progress(progress, text=f"{cat.title()}: ${amount:.2f}")
            
            # Insights
            if 'current_analysis' in last_stats:
                st.subheader("📊 Insights")
                insights = last_stats['current_analysis'].get('insights', '')
                st.write(insights)
                
        except Exception as e:
            st.error(f"Error actualizando estadísticas: {str(e)}")
    else:
        # Mostrar valores por defecto si no hay datos
        st.metric(
            label="Total gastado", 
            value="$0.00"
        )
        
        st.subheader("🏷️ Categorías")
        categories = [
            "groceries", "transport", "entertainment", "utilities",
            "dining_out", "shopping", "health", "other"
        ]
        for cat in categories:
            st.progress(0, text=f"{cat.title()}: $0.00")


# Configuración de la página
st.set_page_config(
    page_title="Expense Tracker Assistant",
    page_icon="💰",
    layout="wide"
)

# Inicializar el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="👋 ¡Hola! Soy tu asistente de gastos. ¿En qué puedo ayudarte hoy?")
    ]

# Diseño de la interfaz
st.title("💰 Expense Tracker Assistant")

# Crear un diseño de tres columnas
left_col, main_col, right_col = st.columns([1, 2, 1])

# Panel izquierdo - Acciones rápidas
with left_col:
    st.subheader("Acciones Rápidas")
    if st.button("🗑️ Limpiar Chat"):
        st.session_state.messages = [
            AIMessage(content="👋 ¡Hola! Soy tu asistente de gastos. ¿En qué puedo ayudarte hoy?")
        ]
        st.rerun()
    
    # Ejemplos de uso
    st.subheader("Ejemplos")
    example_expenses = [
        "Gasté $50 en el supermercado",
        "Me costó $20 el taxi",
        "¿Cuánto he gastado este mes?",
        "Muéstrame mis gastos por categoría"
    ]
    
    for example in example_expenses:
        if st.button(example):
            # Agregar el ejemplo al chat
            st.session_state.messages.append(HumanMessage(content=example))
            st.rerun()

# Panel principal - Chat
with main_col:
    # Mostrar el historial de mensajes
    for msg in st.session_state.messages:
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)
        else:
            with st.chat_message("user"):
                st.write(msg.content)

    # Input del usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        # Invocar al agente
        response = graph.invoke(
            {
                "messages": st.session_state.messages
            },
            config={
                "configurable": {
                    "model_name": "anthropic"  # o "openai" según tu preferencia
                }
            }
        )
        
        # Actualizar mensajes con la respuesta
        st.session_state.messages = response["messages"]
        st.rerun()

# Panel derecho - Estadísticas y Resumen
with right_col:
    st.subheader("📊 Resumen")
    update_stats_panel(st.session_state.messages)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    .stProgress {
        margin-bottom: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)