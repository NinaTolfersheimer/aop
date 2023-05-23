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
