import re
import json

def get_list_no_trx_so_from_query(query):
    pattern = r'SO(?:-[A-Z0-9]+)?-\d{4}-\d{8}|DRAFT\d{6}'
    matches = re.findall(pattern, query)
    return matches

def load_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)