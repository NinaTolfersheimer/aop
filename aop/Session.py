"""
@author: Amélie Solveigh Hohe

This file contains the Session class essential to the aop module.
"""

import json
from datetime import datetime, timezone
from os import makedirs
from uuid import uuid4

from current_jd import current_jd


class Session:
    """
    A class representing an astronomical observing session.

    The Session class provides several public methods representing different
    actions and events that occur throughout an astronomical observation.
    It is logged following the Astronomical Observation Protocol Syntax Guide.

    Attributes
    ----------
    filepath : str
        The path where the implementing script wants aop to store its files.
        This could be a part of the implementing script's installation
        directory, for example.
    state : str
        A status flag indicating the current status of the observing session.
        The class methods set this flag to either
            -> "running",

            -> "aborted" or

            -> "ended".
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
        The air pressure at the observing site in Pascal.
    humidity : float or int
        The air humidity at the observing site in percent.

    Methods
    -------
    start(time=-1)
        Starts the observation either on the current UTC (default, time = -1)
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute to
        "running". Writes SEEV (Session Event).
    interrupt(time=-1)
        Interrupts the observation either on the current UTC (default,
        time = -1) or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'interrupted' attribute
        to True. Writes SEEV (Session Event).
    resume(time=-1)
        Resumes the observation either on the current UTC (default, time = -1)
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'interrupted' attribute
        to False. Writes SEEV (Session Event).
    abort(reason, time=-1)
        Aborts the observation either on the current UTC (default, time = -1)
        or a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute
        to "aborted". Writes SEEV (Session Event).
    end(time=-1)
        Ends the observation either on the current UTC (default, time = -1) or
        a custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates 'state' attribute
        to "ended". Writes SEEV (Session Event).
    comment(comment, time=-1)
        Logs an observer's comment on the current UTC (default, time = -1) or a
        custom time provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Writes OBSC (Observer's Comment)
    issue(gravity, message, time=-1)
        Logs an issue on the current UTC (default, time = -1) or a custom time
        provided as ISO 8601 conform string
        (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Supports three gravity levels:
            -> "potential"/"p",

            -> "normal"/"n" and

            -> "major"/"m".

        Writes ISSU (Issue).
    point_to_name(targets, time=-1)
        Logs the pointing to one or more targets visible in the same field of
        view and identified by name string on the current UTC
        (default, time = -1) or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff").
        Writes POIN (Point).
    point_to_coords(ra, dec, time=-1)
        Logs the pointing to one or more targets visible in the same field of
        view and identified by ICRS coordinates on the current UTC
        (default, time = -1) or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff").
        Writes POIN (Point).
    take_frame(n, ftype, ISO, expt, ap, time = -1)
        Logs the capturing of n frames of type ftype and the camera settings
        used on the current UTC (default, time = -1) or a custom time provided
        as ISO 8601 conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). aop
        recognizes five distinct types of frames (ftype):
            -> "science frame"/"science"/"sf"/"s",

            -> "dark frame"/"dark"/"df"/"d",

            -> "bias frame"/"bias"/"bf"/"b",

            -> "flat frame"/"flat"/"ff"/"f" and

            -> "pointing frame"/"pointing"/"pf"/"p".
        Writes FRAM (Take Frame).
    condition_report(description = None, temp = None, pressure = None, humidity = None, time = -1)
        Logs a condition description (description != None) and/or condition
        measurement of temperature (temp != None) and/or air pressure
        (pressure != None) and/or air humidity (humidity != None) on the
        current UTC (default, time = -1) or a custom time provided as ISO 8601
        conform string (time = "YYYY-mm-ddTHH:MM:SS.ffffff"). Updates the
        'conditionDescription' flag if description != None and/or the 'temp'
        flag if temp != None and/or the 'pressure' flag if pressure != None
        and/or the 'humidity' flag if humidity != None. Writes CDES (Condition
        Description) if description != None and/or CMES (Condition Measurement)
        if temp != None or pressure != None or humidity != None. Writes one
        entry per condition argument given (description, temp, pressure,
        humidity).
    """

    def __init__(self, filepath, **kwargs):
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
                    provide further insight on the observation's purpose for
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

        Returns
        -------
        None.

        """

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
        # store every additional argument passed to the class as attribute
        # also add self.state and self.interrupted to this parameter
        # dictionary.
        self.parameters["state"] = self.state
        self.parameters["interrupted"] = self.interrupted

        self.conditionDescription = None
        self.temp = None
        self.pressure = None
        self.humidity = None

    def __repr__(self):
        """
        A Session object is represented by its attributes.


        Returns
        -------
        return_str : str
            A string containing all the instances attributes and their values
            in line format.

        """
        return_str = ""
        for i in self.__dict__:
            if not i == "parameters":
                return_str += f"{i}: {self.__dict__[i]}\n"
        return return_str

    @staticmethod
    def __generate_observation_id(digits=10):
        """
        This pseudo-private method generates a unique observation ID.

        The ID is generated as such:
            YYYY-mm-dd-HH-MM-SS-uuuuuuuuuu
        where:
            YYYY: current UTC year
            mm: current UTC month
            dd: current UTC day
            HH: current UTC hour
            MM: current UTC minute
            SS: current UTC second
            uuuuuuuuuu: a digits-long unique identifier (10 digits per default)

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

    @staticmethod
    def __create_entry_id(time=-1, digits=30):
        """
        Creates a unique identifier for each and every entry in a .aop protocol.
        This identifier is unique even across observations.

        Parameters
        ----------
        time : int or str, optional
            If of type int and equal to -1, the current UTC datetime is used for
            entry ID creation. You can also pass an ISO 8601 conform string to
            time, if the time of the entry is not the current time this method is
            called. The default is -1.
        digits : int, optional
            The number of digits to use for the unique part of the entry ID. The
            default is 30.

        Raises
        ------
        TypeError
            If time is != -1, but also not a string.

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

                - u      represents digits of unique identifier characters.

        """
        if time == -1:
            # if current time is used, return an entryID, consisting of the current
            # UTC and a digits-long unique identifier.
            return f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{uuid4().hex[:digits]}"
        else:
            # if not, check whether time is a string, like
            # datetime.datetime.fromisoformat demands.
            if isinstance(time, str):
                # if so, return an entryId using the time provided
                timestring = datetime.fromisoformat(time)
                return f"{timestring.strftime('%Y%m%d%H%M%S%f')}-{uuid4().hex[:digits]}"
            else:
                # if not, demand users put in a string.
                raise TypeError("Please pass a string as 'time' argument, formatted as ISO 8601 time, in UTC.")

    def start(self, time=-1):
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
            observation to start. The default is -1, in which case the current
            UTC datetime will be used.

        Returns
        -------
        None.

        """
        # initialize session's state to "running"
        self.state = "running"
        self.parameters["state"] = "running"

        # generate a unique observation ID and store it as attribute
        self.obsID = self.__generate_observation_id()
        self.parameters["obsID"] = self.obsID

        # create the directory where the session's data will be stored
        makedirs(self.filepath + "\\" + str(self.obsID), exist_ok=True)

        # create (or overwrite) the main protocol file. Regardless
        # of the .aop file extension, this should be just an ordinary
        # .txt file.
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
            f.write(f"({self.__create_entry_id()}) {current_jd(time):.10f} -> SEEV SESSION {self.obsID} STARTED\n")

        # create or overwrite the parameter and flags log. This is a JSON file.
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as f:
            f.write(json.dumps(self.parameters, indent=4))

    @staticmethod
    def __write_to_aop(self, opcode, argument, time=-1):
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
            default is -1, in which case the current UTC datetime will be used.
            In most cases, however, the calling method will pass its own time
            argument on to __write_to_aop().

        Returns
        -------
        None.

        """
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aop", "at") as f:
            f.write(f"({self.__create_entry_id(time)}) {current_jd(time):.10f} -> {opcode} {argument}\n")

    def interrupt(self, time=-1):
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
            observation to be interrupted at. The default is -1, in which case
            the current UTC datetime will be used.

        Returns
        -------
        None.

        """
        # set interrupted flag to True
        self.interrupted = True
        self.parameters["interrupted"] = True

        # write session event: session interrupted to protocol
        self.__write_to_aop(self, "SEEV", "SESSION INTERRUPTED", time=time)

        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
            param = json.load(log)
        # ... then the flag is updated there ...
        param["interrupted"] = True
        # ... before the file is overwritten with the updated param object.
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
            log.write(json.dumps(param, indent=4))

    def resume(self, time=-1):
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
            observation to be resumed at. The default is -1, in which case the
            current UTC datetime will be used.

        Returns
        -------
        None.

        """
        # set interrupted flag to False again
        self.interrupted = False
        self.parameters["interrupted"] = False

        # write session event: session resumed to protocol
        self.__write_to_aop(self, "SEEV", "SESSION RESUMED", time)

        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
            param = json.load(log)
        # ... then the flag is updated there ...
        param["interrupted"] = False
        # ... before the file is overwritten with the updated param object.
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
            log.write(json.dumps(param, indent=4))

    def abort(self, reason, time=-1):
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
            observation to be aborted at. The default is -1, in which case the
            current UTC datetime will be used.

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

        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
            param = json.load(log)
        # ... then the flag is updated there ...
        param["state"] = "aborted"
        # ... before the file is overwritten with the updated param object.
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
            log.write(json.dumps(param, indent=4))

    def end(self, time=-1):
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
            observation to be ended at. The default is -1, in which case the
            current UTC datetime will be used.

        Returns
        -------
        None.

        """
        # set state flag to "ended"
        self.state = "ended"
        self.parameters["state"] = "ended"

        # write session event: session ended to protocol
        self.__write_to_aop(self, "SEEV", f"SESSION {self.obsID} ENDED", time)

        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
            param = json.load(log)
        # ... then the flag is updated there ...
        param["state"] = "ended"
        # ... before the file is overwritten with the updated param object.
        with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
            log.write(json.dumps(param, indent=4))

    def comment(self, comment, time=-1):
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
            comment to be added at. The default is -1, in which case the
            current UTC datetime will be used.

        Returns
        -------
        None.

        """
        self.__write_to_aop(self, "OBSC", comment, time)

    def issue(self, gravity, message, time=-1):
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
            issue to be reported at. The default is -1, in which case the
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

    def point_to_name(self, targets, time=-1):
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
            pointing to be reported at. The default is -1, in which case the
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

    def point_to_coords(self, ra, dec, time=-1):
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
            pointing to be reported at. The default is -1, in which case the
            current UTC datetime will be used.

        Returns
        -------
        None.

        """

        self.__write_to_aop(self, "POIN", f"Pointing at coordinates: R.A.: {ra} Dec.: {dec}", time)

    def take_frame(self, n, ftype, iso, expt, ap, time=-1):
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
            frame(s) to be reported at. The default is -1, in which case the
            current UTC datetime will be used.

        Raises
        ------
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

    def condition_report(self, description=None, temp=None, pressure=None, humidity=None, time=-1):
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
            condition update to be reported at. The default is -1, in which
            case the current UTC datetime will be used.

        Returns
        -------
        None.

        """
        if description is not None:
            # if a description is provided, set the conditionDescription
            # parameter
            self.conditionDescription = description
            self.parameters["conditionDescription"] = self.conditionDescription

            # write parameter change to log. Since this is JSON, the file
            # is first read to param ...
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
                param = json.load(log)
            # ... then the parameter is updated there ...
            param["conditionDescription"] = self.conditionDescription
            # ... before the file is overwritten with the updated param object.
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))

            # finally, write condition description to protocol
            self.__write_to_aop(self, "CDES", description, time)

        if temp is not None:
            # if a temperature is provided, set the temp parameter
            self.temp = temp
            self.parameters["temp"] = self.temp

            # write parameter change to parameter log. Since this is JSON, the
            # file is first read to param ...
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
                param = json.load(log)
            # ... then the parameter is updated there ...
            param["temp"] = self.temp
            # ... before the file is overwritten with the updated param object.
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))

            # finally, write temperature measurement to protocol
            self.__write_to_aop(self, "CMES", f"Temperature: {self.temp}°C", time)

        if pressure is not None:
            # if a pressure is provided, set the pressure parameter
            self.pressure = pressure
            self.parameters["pressure"] = self.pressure

            # write parameter change to parameter log. Since this is JSON, the
            # file is first read to param ...
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
                param = json.load(log)
            # ... then the parameter is updated there ...
            param["pressure"] = self.pressure
            # ... before the file is overwritten with the updated param object.
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))

            # finally, write pressure measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Pressure: {self.pressure} hPa", time)

        if humidity is not None:
            # if a humidity value  is provided, set the humidity parameter
            self.humidity = humidity
            self.parameters["humidity"] = self.humidity

            # write parameter change to parameter log. Since this is JSON, the
            # file is first read to param ...
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "rb") as log:
                param = json.load(log)
            # ... then the parameter is updated there ...
            param["humidity"] = self.humidity
            # ... before the file is overwritten with the updated param object.
            with open(f"{self.filepath}\\{self.obsID}\\{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))

            # finally, write humidity measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Humidity: {self.humidity}%", time)
