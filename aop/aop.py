"""
:Author: Amélie Solveigh Hohe
:Contact: nina.tolfersheimer@posteo.de

This module contains the main classes and functions of the aop package.
"""
import numpy
from astropy.time import Time
import json
from datetime import datetime, timezone
from os import makedirs, path
from uuid import uuid4

# from aop.tools import *
from tools import *

# v2.x
import xml.etree.ElementTree as ET


# v2.x END


def current_jd(time: str = "current") -> numpy.float64:
    """
    Returns the Julian Date for the current UTC or a custom datetime.

    It makes use of astropy's ``Time`` class to represent the datetime given as
    a Julian Date.

    :param time: An ISO 8601 conform string of the UTC datetime you want to be converted
        to a Julian Date. If ``time`` is "current", the current UTC
        datetime will be used, defaults to "current".
    :type time: ``str``, optional

    :raises TypeError: If the ``time`` argument is not of type ``str``.
    :raises InvalidTimeStringError: If the ``time`` argument is of type ``str`` but not interpretable as
        representing a time to astropy.time.Time.

    :return: The Julian Date corresponding to the datetime provided.
    :rtype: ``numpy.float64``
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


def generate_observation_id(digits: int = 10) -> str:
    """
    This function generates a unique observation ID.

    The ID is generated as such: YYYY-mm-dd-HH-MM-SS-uuuuuuuuuu,
    where:
        - YYYY: current UTC year
        - mm: current UTC month
        - dd: current UTC day
        - HH: current UTC hour
        - MM: current UTC minute
        - SS: current UTC second
        - uuuuuuuuuu: a ``digits``-long unique identifier (10 digits per default)

    :param digits: The number of digits to be used for the unique identifier part of
        the observation ID, defaults to 10.
    :type digits: ``int``, optional

    :return: The generated observation ID.
    :rtype: ``str``
    """
    return f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')}-{uuid4().hex[:digits]}"


def create_entry_id(time: str = "current", digits: int = 30) -> str:
    """
    Creates a unique identifier for each and every entry in an .aop protocol.
    This identifier is unique even across observations.

    :param time: If equal to "current", the current UTC datetime is used for
        entry ID creation. You can also pass an ISO 8601 conform string to
        time, if the time of the entry is not the current time this method is
        called, defaults to "current".
    :type time: ``str``, optional
    :param digits: The number of characters to use for the unique part of the entry ID, defaults to 30.
    :type digits: ``int``, optional

    :raises TypeError: If time is not a string.
    :raises InvalidTimeStringError: If a string different from "current" is provided as ``time`` argument, but
        it is not ISO 8601 conform and therefore does not constitute a valid time string.

    :return: The entry ID generated. It follows the syntax YYYYMMDDhhmmssffffff-u,
        where:
            * YYYY   is the specified UTC year,
            * MM     is the specified UTC month,
            * DD     is the specified UTC day,
            * hh     is the specified UTC hour,
            * mm     is the specified UTC month,
            * ss     is the specified UTC second,
            * ffffff is the specified fraction of a UTC second and
            * u      represents the specified amount of unique identifier characters.
    :rtype: ``str``
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
    """

    def __init__(self, filepath: str, **kwargs) -> None:
        r"""
        Constructor method for the :class:`Session` class.

        :param filepath: The path where the implementing script wants aop to store its
            files.
        :type filepath: ``str``
        :param \**kwargs: Any keyword arguments. See below.
        :Keyword Arguments:
                * *name* (``str``) --
                    Observation title. This is not used internally, as aop
                    relies solely on obsID. However, this is logged to
                    observation parameters for organizing purposes.
                * *observer* (``str``) --
                    The name of the person conducting the observation.
                * *locationDescription* (``str``) --
                    A short description of the location, e.g. "12 Example Road"
                * *longitude* (``float``) --
                    The location's geographical longitude, expressed in decimal
                    degrees. Eastern values are considered positive, Western
                    values are considered negative.
                * *latitude* (``float``) --
                    The location's geographical latitude, expressed in decimal
                    degrees. Northern values are considered positive, Southern
                    values are considered negative.
                * *transcription* (``str``) --
                    The person who compiled the protocol.
                * *listOfGear* (``list``) --
                    A list of each piece of gear used for the observation.
                    List elements can be of any type.
                * *project* (``str``) --
                    The title of the project this observation is a part of.
                * *target* (``str``) --
                    The object that was observed.
                * *commentary* (``str``) --
                    General commentary referring to the whole session and not
                    covered by other functionality of this module. This could
                    provide further insight on the observation's purpose, for
                    example.
                * *digitized* (``bool``) --
                    Whether this is the digitization of a handwritten protocol.
                * *objective* (``str``) --
                    Why this observation was conducted.
                * *digitizer* (``str``) --
                    The name of the person who digitized the protocol.

        :raises ValueError: If the ``latitude`` argument is not convertible to ``float``.
        :raises ValueError: If the ``longitude`` argument is not convertible to ``float``.
        :raises TypeError: If the ``listOfGear`` argument is not of type ``list``.
        :raises TypeError: If the ``digitized`` argument is not of type ``bool``.
        :raises NotADirectoryError: If the ``filepath`` specified does not constitute a directory.
        """

        # check whether the filepath is actually a directory
        if not path.isdir(filepath):
            raise NotADirectoryError("the filepath you provided is not a directory!")

        # there should only ever be a 'parsing' keyword if one has been set by the parse_session function to indicate
        # that we want to use the parameters from the old session
        if "parsing" not in kwargs:
            self.started = False
            """Whether the Session.start() method has already been called on this instance."""
        else:
            self.started = kwargs["started"]

        if "parsing" not in kwargs:
            self.obsID = None
            """The unique observation ID generated using the :func:`generate_observation_id()`
            function."""
        else:
            self.obsID = kwargs["obsID"]

        self.filepath = filepath
        """The path where the implementing script wants aop to store its files. This could be a part of the implementing 
        script's installation directory, for example."""

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
                self.longitude = float(kwargs["longitude"])

        if "latitude" in kwargs:
            if type(kwargs["latitude"]) == float:
                self.latitude = kwargs["latitude"]
            else:
                self.latitude = float(kwargs["latitude"])

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

        if "parsing" not in kwargs:
            self.state = None
            """A status flag indicating the current status of the observing session.
            The class methods set this flag to either
                * "running",
                * "aborted" or
                * "ended".
            Initialized in ``__init__()`` to None, updated in ``start()`` to "running"."""
        else:
            self.state = kwargs["state"]

        if "parsing" not in kwargs:
            self.interrupted = False
            """A status flag indicating whether the session is currently interrupted.
            Initialized as False."""
        else:
            self.interrupted = kwargs["interrupted"]

        # The following code block is legacy only in case things should break
        # and is therefore commented out.
        # It stores every keyword argument passed to the class in a parameter dictionary and
        # also adds all the other attributes to this dictionary. This is inefficient since
        # a Session object now effectively holds every attribute twice.

        # self.parameters = kwargs
        # self.parameters["state"] = self.state
        # self.parameters["interrupted"] = self.interrupted
        # self.parameters["obsID"] = self.obsID
        # self.parameters["conditionDescription"] = self.conditionDescription
        # self.parameters["temp"] = self.temp
        # self.parameters["pressure"] = self.pressure
        # self.parameters["humidity"] = self.humidity
        # self.parameters["started"] = self.started

        self.conditionDescription = None
        """A short description of the observing conditions."""
        self.temp = None
        """The temperature at the observing site in °C."""
        self.pressure = None
        """The air pressure at the observing site in hPa."""
        self.humidity = None
        """The air humidity at the observing site in %."""

    def __repr__(self) -> str:
        """
        A Session object is represented by its attributes.

        :return: A string containing all the instance's attributes and their values
            in line format.
        :rtype: ``str``
        """
        return_str = ""
        for i in self.__dict__:
            if not i == "parameters":
                return_str += f"{i}: {self.__dict__[i]}\n"
        return return_str

    def start(self, time: str = "current") -> None:
        """
        This method is called to start the observing session.

        By not starting the observation when a Session object is created, it is
        possible to prepare the Session object pre-observation as well as
        parse existing protocols from memory into a new Session object. It
        changes the Session's "state" flag to "running", as well as generating
        an observation ID, setting up a directory for the protocol to live in, and writing
        the initial files to that directory.

        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to start. Can also be "current", in which case the current
            UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises PermissionError: If the user does not have the adequate access rights for reading from or writing to the
            .aop file.
        :raises AopFileAlreadyExistsError: If the .aop file the method tries to create already exists.
        :raises AopFileAlreadyExistsError: If the .aopl file the method tries to create for legacy only already exists.
        :raises AolFileAlreadyExistsError: If the .aol file the method tries to create for legacy only already exists.
        """

        # initialize session's state to "running"
        self.state = "running"
        # self.parameters["state"] = "running"

        self.started = True
        # self.parameters["started"] = True

        # generate a unique observation ID and update the as of now empty attribute.
        self.obsID = generate_observation_id()
        # self.parameters["obsID"] = self.obsID

        # create the directory where the session's data will be stored
        makedirs(self.filepath + "/" + str(self.obsID), exist_ok=True)

        # check whether the protocol file already exists
        if path.exists(f"{self.filepath}/{self.obsID}/{self.obsID}.aop"):
            raise AopFileAlreadyExistsError(self.filepath, self.obsID)

        # v1.x START
        # Despite this being deprecated, the sections writing the plain-text logs are still in the code
        # for legacy reasons and in case anything should break. The only changes that have been made to
        # the v1.x code as of v2.0 is replacing the .aop file extension with .aopl (for legacy) and
        # discontinuing the usage of self.parameters in favour of self.__dict__.

        # check whether the legacy protocol files already exist
        if path.exists(f"{self.filepath}/{self.obsID}/{self.obsID}.aopl"):
            raise AopFileAlreadyExistsError(self.filepath, self.obsID)
        if path.exists(f"{self.filepath}/{self.obsID}/{self.obsID}.aol"):
            raise AolFileAlreadyExistsError(self.filepath, self.obsID)

        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aopl", "wt") as f:
                # start each .aop file with the static observation parameters
                for i in self.__dict__:  # line used to say: 'for i in self.parameters:'

                    # do not print these flags, as they are subject to change
                    if i not in ["state", "interrupted"]:
                        f.write(f"{i}: {self.__dict__[i]}\n")
                        # previous line used to say: 'f.write(f"{i}: {self.parameters[i]}\n")'

                # add an extra new line to indicate the main protocol beginning.
                f.write("\n")

                # Session Event: The observation started. Check with the AOP
                # Syntax Guide for reference.
                f.write(f"({create_entry_id()}) {current_jd(time):.10f} -> SEEV SESSION "
                        f"{self.obsID} STARTED\n")
        except PermissionError:
            raise PermissionError("Error when writing to .aopl: You do not have the adequate access rights!")

        # create or overwrite the parameter and flags log. This is a JSON file.
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aol", "w") as f:
                f.write(json.dumps(self.__dict__, indent=4))
                # previous line used to say: 'f.write(json.dumps(self.parameters, indent=4))'
        except PermissionError:
            raise PermissionError("Error when writing to .aol: You do not have the adequate access rights!")
        # v1.x END

        # v2.x START
        # create the protocol file. Regardless of the .aop file extension,
        # this should be just an ordinary .xml file.

        # this is the root element of the xml file
        session_root = ET.Element("session")

        # this will be where all the session parameters and metadata live
        parameters_subelement = ET.SubElement(session_root, "parameters")

        # populate the parameters sub-element with all the available metadata
        for i in self.__dict__:  # line used to say: 'for i in self.parameters:'
            current_parameter = ET.SubElement(parameters_subelement, i)
            current_parameter.text = str(self.__dict__[i])
            # previous line used to say: 'current_parameter.text = str(self.parameters[i])'

        # log the session starting
        session_starts_subelement = ET.SubElement(session_root, "start")
        # record entry id and julian date as attributes
        session_starts_subelement.set("time", str(current_jd(time)))
        session_starts_subelement.set("id", str(create_entry_id()))

        # convert xml to byte object
        byte_xml = ET.tostring(session_root, encoding="UTF-8")

        try:
            # write byte object to file
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(byte_xml)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    @staticmethod
    def __write_to_aop(self, opcode: str, argument: str, time: str = "current") -> None:
        """
        This pseudo-private method is called to update the .aopl legacy protocol file.

        For the syntax, check with the Astronomical Observation Protocol Syntax
        Guide.
        **CAUTION!** This method should be considered deprecated and should not be used in any new code!

        :param opcode: The operation code of the event to be written to protocol, as
            described in the AOP Syntax Guide.
        :type opcode: ``str``
        :param argument: Whatever is to be written to the argument position in the .aopl
            protocol entry.
        :type argument: ``str``
        :param time: An ISO 8601 conform string of the UTC datetime you want to use. Can also be "current", in which
            case the current UTC datetime will be used.
            In most cases, however, the calling method will pass its own time
            argument on to __write_to_aop(), defaults to "current".
        :type time: ``str``, optional

        :raises PermissionError: If the user does not have the adequate access rights for writing to the .aopl file.
        """

        # try to open the existing
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aopl", "at") as f:
                f.write(f"({create_entry_id(time)}) {current_jd(time):.10f} -> {opcode} "
                        f"{argument}\n")
        except PermissionError:
            raise PermissionError("Error when writing to .aopl: You do not have the adequate access rights!")

    @staticmethod
    def __write_to_aol(self, parameter: str, assigned_value) -> None:
        """
        This pseudo-private method is used to update the .aol legacy parameter log.

        It takes two arguments, the first being the parameter name being updated,
        the second one being the value it is assigned.
        **CAUTION!** This method should be considered deprecated and should not be used in any new code!

        :param parameter: The name of the parameter being updated.
        :type parameter: ``str``
        :param assigned_value: The value the parameter should be assigned. Typically, this
            is a string or boolean.
        :type assigned_value: any

        :raises PermissionError: If the user does not have the adequate access rights for reading from the .aol file.
        :raises PermissionError: If the user does not have the adequate access rights for writing to the .aol file.
        """

        # write flag change to parameter log. Since this is JSON, the file
        # is first read to param ...
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aol", "rb") as log:
                param = json.load(log)
        except PermissionError:
            raise PermissionError("Error when reading from .aol: You do not have the adequate access rights!")
        # ... then the flag is updated there ...
        param[parameter] = assigned_value
        # ... before the file is overwritten with the updated param object.
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aol", "w") as log:
                log.write(json.dumps(param, indent=4))
        except PermissionError:
            raise PermissionError("Error when writing to .aol: You do not have the adequate access rights!")

    def interrupt(self, time: str = "current") -> None:
        """
        This method interrupts the session.

        It sets the Session's ``interrupted`` flag to True and logs that change.

        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to be interrupted at. Can also be "current", in which case
            the current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises NotInterruptableError: If the session is not currently "running".
        :raises AlreadyInterruptedError: If the session is already interrupted.
        """

        # make sure interrupting makes sense
        if not self.started:
            raise SessionNotStartedError("interrupt session")
        if not self.state == "running":
            raise NotInterruptableError
        if self.interrupted:
            raise AlreadyInterruptedError

        # set interrupted flag to True
        self.interrupted = True
        # self.parameters["interrupted"] = True

        # v1.x START
        # write session event: session interrupted to protocol
        self.__write_to_aop(self, "SEEV", "SESSION INTERRUPTED", time=time)

        # update session parameters: interrupted = True
        assigned_value = True
        self.__write_to_aol(self, "interrupted", assigned_value)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "interrupt" sub-element of root
        interrupt_element = ET.SubElement(session_root, "interrupt")

        # add time and entry ID as items of the interrupt tag
        interrupt_element.set("time", str(current_jd(time)))
        interrupt_element.set("id", str(create_entry_id()))

        # since session parameters have changed (interrupted is now True), we need to replace the
        # parameters tag as well

        # firstly remove the old tag...
        for parameter_tag in session_root.findall("parameters"):
            session_root.remove(parameter_tag)

        # ...then re-create it with the updated parameters
        parameters_tag = ET.SubElement(session_root, "parameters")

        # populate the parameters sub-element with all the available metadata
        for i in self.__dict__:
            # the self.parameters attribute is legacy only and should be treated as such when updating the code
            if i != "parameters":
                current_parameter = ET.SubElement(parameters_tag, i)
                current_parameter.text = str(self.__dict__[i])

        # finally, we overwrite the .aop with the updated element tree

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def resume(self, time: str = "current") -> None:
        """
        This method resumes the session.

        It sets the Session's ``interrupted`` flag to False and logs that change.

        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to be resumed at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises NotResumableError: If the session is not currently "running".
        :raises NotInterruptedError: If the session is not interrupted.
        """

        # make sure resuming makes sense
        if not self.started:
            raise SessionNotStartedError("resume session")
        if not self.state == "running":
            raise NotResumableError
        if not self.interrupted:
            raise NotInterruptedError

        # set interrupted flag to False again
        self.interrupted = False
        # self.parameters["interrupted"] = False

        # v1.x START
        # write session event: session resumed to protocol
        self.__write_to_aop(self, "SEEV", "SESSION RESUMED", time)

        # update session parameters: interrupted = False
        assigned_value = False
        self.__write_to_aol(self, "interrupted", assigned_value)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "resume" sub-element of root
        resume_element = ET.SubElement(session_root, "resume")

        # add time and entry ID as items of the resume tag
        resume_element.set("time", str(current_jd(time)))
        resume_element.set("id", str(create_entry_id()))

        # since session parameters have changed (interrupted is now False again), we need to replace the
        # parameters tag as well

        # firstly remove the old tag...
        for parameter_tag in session_root.findall("parameters"):
            session_root.remove(parameter_tag)

        # ...then re-create it with the updated parameters
        parameters_tag = ET.SubElement(session_root, "parameters")

        # populate the parameters sub-element with all the available metadata
        for i in self.__dict__:
            # the self.parameters attribute is legacy only and should be treated as such when updating the code
            if i != "parameters":
                current_parameter = ET.SubElement(parameters_tag, i)
                current_parameter.text = str(self.__dict__[i])

        # finally, we overwrite the .aop with the updated element tree

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def abort(self, reason: str, time: str = "current") -> None:
        """
        This method aborts the session while providing a reason for doing so.

        It sets the Session's ``state`` flag to "aborted" and logs that change.

        :param reason: The reason why this session had to be aborted.
        :type reason: ``str``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to be aborted at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises NotAbortableError: If the session is not currently "running".
        """

        # make sure aborting makes sense
        if not self.started:
            raise SessionNotStartedError("abort session")
        if not self.state == "running":
            raise NotAbortableError

        # set state flag to "aborted"
        self.state = "aborted"
        # self.parameters["state"] = "aborted"

        # v1.x START
        # write session event: session aborted to protocol, including the
        # reason
        self.__write_to_aop(self, "SEEV", f"{reason}: SESSION {self.obsID} ABORTED", time)

        # update session parameters: state = aborted
        assigned_value = "aborted"
        self.__write_to_aol(self, "state", assigned_value)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "abort" sub-element of root
        abort_element = ET.SubElement(session_root, "abort")

        # add time and entry ID as items of the abort tag
        abort_element.set("time", str(current_jd(time)))
        abort_element.set("id", str(create_entry_id()))

        # add the reason for aborting as text of the "abort" tag
        abort_element.text = str(reason)

        # since session parameters have changed (state is now aborted), we need to replace the
        # parameters tag as well

        # firstly remove the old tag...
        for parameter_tag in session_root.findall("parameters"):
            session_root.remove(parameter_tag)

        # ...then re-create it with the updated parameters
        parameters_tag = ET.SubElement(session_root, "parameters")

        # populate the parameters sub-element with all the available metadata
        for i in self.__dict__:
            # the self.parameters attribute is legacy only and should be treated as such when updating the code
            if i != "parameters":
                current_parameter = ET.SubElement(parameters_tag, i)
                current_parameter.text = str(self.__dict__[i])

        # finally, we overwrite the .aop with the updated element tree

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def end(self, time: str = "current") -> None:
        """
        This method is called to end the observing session.

        It sets the Session's ``state`` flag to "ended" and logs that change.

        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to be ended at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises NotEndableError: If the session is not currently "running".
        """

        # make sure ending makes sense
        if not self.started:
            raise SessionNotStartedError("end session")
        if not self.state == "running":
            raise NotEndableError

        # set state flag to "ended"
        self.state = "ended"
        # self.parameters["state"] = "ended"

        # v1.x START
        # write session event: session ended to protocol
        self.__write_to_aop(self, "SEEV", f"SESSION {self.obsID} ENDED", time)

        # update session parameters: state = ended
        assigned_value = "ended"
        self.__write_to_aol(self, "state", assigned_value)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "end" sub-element of root
        end_element = ET.SubElement(session_root, "end")

        # add time and entry ID as items of the end tag
        end_element.set("time", str(current_jd(time)))
        end_element.set("id", str(create_entry_id()))

        # since session parameters have changed (state is now ended), we need to replace the
        # parameters tag as well

        # firstly remove the old tag...
        for parameter_tag in session_root.findall("parameters"):
            session_root.remove(parameter_tag)

        # ...then re-create it with the updated parameters
        parameters_tag = ET.SubElement(session_root, "parameters")

        # populate the parameters sub-element with all the available metadata
        for i in self.__dict__:
            # the self.parameters attribute is legacy only and should be treated as such when updating the code
            if i != "parameters":
                current_parameter = ET.SubElement(parameters_tag, i)
                current_parameter.text = str(self.__dict__[i])

        # finally, we overwrite the .aop with the updated element tree

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def comment(self, comment: str, time: str = "current") -> None:
        """
        This method adds an observer's comment to the protocol.

        :param comment: Whatever you want your comment to read in the protocol.
        :type comment: ``str``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            comment to be added at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        """

        # make sure commenting makes sense
        if not self.started:
            raise SessionNotStartedError("add comment")
        if not self.state == "running":
            raise SessionStateError(event="add comment", state="not 'running'")

        # v1.x START
        self.__write_to_aop(self, "OBSC", comment, time)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "comment" sub-element of root
        comment_element = ET.SubElement(session_root, "comment")

        # add time and entry ID as items of the comment tag
        comment_element.set("time", str(current_jd(time)))
        comment_element.set("id", str(create_entry_id()))

        # add the actual comment as text to the comment tag
        comment_element.text = str(comment)

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def issue(self, severity: str, message: str, time: str = "current") -> None:
        """
        This method is called to report an issue to the protocol.

        There are three severity levels available:
            * potential
            * normal
            * major

        :param severity: An indicator of the issue's severity. It has to be one of the
            following strings:
                * "potential"
                * "p"
                * "normal"
                * "n"
                * "major"
                * "m".
        :type severity: ``str``
        :param message: A short description of the issue that is logged as well.
        :type message: ``str``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            issue to be reported at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        :raises ValueError: If an improper value is passed to the 'severity' argument, that is
            anything different from:
                * "potential"
                * "p"
                * "normal"
                * "n"
                * "major"
                * "m".
        """

        # make sure reporting an issue makes sense
        if not self.started:
            raise SessionNotStartedError("report issue")
        if not self.state == "running":
            raise SessionStateError(event="report issue", state="not 'running'")

        # v1.x START
        if severity == "potential" or severity == "p":
            self.__write_to_aop(self, "ISSU", f"Potential Issue: {message}", time)
        elif severity == "normal" or severity == "n":
            self.__write_to_aop(self, "ISSU", f"Normal Issue: {message}", time)
        elif severity == "major" or severity == "m":
            self.__write_to_aop(self, "ISSU", f"Major Issue: {message}", time)
        else:
            # the above three cases are the only ones recognized by aop.
            # if users provide any other issue severity values, aop raises an error.
            raise ValueError("Invalid issue severity!")
        # v1.x END

        # v2.x START
        # make sure we're reporting a valid issue severity
        if severity in ["potential", "p", "normal", "n", "major", "m"]:
            # parse element tree from .aop
            tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

            # get root tag (session)
            session_root = tree.getroot()

            # create a new "issue" sub-element of root
            issue_element = ET.SubElement(session_root, "issue")

            # add time and entry ID as items of the issue tag
            issue_element.set("time", str(current_jd(time)))
            issue_element.set("id", str(create_entry_id()))

            # add the issue severity and the issue description as sub-tags of the issue tag
            severity_tag = ET.SubElement(issue_element, "severity")
            severity_tag.text = severity

            description_tag = ET.SubElement(issue_element, "description")
            description_tag.text = str(message)

            # converting xml to a byte object...
            session_byte = ET.tostring(session_root, encoding="UTF-8")

            # ...then trying to write the file to memory, if we have permission to do so
            try:
                with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                    f.write(session_byte)
            except PermissionError:
                raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
            # v2.x END
        else:
            raise ValueError("Invalid issue severity!")

    def point_to_name(self, targets: list, time: str = "current") -> None:
        """
        This method indicates the pointing to one or more target(s) identified by name.

        It can handle multiple targets at once, each will be logged in its own sub-tag of the
        'point' tag.

        :param targets: A list object that contains whatever objects represent the targets,
            most likely strings, but it could be any other object.
        :type targets: ``list[any]``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            pointing to be reported at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        :raises TypeError: If the ``targets`` argument is not of type ``list``.
        """

        # make sure pointing to name makes sense
        if not self.started:
            raise SessionNotStartedError("point to name")
        if not self.state == "running":
            raise SessionStateError(event="point to name", state="not 'running'")

        # v1.x START
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
            # ... that finally constructs a comma-separated string from the list ...
            if not i == 0:
                tar_str += ", "
            tar_str += targets[i]
        # ... and writes that string to the protocol.
        self.__write_to_aop(self, "POIN", f"Pointing at target(s): {tar_str}", time)
        # v1.x END

        # v2.x START
        # ensure a list was supplied as 'targets' argument
        if not isinstance(targets, list):
            raise TypeError("Please provide the 'targets' argument as a list, even if it only has one item.")

        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "point" sub-element of root
        point_element = ET.SubElement(session_root, "point")

        # add time and entry ID as items of the point tag
        point_element.set("time", str(current_jd(time)))
        point_element.set("id", str(create_entry_id()))

        # add the contents of the targets list as sub-tags to the point tag
        for i in targets:
            new_target_element = ET.SubElement(point_element, "name")
            new_target_element.text = str(i)

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def point_to_coords(self, ra: float, dec: float, time: str = "current") -> None:
        """
        This method indicates the pointing to ICRS coordinates.

        Unlike the :func:`point_to_name` method, this method can only handle one set
        of coordinates each time, ideally representing the middle of the field of view.
        Provide decimal degrees for declination and decimal hours for right ascension.

        :param ra: Right ascension in the ICRS coordinate framework.
        :type ra: ``float``
        :param dec: Declination in the ICRS coordinate framework.
        :type dec: ``float``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            pointing to be reported at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        :raises TypeError: If 'ra' is not of type 'float'.
        :raises TypeError: If 'dec' is not of type 'float'.
        :raises ValueError: If 'ra' is not 0.0h <= 'ra' < 24.0h.
        :raises ValueError: If 'dec' is not -90.0° <= 'dec' <= 90.0°.
        """

        # make sure pointing to coords makes sense
        if not self.started:
            raise SessionNotStartedError("point to coords")
        if not self.state == "running":
            raise SessionStateError(event="point to coords", state="not 'running'")

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

        # if the values are valid, we can write them to the protocol
        # v1.x START
        self.__write_to_aop(self, "POIN", f"Pointing at coordinates: R.A.: {ra} Dec.: {dec}", time)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "point" sub-element of root
        point_element = ET.SubElement(session_root, "point")

        # add time and entry ID as items of the point tag
        point_element.set("time", str(current_jd(time)))
        point_element.set("id", str(create_entry_id()))

        # add R.A. and Dec. of the target as sub-tags to the point tag respectively
        ra_sub_tag = ET.SubElement(point_element, "ra")
        ra_sub_tag.text = str(ra)

        dec_sub_tag = ET.SubElement(point_element, "dec")
        dec_sub_tag.text = str(dec)

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def take_frame(self, n: int, ftype: str, iso: int, expt: float, ap: float, time: str = "current") -> None:
        """
        This method reports the taking of one or more frame(s) of the same target and the same camera settings used.

        It is centered on using a DSLR/DSLM as detector, since it uses the term ISO and expects
        aperture to be provided as a fraction, like it is common for photographic lenses.
        You can use a dedicated astronomy camera as well however. Interpret 'iso' as Gain and
        calculate the aperture fraction of your optics for the 'ap' argument.
        This method recognizes five distinct frame types:
            * science/light frame (sometimes called 'sub', too)
            * dark frame
            * flat frame
            * bias frame
            * pointing frame

        :param n: Number of frames of the specified frame type and settings that were
            taken of the same target.
        :type n: ``int``
        :param ftype: Type of frame, ftype must not be anything other than:
                * "science frame"
                * "science"
                * "sf"
                * "s"
                * "dark frame"
                * "dark"
                * "df"
                * "d"
                * "flat frame"
                * "flat"
                * "ff"
                * "f"
                * "bias frame"
                * "bias"
                * "bf"
                * "b"
                * "pointing frame"
                * "pointing"
                * "pf"
                * "p".
        :type ftype: ``str``
        :param iso: ISO or Gain setting that was used for the frame(s).
        :type iso: ``int``
        :param ap: The denominator of the aperture setting that was used for the
            frame(s). For example, if f/5.6 was used, provide ap=5.6 to the
            method.
        :type ap: ``float``
        :param expt: Exposure time that was used for the frame(s), given in seconds.
        :type expt: ``float``
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            frame(s) to be reported at. Can also be "current", in which case the
            current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        :raises TypeError: If one of the parameters is not of the required type:
                * n: int
                * ftype: str
                * expt: float
                * ap: float
                * iso: int
        :raises ValueError:
            If an improper value is passed in the 'ftype' argument, that is
            anything other than:
                * "science frame"
                * "science"
                * "sf"
                * "s"
                * "dark frame"
                * "dark"
                * "df"
                * "d"
                * "flat frame"
                * "flat"
                * "ff"
                * "f"
                * "bias frame"
                * "bias"
                * "bf"
                * "b"
                * "pointing frame"
                * "pointing"
                * "pf"
                * "p".
        """

        # make sure frame taking makes sense
        if not self.started:
            raise SessionNotStartedError("take frame")
        if not self.state == "running":
            raise SessionStateError(event="take frame", state="not 'running'")

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
        # v1.x START
        self.__write_to_aop(self, "FRAM",
                            f"{n} {typestr} frame(s) taken with settings: Exp.t.: {expt}s, Ap.: f/{ap}, ISO: {iso}",
                            time)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "frame" sub-element of root
        frame_element = ET.SubElement(session_root, "frame")

        # add time and entry ID as items of the frame tag
        frame_element.set("time", str(current_jd(time)))
        frame_element.set("id", str(create_entry_id()))

        # add the camera settings as sub-tags of the frame tag, respectively
        number_tag = ET.SubElement(frame_element, "number_of_frames")
        number_tag.text = str(n)

        ftype_tag = ET.SubElement(frame_element, "type")
        ftype_tag.text = typestr

        expt_tag = ET.SubElement(frame_element, "exposure")
        expt_tag.text = str(expt)

        iso_tag = ET.SubElement(frame_element, "iso")
        iso_tag.text = str(iso)

        ap_tag = ET.SubElement(frame_element, "aperture")
        ap_tag.text = str(ap)

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END

    def condition_report(self, description: str = None, temp: float = None, pressure: float = None, humidity: float =
        None, time: str = "current") -> None:

        """
        This method reports a condition description or measurement.

        Every argument is optional, just pass the values for the arguments you
        want to log. Each argument will be processed completely
        separately, so a separate log entry will be produced for every
        argument you provide. For each type of condition report, a
        corresponding flag will be set.

        :param description: A short description of every relevant element influencing the
            overall observing description, but do not provide any measurements,
            as these are a Condition Measurement rather than a Condition
            Description, defaults to None.
        :type description: ``str``, optional
        :param temp: The measured temperature in °C, defaults to None.
        :type temp: ``float``, optional
        :param pressure: The measured air pressure in hPa, defaults to None.
        :type pressure: ``float``, optional
        :param humidity: The measured air humidity in %, defaults to None.
        :type humidity: ``float``, optional
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            condition update to be reported at. Can also be "current", in which
            case the current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".

        :return: None
        """

        # make sure reporting conditions makes sense
        if not self.started:
            raise SessionNotStartedError("report observing conditions")
        if not self.state == "running":
            raise SessionStateError(event="report observing conditions", state="not 'running'")

        if type(description) == str:
            # if a description is provided, set the conditionDescription
            # parameter
            self.conditionDescription = description
            # self.parameters["conditionDescription"] = self.conditionDescription

            # v1.x START
            # update session parameters: conditionDescription = description
            self.__write_to_aol(self, "conditionDescription", description)

            # finally, write condition description to protocol
            self.__write_to_aop(self, "CDES", description, time)
            # v1.x END

            # v2.x START
            # parse element tree from .aop
            tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

            # get root tag (session)
            session_root = tree.getroot()

            # create a new "condition_description" sub-element of root
            condition_description_element = ET.SubElement(session_root, "condition_description")

            # add time and entry ID as items of the condition_description tag
            condition_description_element.set("time", str(current_jd(time)))
            condition_description_element.set("id", str(create_entry_id()))

            # add the actual condition description as text of the condition description tag
            condition_description_element.text = str(description)

            # since session parameters have changed (conditionDescription), we need to replace the
            # parameters tag as well

            # firstly remove the old tag...
            for parameter_tag in session_root.findall("parameters"):
                session_root.remove(parameter_tag)

            # ...then re-create it with the updated parameters
            parameters_tag = ET.SubElement(session_root, "parameters")

            # populate the parameters sub-element with all the available metadata
            for i in self.__dict__:
                # the self.parameters attribute is legacy only and should be treated as such when updating the code
                if i != "parameters":
                    current_parameter = ET.SubElement(parameters_tag, i)
                    current_parameter.text = str(self.__dict__[i])

            # finally, we overwrite the .aop with the updated element tree

            # converting xml to a byte object...
            session_byte = ET.tostring(session_root, encoding="UTF-8")

            # ...then trying to write the file to memory, if we have permission to do so
            try:
                with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                    f.write(session_byte)
            except PermissionError:
                raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
            # v2.x END

        if type(temp) == float or type(temp) == int:
            # if a temperature is provided, set the temp parameter
            self.temp = temp
            # self.parameters["temp"] = self.temp

            # v1.x START
            # update session parameters: temp = temp
            self.__write_to_aol(self, "temp", temp)

            # finally, write temperature measurement to protocol
            self.__write_to_aop(self, "CMES", f"Temperature: {self.temp}°C", time)
            # v1.x END

            # v2.x START
            # parse element tree from .aop
            tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

            # get root tag (session)
            session_root = tree.getroot()

            # create a new "temperature" sub-element of root
            temperature_element = ET.SubElement(session_root, "temperature")

            # add time and entry ID as items of the temperature tag
            temperature_element.set("time", str(current_jd(time)))
            temperature_element.set("id", str(create_entry_id()))

            # add the actual temperature as text of the temperature tag
            temperature_element.text = str(temp)

            # since session parameters have changed (temp), we need to replace the
            # parameters tag as well

            # firstly remove the old tag...
            for parameter_tag in session_root.findall("parameters"):
                session_root.remove(parameter_tag)

            # ...then re-create it with the updated parameters
            parameters_tag = ET.SubElement(session_root, "parameters")

            # populate the parameters sub-element with all the available metadata
            for i in self.__dict__:
                # the self.parameters attribute is legacy only and should be treated as such when updating the code
                if i != "parameters":
                    current_parameter = ET.SubElement(parameters_tag, i)
                    current_parameter.text = str(self.__dict__[i])

            # finally, we overwrite the .aop with the updated element tree

            # converting xml to a byte object...
            session_byte = ET.tostring(session_root, encoding="UTF-8")

            # ...then trying to write the file to memory, if we have permission to do so
            try:
                with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                    f.write(session_byte)
            except PermissionError:
                raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
            # v2.x END

        if type(pressure) == int or type(pressure) == float:
            # if a pressure is provided, set the pressure parameter
            self.pressure = pressure
            # self.parameters["pressure"] = self.pressure

            # v1.x START
            # update session parameters: pressure = pressure
            self.__write_to_aol(self, "pressure", pressure)

            # finally, write pressure measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Pressure: {self.pressure} hPa", time)
            # v1.x END

            # v2.x START
            # parse element tree from .aop
            tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

            # get root tag (session)
            session_root = tree.getroot()

            # create a new "pressure" sub-element of root
            pressure_element = ET.SubElement(session_root, "pressure")

            # add time and entry ID as items of the point tag
            pressure_element.set("time", str(current_jd(time)))
            pressure_element.set("id", str(create_entry_id()))

            # add the actual pressure as text of the pressure tag
            pressure_element.text = str(pressure)

            # since session parameters have changed (pressure), we need to replace the
            # parameters tag as well

            # firstly remove the old tag...
            for parameter_tag in session_root.findall("parameters"):
                session_root.remove(parameter_tag)

            # ...then re-create it with the updated parameters
            parameters_tag = ET.SubElement(session_root, "parameters")

            # populate the parameters sub-element with all the available metadata
            for i in self.__dict__:
                # the self.parameters attribute is legacy only and should be treated as such when updating the code
                if i != "parameters":
                    current_parameter = ET.SubElement(parameters_tag, i)
                    current_parameter.text = str(self.__dict__[i])

            # finally, we overwrite the .aop with the updated element tree

            # converting xml to a byte object...
            session_byte = ET.tostring(session_root, encoding="UTF-8")

            # ...then trying to write the file to memory, if we have permission to do so
            try:
                with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                    f.write(session_byte)
            except PermissionError:
                raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
            # v2.x END

        if type(humidity) == int or type(humidity) == float:
            # if a humidity value  is provided, set the humidity parameter
            self.humidity = humidity
            # self.parameters["humidity"] = self.humidity

            # v1.x START
            # update session parameters: humidity = humidity
            self.__write_to_aol(self, "humidity", humidity)

            # finally, write humidity measurement to protocol
            self.__write_to_aop(self, "CMES", f"Air Humidity: {self.humidity}%", time)
            # v1.x END

            # v2.x START
            # parse element tree from .aop
            tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

            # get root tag (session)
            session_root = tree.getroot()

            # create a new "humidity" sub-element of root
            humidity_element = ET.SubElement(session_root, "humidity")

            # add time and entry ID as items of the humidity tag
            humidity_element.set("time", str(current_jd(time)))
            humidity_element.set("id", str(create_entry_id()))

            # add the actual humidity as text of the humidity tag
            humidity_element.text = str(humidity)

            # since session parameters have changed (humidity), we need to replace the
            # parameters tag as well

            # firstly remove the old tag...
            for parameter_tag in session_root.findall("parameters"):
                session_root.remove(parameter_tag)

            # ...then re-create it with the updated parameters
            parameters_tag = ET.SubElement(session_root, "parameters")

            # populate the parameters sub-element with all the available metadata
            for i in self.__dict__:
                # the self.parameters attribute is legacy only and should be treated as such when updating the code
                if i != "parameters":
                    current_parameter = ET.SubElement(parameters_tag, i)
                    current_parameter.text = str(self.__dict__[i])

            # finally, we overwrite the .aop with the updated element tree

            # converting xml to a byte object...
            session_byte = ET.tostring(session_root, encoding="UTF-8")

            # ...then trying to write the file to memory, if we have permission to do so
            try:
                with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                    f.write(session_byte)
            except PermissionError:
                raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
            # v2.x END

    def report_variable_star_observation(self, star_id: str, chart_id: str, magnitude: float, comparison_star_1: str,
                                         comparison_star_2: str = None, codes: list = None,
                                         time: str = "current") -> None:
        """
        This method reports a (visual) observation of a variable star.

        Alongside your magnitude estimate, the finder chart you used as well as at least one
        comparison star and possible comment codes are logged.
        This method is very much constructed with reporting your observation to the
        American Association of Variable Star Observers (AAVSO) in mind.
        Please note, however, that it DOES NOT write an AAVSO Visual File
        Format compliant report, as this is a higher task left to the front-end application.

        :param star_id: An unambiguous identifier of the variable star being observed (e.g. "del Cep").
        :type star_id: ``str``
        :param chart_id: The ID of the finder chart in usage. AAVSO charts usually have a box at the upper right-hand
        corner containing this information.
        :type chart_id: ``str``
        :param magnitude: Your magnitude estimate, including the decimal point.
        :type magnitude: ``float``
        :param comparison_star_1: The label of the first comparison star being used. AAVSO charts leave out the decimal
        point here, please do so as well.
        :type comparison_star_1: ``str``
        :param comparison_star_2: The label of the second comparison star being used, if any.
        :type comparison_star_2: ``str``, optional
        :param codes: A list of comment codes detailing your observation. Usage of the official AAVSO one-character
        comment codes is recommended, but not mandated.
        :type codes: ``list``, optional
        :param time: An ISO 8601 conform string of the UTC datetime you want your
            observation to be reported at. Can also be "current", in which
            case the current UTC datetime will be used, defaults to "current".
        :type time: ``str``, optional
        :return: None

        :raises SessionNotStartedError: If the session has not yet been started.
        :raises SessionStateError: If the session is not currently "running".
        """

        if codes is None:
            codes = []

        # make sure action makes sense
        if not self.started:
            raise SessionNotStartedError("report variable star observation")
        if not self.state == "running":
            raise SessionStateError(event="report variable star observation", state="not 'running'")

        # v1.x START
        if comparison_star_2 is not None:
            self.__write_to_aop(self, "VSOB",
                                f"{star_id}@{magnitude}: compared to {comparison_star_1} and "
                                f"{comparison_star_2} on chart '{chart_id}'. Comment codes: {codes}",
                                time)
        else:
            self.__write_to_aop(self, "VSOB",
                                f"{star_id}@{magnitude}: compared to {comparison_star_1} on chart '{chart_id}'."
                                f" Comment codes: {codes}",
                                time)
        # v1.x END

        # v2.x START
        # parse element tree from .aop
        tree = ET.parse(f"{self.filepath}/{self.obsID}/{self.obsID}.aop")

        # get root tag (session)
        session_root = tree.getroot()

        # create a new "variable_star" sub-element of root
        variable_star_element = ET.SubElement(session_root, "variable_star_observation")

        # add time and entry ID as items of the variable_star tag
        variable_star_element.set("time", str(current_jd(time)))
        variable_star_element.set("id", str(create_entry_id()))

        # add the star-specific observation parameters as sub-tags of the variable_star tag, respectively
        star_id_tag = ET.SubElement(variable_star_element, "star_id")
        star_id_tag.text = str(star_id)

        magnitude_tag = ET.SubElement(variable_star_element, "magnitude")
        magnitude_tag.text = str(magnitude)

        chart_id_tag = ET.SubElement(variable_star_element, "chart_id")
        chart_id_tag.text = str(chart_id)

        comparison_star_1_tag = ET.SubElement(variable_star_element, "comparison_star_1")
        comparison_star_1_tag.text = str(comparison_star_1)

        if comparison_star_2 is not None:
            comparison_star_2_tag = ET.SubElement(variable_star_element, "comparison_star_2")
            comparison_star_2_tag.text = str(comparison_star_2)

        codes_tag = ET.SubElement(variable_star_element, "observation_codes")
        codes_tag.text = str(codes)

        # converting xml to a byte object...
        session_byte = ET.tostring(session_root, encoding="UTF-8")

        # ...then trying to write the file to memory, if we have permission to do so
        try:
            with open(f"{self.filepath}/{self.obsID}/{self.obsID}.aop", "wb") as f:
                f.write(session_byte)
        except PermissionError:
            raise PermissionError("Error when writing to .aop: You do not have the adequate access rights!")
        # v2.x END


