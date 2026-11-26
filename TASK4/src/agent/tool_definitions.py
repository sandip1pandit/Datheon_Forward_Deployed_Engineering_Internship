
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Retrieve all available products and their stock quantities.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Retrieve inventory details for a specific product using its product ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID, such as LAP-101."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_lead",
            "description": "Update the status of an existing CRM lead. Requires human approval before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "The CRM lead ID."
                    },
                    "status": {
                        "type": "string",
                        "enum": ["new", "contacted", "qualified", "lost"],
                        "description": "The new lead status."
                    }
                },
                "required": ["lead_id", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a customer support ticket. Requires human approval before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string"
                    },
                    "issue": {
                        "type": "string"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    }
                },
                "required": [
                    "customer_name",
                    "issue",
                    "priority"
                ]
            }
        }
    }
]
