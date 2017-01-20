
valid_schema = {
    "title": "Product",
    "description": "Some product's description",
    "type": "object",
    "properties": {
        "id": {
            "description": "The unique identifier for a product",
            "type": "integer"
        },
        "name": {
            "description": "Name of the product",
            "type": "string"
        },
        "prices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "value": {
                        "type": "integer",
                    }
                },
                "required": ["name", "value"],
            }
        }
    },
    "required": ["id", "name"]
}

invalid_schema = {
    "type": "invalid-type"
}

valid_docs = [
    {
        "id": 123,
        "name": "name",
        "prices": [
            {
                "name": "price1",
                "value": 100
            },
            {
                "name": "price2",
                "value": 200
            }
        ]
    }
]

invalid_doc_types = [
    {
        "id": '123',        # this value should be an integer, not its string representation
        "name": "name"
    },
    {
        "id": 123,
        "name": ["name"]    # this value should be a string, not a list of strings
    }
]

invalid_doc_required = [
    {
        "name": 123
        # 'id' is missing
    },
    {
        # 'name' is missing
        "id": {}
    }
]
