from typing import Callable, Any
from abc import ABC, abstractmethod
import bale


# Global context storage for message data
_message_context = {}


def get_message_context(message: bale.Message) -> dict:
    """Get context data for a message."""
    message_id = id(message)
    return _message_context.get(message_id, {})


def set_message_context(message: bale.Message, data: dict) -> None:
    """Set context data for a message."""
    message_id = id(message)
    _message_context[message_id] = data


def clear_message_context(message: bale.Message) -> None:
    """Clear context data for a message."""
    message_id = id(message)
    _message_context.pop(message_id, None)


class Middleware(ABC):
    """Base middleware class for handling requests."""

    @abstractmethod
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        """
        Process the message and call next handler in chain.
        
        Args:
            message: The incoming message
            pool: Database connection pool
            next_handler: Next handler in the middleware chain
            
        Returns:
            Result from the handler chain
        """
        pass


class MiddlewareManager:
    """Manages middleware chain execution."""

    def __init__(self):
        self.middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """Add middleware to the chain."""
        self.middlewares.append(middleware)

    async def execute(self, message: bale.Message, pool, final_handler: Callable) -> Any:
        """Execute middleware chain."""
        
        async def build_chain(index: int):
            """Recursively build middleware chain."""
            if index >= len(self.middlewares):
                return await final_handler(message, pool)
            
            # Get current middleware
            middleware = self.middlewares[index]
            
            # Create next handler
            async def next_handler(msg, p):
                return await build_chain(index + 1)
            
            # Process current middleware
            return await middleware.process(message, pool, next_handler)
        
        try:
            return await build_chain(0)
        finally:
            clear_message_context(message)
