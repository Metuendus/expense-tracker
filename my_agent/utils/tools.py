from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Dict, List
from datetime import datetime

CATEGORIES = [
    "groceries", "transport", "entertainment", "utilities", 
    "dining_out", "shopping", "health", "other"
]

@tool
def add_expense(amount: float, description: str, category: str) -> Dict:
    """
    Agrega un nuevo gasto al registro.
    
    Args:
        amount: Cantidad gastada
        description: Descripción del gasto
        category: Categoría del gasto (debe ser una de las categorías válidas)
    """
    if category not in CATEGORIES:
        return {"error": f"Categoría inválida. Debe ser una de: {', '.join(CATEGORIES)}"}
    
    return {
        "amount": amount,
        "description": description,
        "category": category,
        "date": datetime.now().isoformat()
    }
    
@tool
def calculate_totals(expenses: List[Dict]) -> Dict[str, float]:
    """
    Calcula los totales por categoría.
    
    Args:
        expenses: Lista de gastos
    """
    totals = {category: 0.0 for category in CATEGORIES}
    for expense in expenses:
        if expense.get('category'):
            totals[expense['category']] += expense['amount']
    return totals

@tool
def analyze_spending(expenses: List[Dict]) -> Dict:
    """
    Analiza patrones de gasto y proporciona insights.
    
    Args:
        expenses: Lista de gastos a analizar
    """
    total = sum(expense['amount'] for expense in expenses)
    by_category = {}
    for cat in CATEGORIES:
        cat_total = sum(e['amount'] for e in expenses if e.get('category') == cat)
        if cat_total > 0:
            by_category[cat] = cat_total

    return {
        "total_spent": total,
        "breakdown": by_category,
        "biggest_category": max(by_category.items(), key=lambda x: x[1])[0] if by_category else None
    }

tools = [
    TavilySearchResults(max_results=1),
    add_expense,
    calculate_totals,
    analyze_spending
    ]