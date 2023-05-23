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
