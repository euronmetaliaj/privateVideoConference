from jsonschema import validate


def validate_create(data):
    try:
        schemas = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "surname": {
                    "type": "string"
                },
                "card_id": {
                    "type": "string",
                    "maxLength": 14,
                    "minimum": 14
                }
            },
            "required": ['name', 'surname', 'card_id']
        }
        validate(data, schema=schemas)
        return {"state": True}
    except Exception as e:
        return {"state": False, "message": e.message}


data = {
    "name": "Euron",
    "surname": "Metaliaj",
    "customer_type": "individual",
    "card_id": "J5468545465465",
    "street": "Lord Bajron",
    "email": "euron.metaliaj@gmail.com",
    "phone": "0683115921",
    "birthday": "31/12/1994",
    "is_company": "True",
    "gender": "male",
}
print validate_create(data)
