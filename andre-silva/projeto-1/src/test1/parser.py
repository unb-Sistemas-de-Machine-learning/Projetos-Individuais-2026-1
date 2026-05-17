from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    IDENTIFIER = 1
    AND = 2
    OR = 3
    L_PARENTHESIS = 4
    R_PARENTHESIS = 5
    EOF = 6

    
@dataclass
class Token:
    tokenType: TokenType
    value: str

class Tokenizer():
    keywords = {"E": TokenType.AND, "OU": TokenType.OR}
    symbols = {"(": TokenType.L_PARENTHESIS, ")": TokenType.R_PARENTHESIS}
    
    def __init__(self, input_str: str):
        if input_str == None or len(input_str) == 0:
            raise Exception("Trying to tokenize empty string")

        self.input_str = input_str
        self.current_index = 0

    def _isEOF(self) -> bool:
        return self.current_index == len(self.input_str)

    def get_next_token(self) -> Token:
        while not self._isEOF() and self.input_str[self.current_index].isspace():
            self.current_index += 1

        if self.current_index == len(self.input_str):
            return Token(TokenType.EOF, "#")

        atom = self.input_str[self.current_index]
        if atom in self.symbols:
            self.current_index += 1
            return Token(self.symbols[atom], atom)

        if atom.isalpha():
            start_index = self.current_index
            while not self._isEOF() and self.input_str[self.current_index].isalnum():
                self.current_index += 1
            atom = self.input_str[start_index:self.current_index]
            if atom in self.keywords:
                return Token(self.keywords[atom], atom)
            else:
                return Token(TokenType.IDENTIFIER, atom)
        
        raise ValueError(f"Unknown token: {atom}")

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

def main():
    test_string = "( ( FGA0085 ) OU ( FGA0159 ) )"
    parser = Parser(test_string)
    parser.parse()

if __name__ == '__main__':
    main()
