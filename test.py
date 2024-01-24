import pathlib
import json

path = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/") + "/"
nickname = str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/") + "/Content/NicknameSave.json"

with open(nickname) as json_file:
    json_data = json.load(json_file)

print(json_data["name"])