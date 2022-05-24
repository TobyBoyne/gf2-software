class ErrorLog:
    def __init__(self):
        self.errors = {}

    def __call__(self, errortype, errormessage=""):
        print(errormessage)

    def no_errors(self):
        return len(self.errors) == 0