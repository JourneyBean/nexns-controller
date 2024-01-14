class ParseError(Exception):
    
    def __init__(self, expression: str, reason: str) -> None:
        super().__init__(f"Error parsing record expression: at {expression}, {reason}.")
