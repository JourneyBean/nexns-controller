class ParseError(Exception):
    
    def __init__(self, expression: str, reason: str) -> None:
        self.message = f"Error parsing record expression: at {expression}, {reason}."
        super().__init__(self.message)

    def __repr__(self) -> str:
        return self.message
