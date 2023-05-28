"""
"""

from astropy.time import Time
import json
from datetime import datetime, timezone
from os import makedirs, path
from uuid import uuid4

from aop.tools import *


def current_jd(time: str="current"):
    """
    Returns the Julian Date for the current UTC or a custom datetime.

    It makes use of astropy's 'Time' object to represent the datetime given as
    a Julian Date.

    Parameters
    ----------
    time : str, optional
        An ISO 8601 conform string of the UTC datetime you want to be converted
        to a Julian Date. The default is "current", in which case the current UTC
        datetime will be used.

    Raises
    ------
    TypeError
        If the 'time' argument is not of type 'str'.
    InvalidTimeStringError
        If the 'time' argument is of type 'str' but not interpretable as representing a time to astropy.time.Time.

    Returns
    -------
    numpy.float64
        The Julian Date corresponding to the datetime provided.

    """

    if time == "current":
        # if the current time is requested, return current Julian Date.
        return Time.now().jd
    else:
        if isinstance(time, str):
            # check whether time is a string, like astropy.time.core.Time expects.
            # if so, return the corresponding Julian Date
            try:
                return Time([time], format="isot", scale="utc").jd[0]
            except ValueError:
                raise InvalidTimeStringError(time)
        else:
            # if not, demand users put in a string.
            raise TypeError("Please pass a string as 'time' argument, formatted as ISO 8601 time, in UTC, or 'current' "
                            "to use current time")


