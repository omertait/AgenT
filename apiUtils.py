import json

# Utility functions for schema transformation
def load_schema(file_path: str) -> dict:
    """Load a JSON schema from a file."""
    with open(file_path, "r") as schema_file:
        return json.load(schema_file)


def save_schema(file_path: str, schema: dict):
    """Save a JSON schema to a file."""
    with open(file_path, "w") as schema_file:
        json.dump(schema, schema_file, indent=2)


def recursively_process(schema, callback):
    """Apply a callback function recursively to all nested dictionaries and lists."""
    if isinstance(schema, dict):
        callback(schema)
        for value in schema.values():
            recursively_process(value, callback)
    elif isinstance(schema, list):
        for item in schema:
            recursively_process(item, callback)


def remove_conditionals(schema: dict):
    """Remove `if`, `then`, and `else` conditionals from a schema."""
    schema.pop("if", None)
    schema.pop("then", None)
    schema.pop("else", None)


def add_additional_properties(schema: dict, allow_additional=False):
    """Ensure all object schemas define `additionalProperties`."""
    if schema.get("type") == "object":
        schema.setdefault("additionalProperties", allow_additional)


def align_required_with_properties(schema: dict):
    """Ensure `required` matches the keys in `properties` for object schemas."""
    if schema.get("type") == "object":
        properties = schema.get("properties", {})
        schema["required"] = list(properties.keys())


def transform_schema_to_openai_format(schema: dict, name="workflow") -> dict:
    """
    Transform a JSON schema to OpenAI's response_format structure.
    """
    schema.pop("$schema", None)  # Remove `$schema` if present
    recursively_process(schema, remove_conditionals)
    recursively_process(schema, add_additional_properties)
    recursively_process(schema, align_required_with_properties)

    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "schema": schema,
            "strict": True,
        },
    }