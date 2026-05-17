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
