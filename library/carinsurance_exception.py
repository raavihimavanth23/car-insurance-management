class CarInsuranceException(Exception):
    def __init__(self, message="This field is required!"):
        self.message = message
        super().__init__(self.message)