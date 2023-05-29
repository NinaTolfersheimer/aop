# aop
aop is a Python package that implements the [aop standard v1.0](https://tolfersheim.ddns.net/index.php/s/GabziFRsMD7FLeY) for amateur astronomical observation logs.

Are you an amateur astronomer or astrophotographer who has some ambitions to document their observations in a clean, meaningfull way? Maybe you are currently working on a small, home-made research project or maybe you are just struggeling to remember the order of all the calibration frames you took last night. Either way, the aop standard is for you! It provides a clear and straightforward standard for the logging of amateur observations of the night sky. aop is the Python module that implements this standard. Nina Tolfersheimer Industries, the developer of both the standard and the module, recommend the use of [Gala](https://ninatolfersheimer.github.io/gala) to make it easy to use.

## Installation
Save the code in this repository to your hard drive. In a command-line, move to the directory you copied it to (as contents of that directory, you should see at least `setup.py` and the `aop` subdirectory). Now execute
```
pip install .
```
Congretulations! You should now be able to use `import aop` in every Python file on your machine.

**CAUTION!** aop is still in a pre-release and testing phase. It cannot be considered stable and it is very likely that there are bugs in the code, even ones that will crash the application. In case of doubt, please wait for the full release of v1.0.

## Scope
This is a module, so it does not include any way to actually *use* the possibilities it creates. Although it would be possible to run this code in an interactive Python console and to then call the methods directly, this is not the intended usage. This code is meant to be implemented by another application.

Nina Tolfersheimer Industries is currently working on the development of *Gala*, the Graphical Astronomy Logging Application, to fill this gap and to implement the aop module properly.

## How to use
*Note: This is just a simple overview. Check out the [proper documentation](https://ninatolfersheimer.github.io/aop) for technical details.*

The main feature of aop is the `Session` class. This class represents an amateur astronomical observation session. When initializing a `Session` object, you can provide a variety of parameters describing the session details further, e.g. the observer, geographical position, etc. All observation related actions you might take throughout the session are represented by `Session` methods.

You can `start`, `interrupt`, `resume`, `abort`, or simply `end` a session; you can also take notes (`comment`), measure or describe conditions in a `condition_report`, report an `issue`, point at objects identified by name (`point_to_name`) or ICRS coordinates (`point_to_coords`), as well as take pictures of them (`take_frame`). Parsing the information of a past session into a new `Session` object is also possible using the `parse_session` function independent from the `Session` class.

aop will mainly take care of the process of logging these events according to the protocol standard of the same name. It requires the implementing software to provide sensible information, as well as a writable space to store the logs.