def parse_session(filepath: str, session_id: str) -> Session:
    """
    This function parses a session from memory to a new Session object.

    Provided with the filepath to the general location where the
    log files are stored and an observation ID, it reads in the observation
    parameters from the session's log. This information is then used
    to create a new Session object, which is returned by the function.

    :param filepath: The path to the file where you expect the session directory to reside.
        This is most likely equivalent to the path passed to the Session class
        to create its files in.
    :type filepath: str
    :param session_id: The observation ID of the session to be parsed.
    :type session_id: str

    :raises AolNotFoundError: If there is no .aol legacy file using the specified filepath and observation ID.
    :raises SessionIdDoesntExistOnFilepathError: If the specified observation ID is not in the filepath provided.
    :raises NotADirectoryError: If the specified filepath does not constitute a directory.

    :return: The new Session object parsed from the stored observation parameters.
        For all intents and purposes, this object is equivalent to the object
        whose parameters were used to parse, and you can use it to continue your
        observation session or log just the same. Just be careful not to
        run the Session.start() method again, as this would overwrite the
        existing protocol instead of continuing it! Due to the 'started' flag of
        the new Session object most likely being set to True, however, this should
        generally not be possible.
    :rtype: Session
    """

    # v1.x START
    # Since this action cannot sensibly be carried out twice, the legacy part of this
    # method is already disabled. Nevertheless, it is not removed for now, so that it can be
    # re-activated if need should arise.

    # provided a filepath and the session_id, we can read the session parameters
    # if path.isdir(filepath):
    #     if path.isdir(f"{filepath}/{session_id}"):
    #         try:
    #             with open(f"{filepath}/{session_id}/{session_id}.aol", "rb") as log:
    #                 param = json.load(log)
    #         except FileNotFoundError:
    #             raise AolNotFoundError(session_id)
    #         finally:
    #             log.close()
    #         # unpacking the dictionary we obtained from the .aol, we can construct a
    #         # new Session object
    #         session = Session(filepath, **param)
    #         # if there is no observationID attribute, we (re-)create it from the
    #         # function input
    #         if not hasattr(session, "obsID"):
    #             session.obsID = param["obsID"]
    #             session.parameters["obsID"] = session.obsID
    #         return session
    #     else:
    #         raise SessionIDDoesntExistOnFilepathError(session_id)
    # else:
    #     raise NotADirectoryError("your 'filepath' argument is not a directory")

    # v1.x END

    # v2.x START
    # this is a helper-function allowing to extract the contents of an xml ElementTree into a dictionary.
    def extract_parameters(xml):
        parameters_dictionary = {}
        # iterating through every element of the xml object...
        for element in xml:
            # if it has no more sub-elements, we can copy it into the dictionary, the tag being used as the key
            # and the text as the value
            if len(element) == 0:
                parameters_dictionary[element.tag] = element.text
            # if it has sub-elements, however, we're going to process them the same way, using recursion
            else:
                parameters_dictionary[element.tag] = extract_parameters(element)
        return parameters_dictionary

    # is the provided filepath actually a directory?
    if path.isdir(filepath):
        # is there a valid subdirectory for the observation/session ID provided?
        if path.isdir(f"{filepath}/{session_id}"):
            try:
                # getting the root session element of the log...
                tree = ET.parse(f"{filepath}/{session_id}/{session_id}.aop")
                root = tree.getroot()
                # ...finding the parameters subelement...
                parameters_xml = root.find("parameters")
                # ...extracting the information to a directory...
                parameters_dict = extract_parameters(parameters_xml)
                # ...adding the 'parsing' key to it so the Session constructor knows not
                # to handle this as a brand-new session...
                parameters_dict["parsing"] = True
                # ...all before finally constructing and returning the new Session object...
                session = Session(filepath, **parameters_dict)
                return session
            # ... except we somehow can't find the log file in the directory.
            except FileNotFoundError:
                raise AolNotFoundError(session_id)
        else:
            raise SessionIDDoesntExistOnFilepathError(session_id)
    else:
        raise NotADirectoryError("Your 'filepath' argument is not a directory.")
    # v2.x END
