import urllib.request
import json
import typing

#with context manager
#response = urllib.request.urlopen("http://api.quotable.io/random")

def get_quote() -> str :
    with urllib.request.urlopen("http://api.quotable.io/random") as response:
        data = response.read().decode("utf-8")
    data_new = json.loads(data)
    return data_new['content']