# KUCC-Discord-Bot

___________________________________________________________

This is the repository of the Discord Bot written in Python programming language for the Official Discord Server of Kathmandu University Computer Club.

___________________________________________________________

**INSTALLATION**

First make a python virtual environment:

```
    $ python -m venv env
```


Then you need activate the virtual environment:

```
    $ # For Windows we use 
    $ ./env/Scripts/Activate.ps1 # for powershell
    $ ./env/Scripts/activate.bat # for Command Prompt
    $ # For POSIX
    $ source env/Scripts/Activate
```


Finally you need to install the necessary python packages.
The names of required packages are in *requirements.txt*.

```
    $ python -m pip install -r requirements.txt
```

Now you can run the project.

___________________________________________________________

**BUILDING DOCUMENTATION**

To build the documentation file locally.

```
    $ cd docs
    $ ./make html   # This make it into locally available html webpages.
```
You can build the documentation files in different file formats.
However, Extensions are required to build it in other formats.

___________________________________________________________

**FOR CONTRIBUTUION**

first fork the master repo then create a new branch in the new fork.
Then add your code and commit it to your fork.
Create a pull requst and link the pull request to the relevant issue.

___________________________________________________________