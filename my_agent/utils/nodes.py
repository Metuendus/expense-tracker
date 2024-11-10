from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    elif model_name == "anthropic":
        model = ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    
    model = model.bind_tools(tools)
    return model

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
system_prompt = """Eres un asistente inteligente de seguimiento de gastos que ayuda a los usuarios a realizar un seguimiento y analizar sus gastos.

Tus capacidades:
1. Agregar nuevos gastos con la herramienta add_expense
2. Calcular totales por categoría con calculate_totals
3. Analizar patrones de gastos con analyse_spending
4. Buscar información financiera con tavily_search si es necesario

Categorías de gastos disponibles: comestibles, transporte, entretenimiento, servicios públicos, salir a cenar, compras, salud, otros

Siempre:
- Extraer información de gastos de los mensajes de los usuarios
- Clasificar los gastos de forma adecuada
- Proporcionar información útil sobre los patrones de gastos
- Formatear los valores monetarios con el símbolo $ y dos decimales
- Ser amable y proactivo al sugerir formas de gestionar mejor los gastos

Al analizar los gastos:
- Buscar patrones de gastos inusuales
- Identificar categorías con gastos elevados
- Sugerir posibles oportunidades de ahorro

Cuando proporciones resúmenes o análisis, incluye siempre la información en formato JSON:

```json
{
    "expenses": [
        {
            "amount": float,
            "description": string,
            "category": string,
            "date": string
        }
    ],
    "current_analysis": {
        "insights": string,
        "biggest_category": string
    }
}
```

Asegúrate de incluir este JSON en tus respuestas cuando:

Se agregue un nuevo gasto
Se solicite un resumen
Se pida un análisis de gastos
"""

def call_model(state, config):
    """Asegurarse que el estado tenga todos los campos necesarios"""
    if "expenses" not in state:
        state["expenses"] = []
    if "categories_total" not in state:
        state["categories_total"] = {}
    if "current_analysis" not in state:
        state["current_analysis"] = {}

    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model_name = config.get("configurable", {}).get("model_name", "anthropic")
    model = _get_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)