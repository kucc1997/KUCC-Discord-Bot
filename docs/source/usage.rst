Usage
=====

.. _installation:

Installation
------------

First make a python virtual environment:

.. code-block:: console

    $ python -m venv env


Then you need activate the virtual environment:

.. code-block:: console

    $ # For Windows we use 
    $ ./env/Scripts/Activate.ps1 # for powershell
    $ ./env/Scripts/activate.bat # for Command Prompt
    $ # For POSIX
    $ source env/Scripts/Activate

Finally you need to install the necessary python packages.
The names of required packages are in *requirements.txt*.

.. code-block:: console

    $ python -m pip install -r requirements.txt

Now you can run the project.


Building Documentation
----------------------

To build the documentation file locally.

.. code-block:: console

    $ cd docs
    $ ./make html # This make it into locally available html webpages.

You can build the documentation files in different file formats.
However, Extensions are required to build it in other formats.