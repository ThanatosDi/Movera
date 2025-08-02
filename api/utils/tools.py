import functools
import warnings


def deprecated(message):
    """
    一個 decorator，用來標記函式為已棄用。
    """

    def decorator_wrapper(func):
        @functools.wraps(func)
        def function_wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return function_wrapper

    return decorator_wrapper
