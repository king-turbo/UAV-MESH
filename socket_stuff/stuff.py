import json
class stuff:
    def __init__(self, name):
        self.name = name
    def toJSON(self):
        return json.dumps(self.taco, default=lambda o: o.__dict__,
        sort_keys=True, indent=4)
    def taco(self):
        self.taco = {"asdf": 5}
a = stuff("a")
a.taco()
b = a.toJSON()
print(b)