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
