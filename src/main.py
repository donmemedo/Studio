import json
from typing import Dict, Any, TypedDict
from langgraph.graph import END, StateGraph

# Define state structure
class AgentState(TypedDict):
    input_data: dict
    metrics: dict
    report: dict

# Define node functions
def input_node(state: AgentState) -> dict:
    """Validate and structure input data"""
    required_keys = {"today", "yesterday"}
    for day in required_keys:
        if day not in state["input_data"]:
            raise ValueError(f"Missing {day} data")
        for field in ["revenue", "cost", "customers"]:
            if field not in state["input_data"][day]:
                raise ValueError(f"Missing {field} in {day} data")
    
    return {"input_data": state["input_data"]}

def process_node(state: AgentState) -> dict:
    """Calculate business metrics"""
    data = state["input_data"]
    today = data["today"]
    yesterday = data["yesterday"]
    
    # Calculate profits
    profit_today = today["revenue"] - today["cost"]
    profit_yesterday = yesterday["revenue"] - yesterday["cost"]
    
    # Calculate percentage changes
    revenue_change = ((today["revenue"] - yesterday["revenue"]) 
                     / yesterday["revenue"]) * 100
    cost_change = ((today["cost"] - yesterday["cost"]) 
                 / yesterday["cost"]) * 100
    
    # Calculate CAC and changes
    cac_today = today["cost"] / today["customers"]
    cac_yesterday = yesterday["cost"] / yesterday["customers"]
    cac_change = ((cac_today - cac_yesterday) / cac_yesterday) * 100
    
    return {
        "metrics": {
            "profit_today": profit_today,
            "profit_yesterday": profit_yesterday,
            "revenue_change_pct": revenue_change,
            "cost_change_pct": cost_change,
            "cac_today": cac_today,
            "cac_change_pct": cac_change
        }
    }

def recommend_node(state: AgentState) -> dict:
    """Generate business recommendations"""
    metrics = state["metrics"]
    alerts = []
    recommendations = []
    
    # Profit analysis
    profit_status = "positive" if metrics["profit_today"] >= 0 else "negative"
    if metrics["profit_today"] < 0:
        alerts.append("ALERT: Negative profit detected")
        recommendations.append("Reduce operational costs immediately")
    
    # CAC analysis
    if metrics["cac_change_pct"] > 20:
        alerts.append(f"ALERT: CAC increased by {metrics['cac_change_pct']:.1f}%")
        recommendations.append("Review marketing campaigns for efficiency")
    
    # Growth opportunities
    if metrics["revenue_change_pct"] > 10:
        recommendations.append("Consider increasing advertising budget to capitalize on growth")
    elif metrics["revenue_change_pct"] < -5:
        alerts.append(f"ALERT: Revenue decreased by {-metrics['revenue_change_pct']:.1f}%")
        recommendations.append("Analyze sales channels for improvement opportunities")
    
    return {
        "report": {
            "profit_status": profit_status,
            "alerts": alerts,
            "recommendations": recommendations
        }
    }

# Build LangGraph workflow
def create_workflow():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("input", input_node)
    builder.add_node("process", process_node)
    builder.add_node("recommend", recommend_node)
    
    # Define edges
    builder.set_entry_point("input")
    builder.add_edge("input", "process")
    builder.add_edge("process", "recommend")
    builder.add_edge("recommend", END)
    
    return builder.compile()

# Test function with sample data
def test_agent():
    """Test the agent with sample inputs"""
    test_cases = [
        {
            "name": "profitable_growth",
            "input": {
                "today": {"revenue": 15000, "cost": 8000, "customers": 100},
                "yesterday": {"revenue": 10000, "cost": 7000, "customers": 90}
            },
            "expected_profit": "positive",
            "expected_alerts": [],
            "expected_recommendations": ["Consider increasing advertising budget to capitalize on growth"]
        },
        {
            "name": "cac_alert",
            "input": {
                "today": {"revenue": 12000, "cost": 10000, "customers": 80},
                "yesterday": {"revenue": 11000, "cost": 6000, "customers": 75}
            },
            "expected_profit": "positive",
            "expected_alerts": ["ALERT: CAC increased by 66.7%"],
            "expected_recommendations": ["Review marketing campaigns for efficiency"]
        },
        {
            "name": "negative_profit",
            "input": {
                "today": {"revenue": 5000, "cost": 7000, "customers": 50},
                "yesterday": {"revenue": 6000, "cost": 5000, "customers": 60}
            },
            "expected_profit": "negative",
            "expected_alerts": ["ALERT: Negative profit detected"],
            "expected_recommendations": ["Reduce operational costs immediately"]
        }
    ]
    
    workflow = create_workflow()
    
    for test in test_cases:
        print(f"\nRunning test: {test['name']}")
        result = workflow.invoke({"input_data": test["input"]})
        report = result["report"]
        
        # Assertions
        assert report["profit_status"] == test["expected_profit"]
        assert report["alerts"] == test["expected_alerts"]
        assert report["recommendations"] == test["expected_recommendations"]
        
        # Print formatted output
        print("Test passed!")
        print("Generated Report:")
        print(json.dumps(report, indent=2))
    
    print("\nAll tests passed!")

# Main execution
if __name__ == "__main__":
    # Example usage
    workflow = create_workflow()
    sample_input = {
        "input_data": {
            "today": {"revenue": 12000, "cost": 8000, "customers": 100},
            "yesterday": {"revenue": 10000, "cost": 7000, "customers": 90}
        }
    }
    
    result = workflow.invoke(sample_input)
    print("\nFinal Report:")
    print(json.dumps(result["report"], indent=2))
    
    # Run tests
    print("\nRunning validation tests:")
    test_agent()
