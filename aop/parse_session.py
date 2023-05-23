"""
@author: Amélie Solveigh Hohe

This file contains the parse_session function making the parsing of a session possible.
"""

import json
import os.path
import aop.Session
from SessionIDDoesntExistOnFilepathError import SessionIDDoesntExistOnFilepathError
from AolNotFoundError import AolNotFoundError


def parse_session(filepath, session_id):
    """
    This function parses a session from memory to a new Session object.

    Provided with the filepath to the general location where the protocol and
    log files are stored and an observation ID, it reads in the observation
    parameters from the session's parameter log. This information is then used
    to create a new Session object, which is returned by the function. If it
    has no observationID attribute, it is recreated from the function input.

    Parameters
    ----------
    filepath : str
        The path to the file where you expect the session directory to reside.
        This is most likely equivalent to the path passed to the Session class
        to create its files in, which in turn is most likely somewhere in the
        installation directory of the implementing script.
    session_id : str
        The observationID of the session to be parsed.

    Returns
    -------
    session : Session
        The new Session object parsed from the stored observation parameters.
        For all intents and purposes, this object is equivalent to the object
        whose parameters were used to parse, and you can use it to continue your
        observation session or protocol just the same. Just be careful not to
        run the Session.start() method again, as this would overwrite the
        existing protocol instead of continuing it!

    """
    # provided a filepath and the session_id, we can read the session parameters
    if os.path.isdir(filepath):
        if os.path.isdir(f"{filepath}/{session_id}"):
            try:
                with open(f"{filepath}/{session_id}/{session_id}.aol", "rb") as log:
                    param = json.load(log)
            except FileNotFoundError:
                raise AolNotFoundError(session_id)
            finally:
                log.close()
            # unpacking the dictionary we obtained from the .aol, we can construct a
            # new Session object
            session = aop.Session.Session(filepath, **param)
            # if there is no observationID attribute, we (re-)create it from the
            # function input
            if not hasattr(session, "obsID"):
                session.obsID = param["obsID"]
                session.parameters["obsID"] = session.obsID
            return session
        else:
            raise SessionIDDoesntExistOnFilepathError(session_id)
    else:
        raise NotADirectoryError("your 'filepath' argument is not a directory")
