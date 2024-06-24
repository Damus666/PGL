## [<- Back](PGL.md)

# Console Interface

Using the command `python/python3 pgl` you get access to the console interface. It allows to:

- Create projects
- Compile projects
- Run projects
- Set the projects directory

## Set the projects directory

New projects will be created there and paths passed to the run and build commands are also searched in there.
The path is stored at Users/current user/AppData/Roaming/PGL/PGL/userdata.json and in the same directory there
is a default projects folder.

To change the projects directory run `python pgl set_dir <path>`

## Create a project

Use the command `python pgl create <project name>`<br>
It will create a folder named like the project inside the projects folder.<br>
The new folder will contain:

- A config.json file
- A ruff.toml file to ignore errors with ruff
- An assets folder
- A folder named main with a main.py file and some boilerplate code
- A prelude.pyi stub file

You will learn how to use them later.

## Compile a project

With the command `python pgl build <project name>` you can compile a project without running it. This step will be executed by default when running it aswell.<br><br>
It works by stitching the engine runtime and all your scripts in one file named `out.py` which is automatically generated. If you run that file your game will be executed.

## Run a project

Use the command `python pgl run <project name>` and the project will be compiled and run. By adding the flag `-nocompile` your code won't be compiled before running.
