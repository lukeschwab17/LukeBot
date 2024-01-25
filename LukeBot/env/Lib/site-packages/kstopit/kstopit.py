# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, Any

# Pip
import stopit
from stopit.utils import BaseTimeout

# Local
from .timeout_type import TimeoutType

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ Public methods ------------------------------------------------------------ #

def timeoutable(
    timeout_type: TimeoutType,
    name: Optional[str] = None,
    function_name: Optional[str] = None,
    timeout_param: Optional[str] = None
) -> Union[stopit.TimeoutException, Any]:
    """Run a function with signal based timeout

    Args:
        type TimeoutType: Can be either Signal or Threading
        name (Optional[str], optional): Will be used for raised Exception message. Defaults to None.
        function_name (Optional[str], optional): Will be used for raised Exception message in the following format "Function 'function_name'", if 'name' is not provided. Defaults to None.
        timeout_param (Optional[str], optional): The timeout param name to check in the kwargs of the passed function. Defaults to None(timeout).

    Returns:
        Union[stopit.TimeoutException, Any]: [description]
    """

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return __run_with_timeout(
                function,
                stopit.SignalTimeout if timeout_type == TimeoutType.Signal else stopit.ThreadingTimeout,
                name,
                function_name,
                timeout_param,
                *args,
                **kwargs
            )

        return wrapper
    return real_decorator

def signal_timeoutable(
    name: Optional[str] = None,
    function_name: Optional[str] = None,
    timeout_param: Optional[str] = None
) -> Union[stopit.TimeoutException, Any]:
    """Run a function with signal based timeout

    Args:
        name (Optional[str], optional): Will be used for raised Exception message. Defaults to None.
        function_name (Optional[str], optional): Will be used for raised Exception message in the following format "Function 'function_name'", if 'name' is not provided. Defaults to None.
        timeout_param (Optional[str], optional): The timeout param name to check in the kwargs of the passed function. Defaults to None(timeout).

    Returns:
        Union[stopit.TimeoutException, Any]: [description]
    """

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return __run_with_timeout(
                function,
                stopit.SignalTimeout,
                name,
                function_name,
                timeout_param,
                *args,
                **kwargs
            )

        return wrapper
    return real_decorator

def threading_timeoutable(
    name: Optional[str] = None,
    function_name: Optional[str] = None,
    timeout_param: Optional[str] = None
) -> Union[stopit.TimeoutException, Any]:
    """Run a function with threading based timeout

    Args:
        name (Optional[str], optional): Will be used for raised Exception message. Defaults to None.
        function_name (Optional[str], optional): Will be used for raised Exception message in the following format "Function 'function_name'", if 'name' is not provided. Defaults to None.
        timeout_param (Optional[str], optional): The timeout param name to check in the kwargs of the passed function. Defaults to None(timeout).

    Returns:
        Union[stopit.TimeoutException, Any]: [description]
    """

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return __run_with_timeout(
                function,
                stopit.ThreadingTimeout,
                name,
                function_name,
                timeout_param,
                *args,
                **kwargs
            )

        return wrapper
    return real_decorator


# ----------------------------------------------------------- Private methods ------------------------------------------------------------ #

def __run_with_timeout(
    function,
    timeout_class: BaseTimeout, # needs class not object
    name: Optional[str] = None,
    function_name: Optional[str] = None,
    timeout_param: Optional[str] = None,
    *args,
    **kwargs
) -> Union[stopit.TimeoutException, Any]:
    timeout_param = timeout_param or 'timeout'

    if timeout_param in kwargs:
        timeout = kwargs[timeout_param]
        del kwargs[timeout_param]
    else:
        timeout = None

    if timeout and timeout > 0:
        try:
            with timeout_class(timeout, swallow_exc=False):
                return function(*args, **kwargs)
        except stopit.TimeoutException as e:
            return stopit.TimeoutException(
                '{} did exceed maximum timeout value ({} {})'.format(
                    '\'{}\''.format(name) if name else 'Function \'{}\''.format(function_name or function.__name__),
                    timeout,
                    'second' if timeout == 1 else 'seconds'
                )
            )
    else:
        return function(*args, **kwargs)


# ---------------------------------------------------------------------------------------------------------------------------------------- #