from configparser import ConfigParser

class ParsePass:
    """
    Password load/store class
    """
    def __init__(self, secrets_file):
        parser = ConfigParser()
        parser.read(secrets_file)
        self._secrets_file = secrets_file
        
        self.bot_email = parser.get('bot','address')
        self.bot_pass = parser.get('bot','password')