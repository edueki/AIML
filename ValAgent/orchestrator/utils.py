import re
import json

def rpc_response_processor(data):
    match = re.search(r'data:\s*(\{.*\})', data)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        result = data.get("result", {})
        return result
    else:
        return False