"""
@author: Amélie Solveigh Hohe

About: This module provides the background functionality on which an
Astronomical Observation Protocol Program can be built.

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