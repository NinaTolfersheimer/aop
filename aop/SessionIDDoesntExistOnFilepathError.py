class SessionIDDoesntExistOnFilepathError(Exception):
    """
    An error raised upon providing a string to current_jd's time argument that is not interpretable as a time.
    """

    def __init__(self, invalid_id):
        """
        Initialization of a SessionIDDoesntExistOnFilepathError object

        Parameters
        ----------
        invalid_id : str
            the string causing the trouble
        """
        self.invalid_string = invalid_id
