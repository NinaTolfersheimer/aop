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
