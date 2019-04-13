import json

col = json.loads(input("enter json to indent:"))

print(json.dumps(col, indent=4))
