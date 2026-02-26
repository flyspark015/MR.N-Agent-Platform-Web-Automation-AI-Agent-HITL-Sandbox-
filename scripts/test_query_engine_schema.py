from skills.research.query_engine import QUERY_SCHEMA

assert QUERY_SCHEMA.get("type") == "object"
assert "queries" in QUERY_SCHEMA.get("properties", {})
print("OK")
