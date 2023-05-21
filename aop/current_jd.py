"""
@author: Amélie Solveigh Hohe

This file contains the current_jd function, returning the current Julian Date as necessary for the aop module.
"""

from astropy.time import Time


def current_jd(time=-1):
    """
    Returns the Julian Date for the current UTC or a custom datetime.

    It makes use of astropy's 'Time' object to represent the datetime given as
    a Julian Date.

    Parameters
    ----------
    time : str, optional
        An ISO 8601 conform string of the UTC datetime you want to be converted
        to a Julian Date. The default is -1, in which case the current UTC
        datetime will be used.

    Raises
    ------
    TypeError
        If the 'time' argument is not of type 'str'.

    Returns
    -------
    numpy.float64
        The Julian Date corresponding to the datetime provided.

    """
    if time == -1:
        # if time argument is set to an invalid value, return current Julian
        # Date.
        return Time.now().jd
    else:
        if isinstance(time, str):
            # check whether time is a string, like astropy.time.core.Time
            # expects.
            # if so, return the corresponding Julian Date
            return Time([time], format="isot", scale="utc").jd[0]
        else:
            # if not, demand users put in a string.
            raise TypeError("Please pass a string as 'time' argument, formatted as ISO 8601 time, in UTC.")
