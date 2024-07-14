class DocumentException(Exception):
    def __init__(self, message="Invalid document"):
        self.message = message
        super().__init__(self.message)