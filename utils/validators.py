def get_json_data(request):
    data = request.get_json(silent=True)
    return data


def require_fields(data, fields):
    if not data:
        return False
    return all(field in data and data[field] not in (None, "") for field in fields)


def validate_enum(value, allowed_values):
    return value in allowed_values
