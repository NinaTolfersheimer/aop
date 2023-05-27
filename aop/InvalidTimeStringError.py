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
