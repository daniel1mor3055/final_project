class Transient:
    def __init__(self, indices, type):
        self.indices = indices
        self.type = type

    def __str__(self):
        return f'Transient is in the following indices:\n{self.indices}\nand is of type:\n{self.type}\n'
