

class ExpectedKeysException(Exception):

    def __init__(self, lacking_keys):
        self.lacking_keys = lacking_keys

        message = 'expected keys not found: '
        for key in lacking_keys:
            message += f'{key}, '
        self.message = message[:-2]
        super().__init__(self.message)
    
    def __str__(self):
        return self.message