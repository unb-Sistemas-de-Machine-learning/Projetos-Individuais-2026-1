from .parser import Parser

def main():
    test_string = "( ( FGA0085 ) OU ( FGA0159 ) )"
    parser = Parser(test_string)
    parser.parse()

if __name__ == '__main__':
    main()
