"""
@author: Amélie Solveigh Hohe

About: This module provides the background functionality for an implementation of
the Astronomical Observation Protocol standard v1.0 (aop). It fully implements the
standard, but is meant to be implemented by a front-end app.

Third-party dependencies are listed in requirements.txt.
"""

import aop.Session
import aop.current_jd
import aop.parse_session
import aop.AopFileAlreadExistsError
import aop.AolFileAlreadyExistsError
import aop.AolNotFoundError
import aop.SessionIDDoesntExistOnFilepathError
import aop.InvalidTimeStringError
