Tutorials
=========

.. note::

    This page provides a step-by-step explanation of each function of aop. If you're
    looking for some quick references, go to the :doc:`Examples <examples>` page instead!

Think you could use aop but are not sure about exactly **how** to use it? Confused by all
the super-technical API stuff? This page is here to help! In the following paragraphs,
we will tackle the functionality of the aop package bit-by-bit in small, easy to
understand steps. All right, let's get going!

.. attention::

    Writing tutorials takes some time, so this page will not always be up to date.
    Especially when new features were added recently, there may not be a tutorial on
    them right away.

.. note::

    This tutorial works with version 1.0.

Getting started
---------------

First, a few quick words on how this whole thing's gonna work. The Python programming
language, that aop is written for, has a structure known as *classes*.
The concept is simple: Every observing session follows some basic rules, the same
parameters could be relevant and there's only so much you can do during a session.

That's why at the core of the aop package, there's a class simply called :class:`aop.aop.Session`.
Everything to do with aop requires you to work with that class (or, to be super-precise,
*instances* of that class).

But before we dive too deep into the technical stuff already, let's first get a few
conventions straight: Since aop is meant to be implemented front-end and hence has no
real front-end interface, working with the package as is requires us to write some code.
We could do this in a Python script, or in the Python interactive console. We could even
use something more sophisticated like a Jupyter notebook or something. You can really
use whatever you see fit, but for the purpose of this tutorial, we will assume that you
use the Python console. We will therefore print '>>>' in front of every command, as is
convention for the console. If you were using a Jupyter notebook, for example, this
would be equivalent to ``In[1]`` and so on. Enter the console by typing ``python`` in
a command-line interface or terminal (on UNIX-like systems, you sometimes have to type
``python3`` instead). See the Installation guide for help on how to get to the command-
line.

All right, with all that out of the way, let's finally get our hands on some code!
Of course, if you want to use aop, you first have to import it using the ``import``
Statement. Since the aop package contains two modules, :mod:`aop.aop` (providing the main
functionality) and :mod:`aop.tools`, providing largely custom exceptions, we need to
pronounce our ``import`` statement like so:

.. code-block:: python

    >>> from aop.aop import *
    >>> from aop.tools import *

The asterisk symbol * indicates that we want to import all the content of those two
modules. We can verify our import worked by quickly checking the current Julian Date:

.. code-block:: python

    >>> current_jd()
    2460098.980502531

Hooray, it worked! Now that we know how to import the package into our code, we can move
on to the next step.

Our first Session
------------------------

In this section, we will launch our first observing session using aop! We will assume that you have
successfully imported the aop package as described above. If you have, creating a session is a really
straightforward process. Simply type

.. code-block:: python

    >>> my_session = Session(filepath="/home/amelie/astronomy_logs/")

where you replace the *filepath* argument with whatever location you want your logs to be stored to.

.. attention::

    If you are on Windows and want to use the Windows-specific backslash (\) notation
    (e.g. C:\Users\Amelie\astronomy_logs\) you either have to put a little r in front of the first
    quotation mark or double each backslash. This is because Python uses the backslash as a special
    character and would therefore not realize this was a file path. You should, however, be able
    to use regular slashes for Windows paths as well.

Congratulations! You've just created your first instance of aop's :class:`aop.aop.Session` class! That
is what the ``my_session`` object you've just instantiated is. You can now use all the methods of the
``Session`` class on that object.

But before we do that, we'll dive a bit deeper into the possibilities when setting up a new session.
As you've seen, aop requires you to give it a *filepath* argument to know where to store its stuff.
Since this argument is required, you could technically also remove the "filepath=" part, so long as
it remains the first argument.

The Session constructor method, that does all the heavy lifting for us here, also excepts a wide range
of other arguments, however. These are optional, so we need to state them by name. Providing information
on the observer and the location would look like this, for example:

.. code-block:: python

    >>> my_session = Session(filepath="/home/amelie/astronomy_logs/",
                             observer="Jane Doe",
                             locationDescription="12 Example Road")

There are many more options here, check the documentation of the :class:`aop.aop.Session` class for reference.

The door is now wide open, but before we can do anything else, there is just one small step we need to take:
We need to start the session first. It might seem counterintuitive that an aop session does not start
upon creation, but this has one practical reason: Doing it like this, you can prepare your Session
object in advance, and start the session whenever you're ready, which some people might find useful.
Keep in mind, after all, that the aop package is really not meant to be used in an interactive shell
like we do here, but it is meant to be implemented by an app that provides a proper front-end interface.

Nonetheless, starting the session is just this simple command away:

.. code-block:: python

    >>> my_session.start()

And that's it! The start() method works all by itself, no arguments required. You can provide it with
the ``time`` argument, as all ``Session`` methods, but that's a story for another day that is really not
necessary for beginners.

aop should also now have logged it's first entry. To check it out, navigate to the file path you provided
aop with when creating the my_session object in the beginning. You should see a new directory there with
a somewhat cryptic name that starts with the current date in year-month-day format appeared. This is
the observation ID, that makes your specific observation unique. It consists of the date and time it
was created, separated by hyphens, and then ten random characters and numbers, that provide another
level of uniqueness. Move into that directory and you should see two files of the same name, but with
different file extensions. There is one with extension ``.aol`` that we're going to ignore for now.
The real stuff happens inside the ``.aop`` file, which you can open with any text editor (though
high-level word processing applications such as LibreOffice Writer or Microsoft Word are not ideal
since they would likely mess up the layout - please something along the lines of NotePad, which should
be built into all modern operating systems in some capacity).

If you go ahead and do so, you'll firstly see a bunch of meta-data that you provided above. But then,
in a new paragraph, you should now see a line that starts with some gibberish in brackets, then a very
large number around 2.5 million, and finally the message ``SEEV SESSION observation id STARTED``. That
means we were successful!

A few more detailed notes on the contents of that line: The first part, in the brackets, is the so-called
entry ID, that makes every proper entry completely unique, even across observations. It consists of
the date and precise time it was created, all smashed together before the hyphen in the middle, and then
30 characters and numbers that are completely random and ensure that your entry ID is completely unique.
The point of creating a log is to be able to reference it in the future, after all.

The large number that follows the entry ID is the so-called *Julian Date* (JD), a system of keeping
time that is often used in astronomy, since it is independent of time zones, daylight saving hours,
calendar conventions, etc. It instead relies on counting the days that have passed since a largely
arbitrary, yet very well defined point in the distant past. If you're curious, try to calculate which
date it was (or look it up, since this stuff can get really complicated). This counting of Julian Date
has ten decimal places, corresponding to an accuracy of a 10 billionth of a day (0.00864 milliseconds
or 8.64 microseconds). That is limited by the accuracy of your device's clock, however.

After the arrow (``->``), that is just a visual aid to separate the technical stuff from the actual
log, there is only one mystery left: What does ``SEEV`` mean? This is what is known to aop as an
*op code*, short for operation code, and it encrypts what type of action is recorded here. Starting
the session falls into the category of *"session events"* (hence the abbreviation SEEV). Everything
that comes after the op code is referred to as the op code's *argument* and carries the additional
information necessary for understanding what has been going on - in this case, the information that
a session was started, along with it's specific observation ID (although this is technically not
necessary, since the observation ID is also recorded at the top of the file with the other
*session parameters* under the short handle "obsID").

You're now familiar with setting up an aop session, starting it, and you also now where to find the
results and how to read them. That's a great start! In the next chapter, we will explore the other
session events that are available to you.