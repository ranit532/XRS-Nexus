from promptflow import tool

@tool
def lineage_lookup(object_name: str):
    # Mock graph query
    graph = {
        "KNA1": ["Customer_Silver", "Sales_Gold_Agg", "PowerBI_Dashboard_Regional_Sales"],
        "VBAK": ["Sales_Silver", "Revenue_Report"]
    }
    return graph.get(object_name, [])
