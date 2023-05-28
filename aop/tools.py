class AolFileAlreadyExistsError(Exception):
    """
    An error raised upon trying to initialize an .aol file that already exists.
    """

    def __init__(self, filepath, session_id):
        """
        Initialization of an AolFileAlreadyExistsError object

        Parameters
        ----------
        filepath : str
            the filepath causing the trouble
        session_id : str
            the session_id causing the trouble
        """
        self.filepath = filepath
        self.session_id = session_id


class AolNotFoundError(Exception):
    """
    An error raised upon trying to load an .aol file that doesn't exist.
    """

    def __init__(self, session_id):
        """
        Initialization of an AolNotFoundError object

        Parameters
        ----------
        session_id : str
            the session_id causing the trouble
        """
        self.invalid_string = session_id


class AopFileAlreadyExistsError(Exception):
    """
    An error raised upon trying to initialize an .aop file that already exists.
    """

    def __init__(self, filepath, session_id):
        """
        Initialization of an AopFileAlreadyExistsError object

        Parameters
        ----------
        filepath : str
            the filepath causing the trouble
        session_id : str
            the session_id causing the trouble
        """
        self.filepath = filepath
        self.session_id = session_id


class InvalidTimeStringError(Exception):
    """
    An error raised upon providing a string to current_jd's time argument that is not interpretable as a time.
    """

    def __init__(self, invalid_string):
        """
        Initialization of an InvalidTimeStringError object

        Parameters
        ----------
        invalid_string : str
            the string causing the trouble
        """
        self.invalid_string = invalid_string


class SessionIDDoesntExistOnFilepathError(Exception):
    """
    An error raised when a specified session ID could not be found on the provided filepath.
    """

    def __init__(self, invalid_id):
        """
        Initialization of a SessionIDDoesntExistOnFilepathError object

        Parameters
        ----------
        invalid_id : str
            the session_id causing the trouble
        """
        self.invalid_string = invalid_id
