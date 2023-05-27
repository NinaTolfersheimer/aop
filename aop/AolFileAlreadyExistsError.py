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
