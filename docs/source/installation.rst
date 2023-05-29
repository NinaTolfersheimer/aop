Installation
============

To use aop, you first have to install it. Since it is a Python package, you
obviously have to have Python installed. Get it from `the official website
<https://www.python.org/download/>`_ if you don't have it installed already.
You will also need the pip tool, but it usually ships with the Python
interpreter available over the link above (if you for some reason don't have it,
check with `the pip documentation <https://pip.pypa.io/en/stable/installation/>`_
for help).

After you have Python and pip installed, we can shift our attention towards aop. Always
install it from source using pip. First download the source code from
`GitHub <https://github.com/NinaTolfersheimer/aop>`_.

The next step involves a little time spent in a command-line or terminal, so if you've
never done anything like that, no worry, I'll walk you through. The process is dependent
on your operating system, so please go to the specific sub-section below.

Linux or MacOS
--------------
Suppose you have stored the contents of the GitHub repository to
``/home/amelie/Downloads/aop``. Now open your terminal window and navigate to the
folder you stored the source code in. The terminal prompt should start out in your home
directory, so if you fire it up it should look something like this:

.. code-block:: console

    amelie@ameliescomputer:~$

.. tip::
    The ~ symbol refers to your home directory, so ``/home/amelie/`` in our example.

Now navigate to the source code directory using the following command:

.. code-block:: console

    amelie@ameliescomputer:~$ cd Downloads/aop

The prompt now changes to

.. code-block:: console

    amelie@ameliescomputer:~/Downloads/aop$

Using the ``ls`` command, we can inspect the contents of the directory. If you are in
the correct directory, your output should look something like this:

.. code-block:: console

    amelie@ameliescomputer:~/Downloads/aop$ ls
    aop  LICENSE  README.md  requirements.txt  setup.py

If it doesn't, search around a bit. Downloading from GitHub sometimes adds extra
directories around the ones containing the actual code. You can enter those using
the same ``cd <name of directory>`` command as above.

.. tip::

    If you want to get out of a directory, just type ``cd ..`` -  the two dots
    always refer to the parent directory of the one you're currently in, while a
    single dot ``.`` refers to the directory you're currently in.

After you have successfully found the correct source folder, whose ``ls`` output looks
like described above, it's finally time to install the ``aop`` package to your system.
To do so, simply type in the following command (without the dollar sign):

.. code-block:: console

    $ pip install -r requirements.txt .

.. attention::

    Don't forget the extra dot after ``requirements.txt``! While it seems minor, it is
    actually one of the most important parts of this command. As we mentioned earlier,
    a single dot like this refers to the current directory, so
    ``/home/Amelie/Downloads/aop`` in our case. This tells pip to interpret whatever it
    encounters in the current directory as the package we want to install. Without the
    dot it would be completely clueless!

You should see a bunch of lines thrown at you by pip, but as long as the last line says
something like ``Successfully installed aop-1.0``, you're golden.

Congretulations! You've now successfully installed the ``aop`` Python package to your
computer. You can verify that it worked by trying to import it to a Python file.
The most convenient way is to enter Python interactive mode by typing ``python3`` into
your terminal prompt. You should now be seeing something like this '>>>' replacing
your usual ``amelie@ameliescomputer:~$`` prompt. Now type:

.. code-block:: python

    >>> import aop

If there is no reaction and a new prompt (>>>) appears, that means it worked! You
could even type ``help(aop)`` to receive more info about the package, etc.

Windows
-------
The general process is pretty much the same as for UNIX-like systems (Linux and macOS),
only the commands we use slightly differ. That's why I'm not going to describe the general
installation process in great detail here again.

The terminal in Windows is called command line and is somewhat hidden, unfortunately.
If you do not know already how to find it, enter the start menu and search for
``cmd.exe``. Open that application and you are in the Windows command line.

Similarly to Linux, the command prompt will likely start in your home directory. We will
again assume that you have downloaded the aop package source code from GitHub and stored
it to ``C:\Users\Amelie\Downloads\``. The command prompt starts like this:

.. code-block:: powershell

    C:\Users\Amelie>

You can navigate to the aop folder using the same ``cd`` command as on Linux.

.. code-block:: powershell

    C:\Users\Amelie> cd Downloads\aop

    C:\Users\Amelie\Downloads\aop>

Now again, check that you are in fact in the correct directory! This time, however,
you have to use a different command. The appropriate command for listing a folder's
content on Windows is called ``dir``, and it's expected output looks like this (whatever
information is unnecessary is substituted for 'X'):

.. code-block:: powershell

    C:\Users\Amelie\Downloads\aop> dir
     Volume XXX
     Volume Serial Number is XXXX-XXXX

     Directory of C:\Users\Amelie\Downloads\aop
    XX.XX.XXX  XX:XX    <DIR>          .
    XX.XX.XXX  XX:XX    <DIR>          ..
    XX.XX.XXX  XX:XX    <DIR>          aop
    XX.XX.XXX  XX:XX             X.XXX LICENSE
    XX.XX.XXX  XX:XX             X.XXX README.md
    XX.XX.XXX  XX:XX                XX requirements.txt
    XX.XX.XXX  XX:XX               XXX setup.py
                   4 File(s),          X.XXX bytes
                   3 Dir(s), XXX.XXX.XXX.XXX bytes free

Like previously, move around your folders until you are in the correct one, whose
``dir`` output looks like above (to move up, use ``cd ..`` again). Then execute

.. code-block:: powershell

    pip install -r requirements.txt .

.. attention::

    Again: Mind the dot!

to install the package. You can verify it's installation by typing ``python`` to enter
interactive mode, type

.. code-block:: python

    >>> import aop

and if it just prints the next '>>>', ``aop`` is installed on your system!

other operating systems
-----------------------
Unfortunately, I cannot provide you with a step-by-step tutorial here. Try searching
the web for help on how to install Python packages from source in your specific OS.
