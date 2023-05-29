"""
@author: Amélie Solveigh Hohe

This module contains auxiliary classes and functions for the aop package.
"""


class AolFileAlreadyExistsError(Exception):
    """
    An error raised upon trying to initialize an .aol file that already exists.
    """

    def __init__(self, filepath: str, session_id: str) -> None:
        """
        Initialization of an AolFileAlreadyExistsError object

        :param filepath: The filepath used when the trouble happened.
        :type filepath: ``str``
        :param session_id: The session_id used when the trouble happened.
        :type session_id: ``str``
        """

        self.filepath = filepath
        self.session_id = session_id


class AolNotFoundError(Exception):
    """
    An error raised upon trying to load an .aol file that doesn't exist.
    """

    def __init__(self, session_id: str) -> None:
        """
        Initialization of an AolNotFoundError object.

        :param session_id: The session_id used when the trouble happened.
        :type session_id: ``str``
        """

        self.session_id = session_id


class AopFileAlreadyExistsError(Exception):
    """
    An error raised upon trying to initialize an .aop file that already exists.
    """

    def __init__(self, filepath: str, session_id: str) -> None:
        """
        Initialization of an AopFileAlreadyExistsError object.

        :param filepath: The filepath used when the trouble happened.
        :type filepath: ``str``
        :param session_id: The session_id used when the trouble happened.
        :type session_id: ``str``
        """

        self.filepath = filepath
        self.session_id = session_id


class InvalidTimeStringError(Exception):
    """
    An error raised upon providing a string to current_jd's time argument that is not interpretable as a time.
    """

    def __init__(self, invalid_string: str) -> None:
        """
        Initialization of an InvalidTimeStringError object.

        :param invalid_string: The string causing the trouble.
        :type invalid_string: ``str``
        """

        self.invalid_string = invalid_string


class SessionIDDoesntExistOnFilepathError(Exception):
    """
    An error raised when a specified session ID could not be found on the provided filepath.
    """

    def __init__(self, invalid_id: str) -> None:
        """
        Initialization of a SessionIDDoesntExistOnFilepathError object.

        :param invalid_id: The session:id causing the trouble.
        :type invalid_id: ``str``
        """

        self.invalid_id = invalid_id


class SessionStateError(Exception):
    """
    An error raised when the current session parameters don't allow for the requested operation.
    """
    def __init__(self, event: str, state: str) -> None:
        """
        Constructor method of SessionStateError.

        :param event: The operation to be executed.
        :type event: ``str``
        :param state: The state blocking the operation execution. This does not
            need to be equivalent to the Session.state attribute of the Session class,
            so values like 'not interrupted' are totally valid.
        :type state: ``str``
        """

        self.event = event
        self.state = state

    def __str__(self) -> str:
        """
        The default custom error message of SessionStateError

        :return: default custom error message
        :rtype: ``str``
        """

        return f"Not able to {self.event}: session currently {self.state}."


class NotInterruptableError(SessionStateError):
    """
    An error raised when trying to interrupt a session that is not currently 'running'.

    Inherits from SessionStateError, uses "interrupt session" as impossible operation
    and "not running" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of NotInterruptableError.
        """
        super().__init__(event="interrupt session", state="not 'running'")


class NotResumableError(SessionStateError):
    """
    An error raised when trying to resume a session that is not currently 'running'.

    Inherits from SessionStateError, uses "resume session" as impossible operation
    and "not running" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of NotResumableSession.
        """
        super().__init__(event="resume session", state="not 'running'")


class NotAbortableError(SessionStateError):
    """
    An error raised when trying to abort a session that is not currently 'running'.

    Inherits from SessionStateError, uses "abort session" as impossible operation
    and "not running" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of NotAbortableError
        """
        super().__init__(event="abort session", state="not 'running'")


class NotEndableError(SessionStateError):
    """
    An error raised when trying to end a session that is not currently 'running'.

    Inherits from SessionStateError, uses "end session" as impossible operation
    and "not running" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of NotEndableError
        """
        super().__init__(event="end session", state="not 'running'")


class AlreadyInterruptedError(SessionStateError):
    """
    An error raised when trying to interrupt a session that is already 'interrupted'.

    Inherits from SessionStateError, uses "interrupt session" as impossible operation
    and "interrupted" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of AlreadyInterruptedError
        """
        super().__init__(event="interrupt session", state="interrupted")


class NotInterruptedError(SessionStateError):
    """
    An error raised when trying to resume a session that is not currently 'interrupted'.

    Inherits from SessionStateError, uses "resume session" as impossible operation
    and "not interrupted" as problematic session state.
    """
    def __init__(self) -> None:
        """
        Constructor method of NotInterruptedError
        """
        super().__init__(event="resume session", state="not interrupted")
