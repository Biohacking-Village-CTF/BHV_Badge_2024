import json

class ConfigManager:
    def __init__(self):
        with open('config.json', 'r') as file:
            self.configData = json.load(file)

    def update_config(self, key, value):
        # I know I should validate here but I won't just to see what happens
        self.configData[key] = value
        self.write_config()
        
    def write_config(self, jsonData=None):
        if( jsonData == None ):
            jsonData = self.configData

        with open('config.json', 'w') as file:
            json.dump(jsonData, file)        