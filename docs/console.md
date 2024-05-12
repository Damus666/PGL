## [<- Back](PGL.md)

# Console Interface

Using the command `python/python3 pgl` you get access to the console interface. It allows to:

- Create projects
- Compile projects
- Run projects

## Create a project

Use the command `python pgl <project name> -new`<br>
It will create a folder named like the project inside the projects folder.<br>
The new folder will contain:

- A config.json file
- An assets folder
- A folder named main with a main.py file and some boilerplate code
- A prelude.pyi stub file

You will learn how to use them later.

## Compile a project

With the command `python pgl <project name> -compile` you can compile a project without running it. This step will be executed when running it aswell.<br><br>
It works by stitching the engine runtime and all your scripts in one file named `out.py` which is automatically generated. If you run that file your game will be executed.

## Run a project

Use the command `python pgl <project name>` without flags and the project will be compiled and run.
