"""
Testing ways to do class concstruction
"""


class helper_functions:
    """"""
    def __init__(self, text: str = "Hello World"):
        """Constructor for helper_functions"""
        self.text = self.new_text(text=text)

    @staticmethod
    def new_text(text: str = 'Hello World'):
        return text

    def ptext(self):
        print(self.text)