from .tokens import TokenType, Token

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
