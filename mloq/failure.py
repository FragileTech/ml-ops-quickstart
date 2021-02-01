"""Define Failure - the exception to raise when we break."""


class Failure(Exception):
    """Raised when a project setup critical error happens."""

    def __str__(self) -> str:
        """Delegate __str__ to the underlying cause if it exists."""
        if self.args or not self.__cause__:
            return super().__str__()
        return f"{type(self.__cause__).__name__}: {self.__cause__}"
