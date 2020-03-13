import json

class ConfigParser:

    def __init__(self, filepath: str):
        self.config = self._load_config_file(filepath)

    def _load_config_file(self, filepath: str):
        with open(filepath) as f:
            return json.load(f)
    
    def get_aws_config(self):
        return self.config['aws']
