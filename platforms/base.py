from abc import ABC, abstractmethod


class BasePlatform(ABC):
    """Abstract base for all platform bots."""

    @abstractmethod
    async def start(self) -> None:
        """Start the bot and begin polling/webhook."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the bot."""
        ...