def parse_session(filepath: str, session_id: str):
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

    Raises
    ------
    AolNotFoundError
        If there is no .aol file using the specified filepath and session_id.
    SessionIDDoesntExistOnFilepathError
        If the specified session_id is not in the filepath provided.
    NotADirectoryError
        If the specified filepath does not constitute a directory.
    """
    # provided a filepath and the session_id, we can read the session parameters
    if path.isdir(filepath):
        if path.isdir(f"{filepath}/{session_id}"):
            try:
                with open(f"{filepath}/{session_id}/{session_id}.aol", "rb") as log:
                    param = json.load(log)
            except FileNotFoundError:
                raise AolNotFoundError(session_id)
            finally:
                log.close()
            # unpacking the dictionary we obtained from the .aol, we can construct a
            # new Session object
            session = Session(filepath, **param)
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


def generate_observation_id(digits: int = 10):
    """
    This pseudo-private method generates a unique observation ID.

    The ID is generated as such: YYYY-mm-dd-HH-MM-SS-uuuuuuuuuu,
    where:
        - YYYY: current UTC year
        - mm: current UTC month
        - dd: current UTC day
        - HH: current UTC hour
        - MM: current UTC minute
        - SS: current UTC second
        - uuuuuuuuuu: a 'digits'-long unique identifier (10 digits per default)

    Parameters
    ----------
    digits : int, optional
        The number of digits to be used for the unique identifier part of
        the observation ID. The default is 10.

    Returns
    -------
    str
        The generated observation ID.

    """
    return f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')}-{uuid4().hex[:digits]}"


def create_entry_id(time: str = "current", digits: int = 30) -> str:
    """
    Creates a unique identifier for each and every entry in an .aop protocol.
    This identifier is unique even across observations.

    Parameters
    ----------
    time : str, optional
        If equal to "current", the current UTC datetime is used for
        entry ID creation. You can also pass an ISO 8601 conform string to
        time, if the time of the entry is not the current time this method is
        called. The default is "current".
    digits : int, optional
        The number of digits to use for the unique part of the entry ID. The
        default is 30.

    Raises
    ------
    TypeError
        If time is != "current", but also not a string.
    InvalidTimeStringError
        If a string different from "current" is provided as 'time' argument, but it does not constitute a valid time
        string - it is not ISO 8601 conform.

    Returns
    -------
    str
        The entry ID generated. It follows the syntax YYYYMMDDhhmmssffffff-u,
        where:
            - YYYY   is the specified UTC year,
            - MM     is the specified UTC month,
            - DD     is the specified UTC day,
            - hh     is the specified UTC hour,
            - mm     is the specified UTC month,
            - ss     is the specified UTC second,
            - ffffff is the specified fraction of a UTC second and
            - u      represents 'digits' of unique identifier characters.
    """
    if time == "current":
        # if current time is used, return an entryID, consisting of the current
        # UTC and a digits-long unique identifier.
        return f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{uuid4().hex[:digits]}"
    else:
        # if not, check whether time is a string, like
        # datetime.datetime.fromisoformat demands.
        if isinstance(time, str):
            # if so, return an entryId using the time provided
            try:
                timestring = datetime.fromisoformat(time)
                return f"{timestring.strftime('%Y%m%d%H%M%S%f')}-{uuid4().hex[:digits]}"
            except ValueError:
                raise InvalidTimeStringError(time)
        else:
            # if not, demand users put in a string.
            raise TypeError("Please pass a string as 'time' argument, formatted as ISO 8601 time, in UTC, or 'current' "
                            "to use current time")


class Session:
    """
    A class representing an astronomical observing session.

    The Session class provides several public methods representing different
    actions and events that occur throughout an astronomical observation.
    It is logged following the Astronomical Observation Protocol Standard v1.0.

    Attributes
    ----------
    filepath : str
        The path where the implementing script wants aop to store its files.
        This could be a part of the implementing script's installation
        directory, for example.
    state : str
        A status flag indicating the current status of the observing session.
        The class methods set this flag to either
            - "running",
            - "aborted" or
            - "ended".
        Initialized in __init__() to None, updated in start() to "running".
    interrupted : bool
        A status flag indicating whether the session is currently interrupted.
        Initialized as False.
    obsID : str
        The unique observation ID generated using the __generate_observation_id()
        class method.
    name : str
        Observation title. This is not used internally, as aop relies solely on
        obsID. However, this is logged to observation parameters for
        readability and organizing.
    observer : str
        The name of the person conducting the observation.
    locationDescription : str
        A short description of the location, e.g. "12 Example Road"
    longitude : float
        The location's geographical longitude, expressed in decimal degrees.
        Eastern values are considered positive, Western values are considered
        negative.
    latitude : float
        The location's geographical latitude, expressed in decimal degrees.
        Northern values are considered positive, Southern values are considered
        negative.
    transcription : str
        The person who compiled the protocol.
    listOfGear : list
        A list of each piece of gear used for the observation. List elements
        can be of any type.
    project : str
        The title of the project this observation is a part of.
    target : str
        The object(s) that was/were observed.
    commentary : str
        General commentary referring to the whole session and not covered by
        other functionality of this module. This could provide further insight
        on the observation's purpose for example.
    digitized : bool
        Whether this is the digitization of a handwritten protocol.
    objective : str
        Why this observation was conducted, it's objective.
    digitizer : str
        The name of the person who digitized the protocol, if it has been
        digitized.
    conditionDescription : str
        A short description of the observing conditions.
    temp : float or int
        The temperature at the observing site in degrees Celsius.
    pressure : float or int
        The air pressure at the observing site in Hectopascal.
    humidity : float or int
        The air humidity at the observing site in percent.

    Methods
    -------
    start(time="current")
        Starts the observation either on the current UTC (default, time = "current")
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute to
        "running". Writes SEEV (Session Event).
    interrupt(time="current")
        Interrupts the observation either on the current UTC (default,
        time = "current") or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'interrupted' attribute
        to True. Writes SEEV (Session Event).
    resume(time="current")
        Resumes the observation either on the current UTC (default, time = "current")
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'interrupted' attribute
        to False. Writes SEEV (Session Event).
    abort(reason, time="current")
        Aborts the observation either on the current UTC (default, time = "current")
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute
        to "aborted". Writes SEEV (Session Event).
    end(time="current")
        Ends the observation either on the current UTC (default, time = "current") or
        a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute
        to "ended". Writes SEEV (Session Event).
    comment(comment, time="current")
        Logs an observer's comment on the current UTC (default, time = "current") or a
        custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Writes OBSC (Observer's Comment)
    issue(gravity, message, time="current")
        Logs an issue on the current UTC (default, time = "current") or a custom time
        provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Supports three gravity levels:
            - "potential"/"p",
            - "normal"/"n" and
            - "major"/"m".
        Writes ISSU (Issue).
    point_to_name(targets, time="current")
        Logs the pointing to one or more targets visible in the same field of
        view and identified by name string on the current UTC
        (default, time = "current") or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff").
        Writes POIN (Point).
    point_to_coords(ra, dec, time="current")
        Logs the pointing to one or more targets visible in the same field of
        view and identified by ICRS coordinates on the current UTC
        (default, time = "current") or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff").
        Writes POIN (Point).
    take_frame(n, ftype, ISO, expt, ap, time = "current")
        Logs the capturing of n frames of type ftype and the camera settings
        used on the current UTC (default, time = "current") or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). aop
        recognizes five distinct types of frames (ftype):
            - "science frame"/"science"/"sf"/"s",
            - "dark frame"/"dark"/"df"/"d",
            - "bias frame"/"bias"/"bf"/"b",
            - "flat frame"/"flat"/"ff"/"f" and
            - "pointing frame"/"pointing"/"pf"/"p".
        Writes FRAM (Take Frame).
    condition_report(description = None, temp = None, pressure = None, humidity = None, time = "current")
        Logs a condition description (description != None) and/or condition
        measurement of temperature (temp != None) and/or air pressure
        (pressure != None) and/or air humidity (humidity != None) on the
        current UTC (default, time = "current") or a custom time provided as ISO 8601
        conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates the
        'conditionDescription' flag if description != None and/or the 'temp'
        flag if temp != None and/or the 'pressure' flag if pressure != None
        and/or the 'humidity' flag if humidity != None. Writes CDES (Condition
        Description) if description != None and/or CMES (Condition Measurement)
        if temp != None or pressure != None or humidity != None. Writes one
        entry per condition argument given (description, temp, pressure,
        humidity).
    """

    def __init__(self, filepath: str, **kwargs):
        """
        Parameters
        ----------
        filepath : str
            The path where the implementing script wants aop to store its
            files. This could be a part of the implementing script's
            installation directory, for example.
        **kwargs : dict, optional
            Any keyword arguments. aop recognizes the following keyword
            arguments:
                name : str
                    Observation title. This is not used internally, as aop
                    relies solely on obsID. However, this is logged to
                    observation parameters for readability and organizing.
                observer : str
                    The name of the person conducting the observation.
                locationDescription : str
                    A short description of the location, e.g. "12 Example Road"
                longitude : float
                    The location's geographical longitude, expressed in decimal
                    degrees. Eastern values are considered positive, Western
                    values are considered negative.
                latitude : float
                    The location's geographical latitude, expressed in decimal
                    degrees. Northern values are considered positive, Southern
                    values are considered negative.
                transcription : str
                    The person who compiled the protocol.
                listOfGear : list
                    A list of each piece of gear used for the observation.
                    List elements can be of any type.
                project : str
                    The title of the project this observation is a part of.
                target : str
                    The object that was observed.
                commentary : str
                    General commentary referring to the whole session and not
                    covered by other functionality of this module. This could
                    provide further insight on the observation's purpose, for
                    example.
                digitized : bool
                    Whether this is the digitization of a handwritten protocol.
                objective : str
                    Why this observation was conducted, it's objective.
                digitizer : str
                    The name of the person who digitized the protocol.

        Raises
        ------
        TypeError
            If the longitude argument is not of type float.
        TypeError
            If the latitude argument is not of type float.
        TypeError
            If the listOfGear argument is not of type list.
        TypeError
            If the digitized argument is not of type bool.
        NotADirectoryError
            If the filepath specified does not constitute a directory.

        Returns
        -------
        None.

        """

        if not path.isdir(filepath):
            raise NotADirectoryError("the filepath you provided is not a directory!")

        self.obsID = None
        self.filepath = filepath

        # if the keyword arguments provided are recognized, store their values
        # as attributes
        if "name" in kwargs:
            self.name = kwargs["name"]

        if "observer" in kwargs:
            self.observer = kwargs["observer"]

        if "locationDescription" in kwargs:
            self.locationDescription = kwargs["locationDescription"]

        if "longitude" in kwargs:
            if type(kwargs["longitude"]) == float:
                self.longitude = kwargs["longitude"]
            else:
                raise TypeError("Please provide the 'longitude' argument in decimal degrees (as float)!")

        if "latitude" in kwargs:
            if type(kwargs["latitude"]) == float:
                self.latitude = kwargs["latitude"]
            else:
                raise TypeError("Please provide the 'latitude' argument in decimal degrees (as float)!")

        if "transcription" in kwargs:
            self.transcription = kwargs["transcription"]

        if "listOfGear" in kwargs:
            if type(kwargs["listOfGear"]) == list:
                self.listOfGear = kwargs["listOfGear"]
            else:
                raise TypeError("Please provide a list object for the 'listOfGear' argument!")

        if "project" in kwargs:
            self.project = kwargs["project"]

        if "target" in kwargs:
            self.target = kwargs["target"]

        if "commentary" in kwargs:
            self.commentary = kwargs["commentary"]

        if "digitized" in kwargs:
            if kwargs["digitized"]:
                self.digitized = True
            elif not kwargs["digitized"]:
                self.digitized = False
            else:
                raise TypeError("Please provide a boolean value as 'digitized' argument!")

        if "objective" in kwargs:
            self.objective = kwargs["objective"]

        if "digitizer" in kwargs:
            self.digitizer = kwargs["digitizer"]

        # add more keyword arguments here if necessary

        self.state = None
        # self.state stores the current state of the observation.
        # it is only ever set by the module to either "running",
        # "aborted" or "ended". self.state is initialized when
        # self.start() is called.
        self.interrupted = False
        # whether the session is currently interrupted or not

        self.parameters = kwargs
        # store every additional argument passed to the class as attribute.
        # also add self.state and self.interrupted to this parameter
        # dictionary. This seems inefficient since a Session object now effectively
        # holds every attribute twice. We could perhaps instead exchange 'parameters'
        # for a dictionary of all Session object attributes. We will not change that
        # now, however, since it works for now and could break the whole module if
        # not correctly implemented.
        self.parameters["state"] = self.state
        self.parameters["interrupted"] = self.interrupted

        self.conditionDescription = None
        self.temp = None
        self.pressure = None
        self.humidity = None

        self.parameters["obsID"] = self.obsID
        self.parameters["conditionDescription"] = self.conditionDescription
        self.parameters["temp"] = self.temp
        self.parameters["pressure"] = self.pressure
        self.parameters["humidity"] = self.humidity

    def __repr__(self):
        """
        A Session object is represented by its attributes.

        Returns
        -------
        return_str : str
            A string containing all the instance's attributes and their values
            in line format.

        """
        return_str = ""
        for i in self.__dict__:
            if not i == "parameters":
                return_str += f"{i}: {self.__dict__[i]}\n"
        return return_str

    def start(self, time: str="current"):
        """
        This method is called to start the observing session.

        By not starting the observation when a Session object is created, it is
        possible to prepare the Session object pre-observation as well as
        parsing existing protocols from memory into a new Session object. It
        changes the Session's "state" flag to "running" (attribute and
        parameter), as well as generating an observation ID, setting up a
        directory for the protocol and parameter log to live in, and writing
        the initial files to that directory. It also writes a Session Event
        "SEEV SESSION %obsID% STARTED" to .aop.
        Caution! This method overwrites any existing .aop protocol and .aol log
        files without warning, if there are any in the Session's directory.

        Parameters
        ----------
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            observation to start. The default is "current", in which case the current
            UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol or .aop file.

        Returns
        -------
        None.

        """
        # initialize session's state to "running"
        self.state = "running"
        self.parameters["state"] = "running"

        # generate a unique observation ID and store it as attribute
        self.obsID = generate_observation_id()
        self.parameters["obsID"] = self.obsID

        # create the directory where the session's data will be stored
        makedirs(self.filepath + "\\" + str(self.obsID), exist_ok=True)

        # check whether the protocol files already exist
        if path.exists(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aop"):
            raise AopFileAlreadyExistsError(self.filepath, self.obsID)
        if path.exists(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol"):
            raise AolFileAlreadyExistsError(self.filepath, self.obsID)

        # create the main protocol file. Regardless
        # of the .aop file extension, this should be just an ordinary
        # .txt file.
        try:
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aop", "wt") as f:
                # start each .aop file with the static observation parameters
                for i in self.parameters:

                    # do not print these flags, as they are subject to change
                    if i not in ["state", "interrupted"]:
                        f.write(f"{i}: {self.parameters[i]}\n")

                # add an extra new line to indicate the main protocol beginning.
                f.write("\n")

                # Session Event: The observation started. Check with the AOP
                # Syntax Guide for reference.
                f.write(f"({create_entry_id()}) {current_jd(time):.10f} -> SEEV SESSION "
                        f"{self.obsID} STARTED\n")
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")

        # create or overwrite the parameter and flags log. This is a JSON file.
        try:
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as f:
                f.write(json.dumps(self.parameters, indent=4))
        except PermissionError:
            raise PermissionError("Error when writing to .aol: You do not have the adequate access rights!")

    @staticmethod
    def __write_to_aop(self, opcode: str, argument: str, time: str="current"):
        """
        This pseudo-private method is called to update the .aop protocol file.

        For the syntax, check the Astronomical Observation Protocol Syntax
        Guide.

        Parameters
        ----------
        opcode : str
            The operation code of the event to be written to protocol, as
            described in the AOP Syntax Guide.
        argument : str
            Whatever is to be written to the argument position in the .aop
            protocol entry.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want to use. The
            default is "current", in which case the current UTC datetime will be used.
            In most cases, however, the calling method will pass its own time
            argument on to __write_to_aop().

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for writing to the .aop file.

        Returns
        -------
        None.

        """
        try:
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aop", "at") as f:
                f.write(f"({create_entry_id(time)}) {current_jd(time):.10f} -> {opcode} "
                        f"{argument}\n")
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")

    @staticmethod
    def __write_to_aol(self, parameter: str, assigned_value):
        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        try:
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
                param = json.load(log)
        except PermissionError:
            raise PermissionError("Error when reading from .aol: You do not have the adequate access rights!")
        # ... then the flag is updated there ...
        param[parameter] = assigned_value
        # ... before the file is overwritten with the updated param object.
        try:
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))
        except PermissionError:
            raise PermissionError("Error when writing to .aol: You do not have the adequate access rights!")

    def interrupt(self, time: str="current"):
        """
        This method interrupts the session.

        It sets the Session's 'interrupted' flag to True in the instance
        attribute as well as the parameter attribute. After this, it writes a
        Session Event "SEEV SESSION INTERRUPTED" to the protocol and updates
        the .aol parameter log.

        Parameters
        ----------
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            observation to be interrupted at. The default is "current", in which case
            the current UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol file.

        Returns
        -------
        None.

        """
        # set interrupted flag to True
        self.interrupted = True
        self.parameters["interrupted"] = True

        # write session event: session interrupted to protocol
        self.__write_to_aop(self, "SEEV", "SESSION INTERRUPTED", time=time)

        # update session parameters: interrupted = True
        assigned_value = True
        self.__write_to_aol(self, "interrupted", assigned_value)

    def resume(self, time: str="current"):
        """
        This method resumes the session.

        It sets the Session's 'interrupted' flag to False in the instance
        attribute as well as the parameter attribute. After this, it writes a
        Session Event "SEEV SESSION RESUMED" to the protocol and updates the
        .aol parameter log.

        Parameters
        ----------
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            observation to be resumed at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol file.

        Returns
        -------
        None.

        """
        # set interrupted flag to False again
        self.interrupted = False
        self.parameters["interrupted"] = False

        # write session event: session resumed to protocol
        self.__write_to_aop(self, "SEEV", "SESSION RESUMED", time)

        # update session parameters: interrupted = False
        assigned_value = False
        self.__write_to_aol(self, "interrupted", assigned_value)

    def abort(self, reason: str, time: str="current"):
        """
        This method aborts the session while providing a reason for doing so.

        It sets the Session's 'state' flag to "aborted" in the instance
        attribute as well as the parameter attribute. After this, it writes a
        Session Event "SEEV %reason%: SESSION %obsID% ABORTED" to the protocol
        and updates the .aol parameter log.

        Parameters
        ----------
        reason : str
            The reason why this session had to be aborted.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            observation to be aborted at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol file.

        Returns
        -------
        None.

        """
        # set state flag to "aborted"
        self.state = "aborted"
        self.parameters["state"] = "aborted"

        # write session event: session aborted to protocol, including the
        # reason
        self.__write_to_aop(self, "SEEV", f"{reason}: SESSION {self.obsID} ABORTED", time)

        # update session parameters: state = aborted
        assigned_value = "aborted"
        self.__write_to_aol(self, "state", assigned_value)

    def end(self, time: str="current"):
        """
        This method is called to end the observing session.

        It sets the Session's 'state' flag to "ended" in the instance
        attribute as well as the parameter attribute. After this, it writes a
        Session Event "SEEV SESSION %obsID% ENDED" to the protocol and updates
        the .aol parameter log.

        Parameters
        ----------
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            observation to be ended at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol file.

        Returns
        -------
        None.

        """
        # set state flag to "ended"
        self.state = "ended"
        self.parameters["state"] = "ended"

        # write session event: session ended to protocol
        self.__write_to_aop(self, "SEEV", f"SESSION {self.obsID} ENDED", time)

        # update session parameters: state = ended
        assigned_value = "ended"
        self.__write_to_aol(self, "state", assigned_value)

    def comment(self, comment: str, time: str="current"):
        """
        This method adds an observer's comment to the protocol.

        It writes an Observer's Comment "OBSC %comment%" to the protocol, where
        the AOP argument is whatever string is passed as the 'comment' argument
        to the method verbatim.

        Parameters
        ----------
        comment : str
            Whatever you want your comment to read in the protocol.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            comment to be added at. The default is "current", in which case the
            current UTC datetime will be used.

        Returns
        -------
        None.

        """
        self.__write_to_aop(self, "OBSC", comment, time)

    def issue(self, gravity: str, message: str, time: str="current"):
        """
        This method is called to report an issue to the protocol.

        It evaluates the 'gravity' argument and after that writes the
        corresponding Issue to the protocol:
            - "potential"/"p": "ISSU Potential Issue: %message%"
            - "normal"/"n": "ISSU Normal Issue: %message%"
            - "major"/"m": "ISSU Major Issue: %message%"

        Parameters
        ----------
        gravity : str
            An indicator of the issue's gravity. It has to be one of the
            following strings:
                - "potential"
                - "p"
                - "normal"
                - "n"
                - "major"
                - "m".
        message : str
            A short description of the issue that is printed to the protocol
            verbatim.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            issue to be reported at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        ValueError
            If an improper value is passed in the 'gravity' argument, that is
            anything different from:
                - "potential"
                - "p"
                - "normal"
                - "n"
                - "major"
                - "m".

        Returns
        -------
        None.

        """
        if gravity == "potential" or gravity == "p":
            self.__write_to_aop(self, "ISSU", f"Potential Issue: {message}", time)
        elif gravity == "normal" or gravity == "n":
            self.__write_to_aop(self, "ISSU", f"Normal Issue: {message}", time)
        elif gravity == "major" or gravity == "m":
            self.__write_to_aop(self, "ISSU", f"Major Issue: {message}", time)
        else:
            # the above three cases are the only ones recognized by aop.
            # if users provide any other issue gravity values, aop raises an error.
            raise ValueError("Invalid issue gravity!")

    def point_to_name(self, targets: list, time: str="current"):
        """
        This method indicates the pointing to a target identified by name.

        It starts by evaluating the 'targets' argument provided to the method
        and constructing a comma-separated list of targets, which is then
        written in the AOP argument position in the Pointing "POIN Pointing at
        target(s): %list of targets%" that is being written to the protocol.

        Parameters
        ----------
        targets : list
            A list object that contains whatever objects represent the targets,
            most likely strings, but it could be any other object.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            pointing to be reported at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        TypeError
            If the 'targets' argument is not of type 'list'.

        Returns
        -------
        None.

        """

        # unfortunately now you have to provide a list for targets, but this
        # way, a custom time can be set conveniently
        if not isinstance(targets, list):
            # in order to ensure the possibility of putting in a custom time,
            # the *args syntax can't be used here, so you have to provide a
            # list, ...
            raise TypeError("Please provide the 'targets' argument as a list, even if it only has one item.")
        tar_str = ""
        # ... which is then iterated through by the function ...
        for i in range(len(targets)):
            # ... that finally constructs a comma-separated string
            # from the list ...
            if not i == 0:
                tar_str += ", "
            tar_str += targets[i]
        # ... and writes that string to the protocol.
        self.__write_to_aop(self, "POIN", f"Pointing at target(s): {tar_str}", time)

    def point_to_coords(self, ra: float, dec: float, time: str="current"):
        """
        This method indicates the pointing to ICRS coordinates.

        It takes a 'ra' argument for right ascension and a 'dec' argument for
        declination. After that, a Pointing "Pointing at coordinates: R.A.:
        %ra% Dec.: %dec%" is written to the protocol. There is intentionally
        no unit reference provided. Provide decimal degrees or hours to be
        safe, or put in a string specifying your units. Whatever you put in
        will be printed in the .aop, as long as it is representable as a
        string.

        Parameters
        ----------
        ra : any type representable as a string
            Right ascension in the ICRS coordinate framework.
        dec : any type representable as a string
            Declination in the ICRS coordinate framework.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            pointing to be reported at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        TypeError
            If 'ra' or 'dec' is not of type 'float'.
        ValueError
            If 'ra' is not 0.0h <= 'ra' < 24.0h.
        ValueError
            If 'dec' is not -90.0° <= 'dec' <= 90.0°.

        Returns
        -------
        None.

        """

        # exclude invalid coord values
        if not type(ra) == float:
            raise TypeError(f"Please put in coordinates as 'float' object! R.A. value of {str(ra)} is not 'float'.")
        if not type(dec) == float:
            raise TypeError(f"Please put in coordinates as 'float' object! Dec. value of {str(dec)} is not 'float'.")
        if ra < 0.0:
            raise ValueError(f"R.A. value of {str(ra)} is out of range! Must be >= 0.0h.")
        elif ra >= 24.0:
            raise ValueError(f"R.A. value of {str(ra)} is out of range! Must be < 24.0h. aop expects an R.A. value in "
                             f"hours, so if your coordinates are in degrees, please convert to hours beforehand (divide"
                             f" by 15).")
        if dec < -90.0:
            raise ValueError(f"Dec. value of {str(dec)} is out of range! Must be >= -90.0°.")
        elif dec > 90.0:
            raise ValueError(f"Dec. value of {str(dec)} is out of range! Must be <= 90.0°.")

        # if the values are value, we can write them to the protocol
        self.__write_to_aop(self, "POIN", f"Pointing at coordinates: R.A.: {ra} Dec.: {dec}", time)

    def take_frame(self, n: int, ftype: str, iso: int, expt: float, ap: float, time: str="current"):
        """
        This method reports the taking of one or more frame(s) of the same target and the camera settings used.

        It evaluates the type of frame provided in the 'ftype' argument to
        arrive at a string to be written to the protocol as frame type:
            - "science frame"/"science"/"sf"/"s": "science"
            - "dark frame"/"dark"/"df"/"d": "dark"
            - "flat frame"/"flat"/"ff"/"f": "flat"
            - "bias frame"/"bias"/"bf"/"b": "bias"
            - "pointing frame"/"pointing"/"pf"/"p": "pointing"
        Finally, the method writes a Frame "FRAM %n% %frame type% frame(s)
        taken with settings: Exp.t.: %expt%s, Ap.: f/%ap%, ISO: %ISO%" to the
        protocol.

        Parameters
        ----------
        n : int
            Number of frames of the specified frame type and settings that were
            taken of the same target.
        ftype : str
            Type of frame, ftype must not be anything other than:
                - "science frame"
                - "science"
                - "sf"
                - "s"
                - "dark frame"
                - "dark"
                - "df"
                - "d"
                - "flat frame"
                - "flat"
                - "ff"
                - "f"
                - "bias frame"
                - "bias"
                - "bf"
                - "b"
                - "pointing frame"
                - "pointing"
                - "pf"
                - "p".
        iso : int
            ISO setting that was used for the frame(s).
        expt : float
            Exposure time that was used for the frame(s), given in seconds.
        ap : float
            The denominator of the aperture setting that was used for the
            frame(s). For example, if f/5.6 was used, provide ap=5.6 to the
            method.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            frame(s) to be reported at. The default is "current", in which case the
            current UTC datetime will be used.

        Raises
        ------
        TypeError
            If one of the parameters is not of the required type:
                - n: int
                - ftype: str
                - expt: float
                - ap: float
                - iso: int
        ValueError
            If an improper value is passed in the 'ftype' argument, that is
            anything other than:
                - "science frame"
                - "science"
                - "sf"
                - "s"
                - "dark frame"
                - "dark"
                - "df"
                - "d"
                - "flat frame"
                - "flat"
                - "ff"
                - "f"
                - "bias frame"
                - "bias"
                - "bf"
                - "b"
                - "pointing frame"
                - "pointing"
                - "pf"
                - "p".

        Returns
        -------
        None.

        """

        # type check
        if not type(n) == int:
            raise TypeError("Please provide an integer as frame number ('n' argument)!")
        if not type(ftype) == str:
            raise TypeError("Please provide a string as frame type ('ftype' argument)!")
        if not type(expt) == float:
            raise TypeError("Please provide a float as exposure time ('expt' argument)!")
        if not type(ap) == float:
            raise TypeError("Please provide a float as aperture ('ap' argument)!")
        if not type(iso) == int:
            raise TypeError("Please provide an integer as ISO value ('iso' argument)!")

        # decode or pass ftype - or raise ValueError if invalid key
        if ftype == "science" or ftype == "science frame" or ftype == "s" or ftype == "sc":
            typestr = "science"
        elif ftype == "dark" or ftype == "dark frame" or ftype == "d" or ftype == "df":
            typestr = "dark"
        elif ftype == "flat" or ftype == "flat frame" or ftype == "f" or ftype == "ff":
            typestr = "flat"
        elif ftype == "bias" or ftype == "bias frame" or ftype == "b" or ftype == "bf":
            typestr = "bias"
        elif ftype == "pointing" or ftype == "pointing frame" or ftype == "p" or ftype == "pf":
            typestr = "pointing"
        else:
            raise ValueError("Invalid frame type!")

        # after decoding the type of the frame, all the data is written to the
        # protocol
        self.__write_to_aop(self, "FRAM",
                            f"{n} {typestr} frame(s) taken with settings: Exp.t.: {expt}s, Ap.: f/{ap}, ISO: {iso}",
                            time)

    def condition_report(self, description=None, temp=None, pressure=None, humidity=None, time: str="current"):
        """
        This method reports a condition description or measurement.

        Every argument is optional, just pass the values for the arguments you
        want to protocol. Each argument will be processed completely
        separately, so a separate protocol entry will be produced for every
        argument you provide. For each type of condition report, a
        corresponding flag will be set as an instance attribute as well as a
        parameter. This flag update will also be written to the parameter log.
        In case a description is provided, a Condition Description "CDES
        %description%" is written to the protocol, if a temperature, pressure
        or humidity is provided, however, a Condition Measurement is written to
        protocol for each:
            - "CMES Temperature: %temp%°C" and/or
            - "CMES Air Pressure: %pressure% Pa" and/or
            - "CMES Air Humidity: %humidity%%"

        Parameters
        ----------
        description : str, optional
            A short description of every relevant element influencing the
            overall observing description, but do not provide any measurements,
            as these are a Condition Measurement rather than a Condition
            Description. The default is None.
        temp : float, optional
            The measured temperature in °C. The default is None.
        pressure : float, optional
            The measured air pressure in hPa. The default is None.
        humidity : float, optional
            The measured air humidity in %. The default is None.
        time : str, optional
            An ISO 8601 conform string of the UTC datetime you want your
            condition update to be reported at. The default is "current", in which
            case the current UTC datetime will be used.

        Raises
        ------
        PermissionError
            If the user does not have the adequate access rights for reading from or writing to the .aol file.

        Returns
        -------
        None.

        """
        if type(description) == str:
            # if a description is provided, set the conditionDescription
            # parameter
            self.conditionDescription = description
            self.parameters["conditionDescription"] = self.conditionDescription

            # update session parameters: conditionDescription = description
            self.__write_to_aol(self, "conditionDescription", description)

            # finally, write condition description to protocol
            self.__write_to_aop(self, "CDES", description, time)

        if type(temp) == float or type(temp) == int:
            # if a temperature is provided, set the temp parameter
            self.temp = temp
            self.parameters["temp"] = self.temp

            # update session parameters: temp = temp
            self.__write_to_aol(self, "temp", temp)

            # finally, write temperature measurement to protocol
            self.__write_to_aop(self, "CMES", f"Temperature: {self.temp}°C", time)

        if type(pressure) == int or type(pressure) == float:
            # if a pressure is provided, set the pressure parameter
            self.pressure = pressure
            self.parameters["pressure"] = self.pressure

            # update session parameters: pressure = pressure
            self.__write_to_aol(self, "pressure", pressure)

            # finally, write pressure measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Pressure: {self.pressure} hPa", time)

        if type(humidity) == int or type(humidity) == float:
            # if a humidity value  is provided, set the humidity parameter
            self.humidity = humidity
            self.parameters["humidity"] = self.humidity

            # update session parameters: humidity = hunidity
            self.__write_to_aol(self, "humidity", humidity)

            # finally, write humidity measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Humidity: {self.humidity}%", time)
