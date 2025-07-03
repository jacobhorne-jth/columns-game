class GameError(Exception):
    """Base class for game-related exceptions."""
    pass

class InvalidMoveError(GameError):
    """Raised when a move is invalid."""
    pass

class GameOverError(GameError):
    """Raised when an action is attempted after the game is over."""
    pass

class InvalidParametersError(GameError):
    """Raised when invalid parameters are provided."""
    pass
