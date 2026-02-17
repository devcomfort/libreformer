from .categories import DocumentCategory

__all__ = ["DocumentCategory", "FormatRegistry"]


# Lazy import to avoid circular dependency with schemas.format_info
def __getattr__(name: str):
    if name == "FormatRegistry":
        from .registry import FormatRegistry

        return FormatRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
