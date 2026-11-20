"""Persistence-level errors. Messages never carry statement parameters."""


class StorageError(Exception):
    """Busy timeout, connection, disk or other database failure (rolled back)."""

    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


class IntegrityConflict(StorageError):
    """A unique or foreign-key constraint rejected the write (rolled back)."""

    def __init__(self) -> None:
        super().__init__("IntegrityError")


class SchemaVerificationError(Exception):
    """Required table or unique index missing. Names the object only."""
