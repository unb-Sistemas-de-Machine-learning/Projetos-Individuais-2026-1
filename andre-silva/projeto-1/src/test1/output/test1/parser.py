from .tokens import TokenType
from .tokenizer import Tokenizer

class Parser():

    def __init__(self, input_str: str):
        self.tokenizer = Tokenizer(input_str)
        self.current_token = self.tokenizer.get_next_token()

    def check_token(self, expected_type: TokenType):
        if self.current_token.tokenType != expected_type:
            raise ValueError(f"Unexpect token {self.current_token}, expected: {expected_type}")
        self.current_token = self.tokenizer.get_next_token()

    def parse(self):
        self.__expression()
        if self.current_token.tokenType != TokenType.EOF:
            raise ValueError(f"Error while parsing string {self.tokenizer.input_str}")

    def __expression(self):
        self.__term()
        if self.current_token.tokenType == TokenType.OR:
            self.check_token(TokenType.OR)
            self.__term()

    def __term(self):
        self.__factor()
        if self.current_token.tokenType == TokenType.AND:
            self.check_token(TokenType.AND)
            self.__factor()

    def __factor(self):
        if self.current_token.tokenType == TokenType.IDENTIFIER:
            self.check_token(TokenType.IDENTIFIER)
        else:
            self.check_token(TokenType.L_PARENTHESIS)
            self.__expression()
            self.check_token(TokenType.R_PARENTHESIS)
