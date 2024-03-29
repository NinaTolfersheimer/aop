# aop
aop is a Python package for amateur astronomical observation logs.

Are you an amateur astronomer or astrophotographer who has some ambitions to document their observations in a clean, meaningful way? Maybe you are currently working on a small, home-made research project or maybe you are just struggling to remember the order of all the calibration frames you took last night. Either way, the aop package is for you! It provides a clear and straightforward way for the logging of amateur observations of the night sky. aop only provides the means to do so, however, as it is meant to be implemented by a front-end application. Theoretically, you could use any app that is capable of implementing this package. We recommend the use of Amélie Hohe's [Gala](https://github.com/NinaTolfersheimer/Gala) to improve your observation logging quality. Focus on the hobby you enjoy, and aop and Gala will do the logging for you.

## Installation
Save the code in this repository to your hard drive and unpack the zip archive. In a command-line, move to the directory you copied it to (as contents of that directory, you should see at least `setup.py` and the `aop` subdirectory). Now execute
```
pip install -r requirements.txt .
```
Congretulations! You should now be able to use `import aop` in every Python file on your machine.

## Scope
This is a package, so it does not include any way to actually *use* the possibilities it creates. Although it would be possible to run this code in an interactive Python console and to then call the methods directly, this is not the intended usage. This code is meant to be implemented by another application that provides a front-end interface.

Nina Tolfersheimer Industries is currently working on the development of *Gala*, the Graphical Astronomy Logging Application, to fill this gap and to implement the aop package properly.

## How to use
*Note: This is just a simple overview. Check out the [proper documentation](https://aop-package.readthedocs.io) for technical details.*

The main feature of aop is the `Session` class. This class represents an amateur astronomical observation session. When initializing a `Session` object, you can provide a variety of parameters describing the session details further, e.g. the observer, geographical position, etc. All observation related actions you might take throughout the session are represented by `Session` methods.

You can `start`, `interrupt`, `resume`, `abort`, or simply `end` a session; you can also take notes (`comment`), measure or describe conditions in a `condition_report`, report an `issue`, point at objects identified by name (`point_to_name`) or ICRS coordinates (`point_to_coords`), as well as take pictures of them (`take_frame`). You can also report your magnitude estimate of a variable star using the `report_variable_star_observation` method. Parsing the information of a past session into a new `Session` object is also possible using the `parse_session` function independent from the `Session` class.

aop will mainly take care of the process of logging these events to an xml file. It requires the implementing software to provide sensible information, as well as a writable space to store the logs.
