import sys
from pgl.main import (
    run_project,
    build_project,
    create_project,
    set_directory,
    start_app,
    list_projects,
    PGLError,
)

if __name__ == "__main__":
    DOUBLE_COMMAND_FUNC = {
        "run": run_project,
        "build": build_project,
        "create": create_project,
        "set_dir": set_directory,
    }
    SINGLE_COMMAND_FUNC = {
        "app": start_app,
        "help": lambda: print(
            "Available commands: run <path>, build <path>, create <name>, set_dir <path>"
        ),
        "list": list_projects,
    }

    argv = sys.argv[1:]
    if len(argv) < 1:
        print(f"Wrong amount of arguments ({len(argv)}), expected at least 1")
        sys.exit()

    command = argv[0]
    if command not in list(DOUBLE_COMMAND_FUNC.keys())+list(SINGLE_COMMAND_FUNC.keys()):
        print(f"Unknown command '{command}'")
        sys.exit()

    if command in SINGLE_COMMAND_FUNC:
        try:
            SINGLE_COMMAND_FUNC[command]()
            raise SystemExit
        except PGLError as e:
            print(e)
            sys.exit()

    if len(argv) < 2:
        print(f"Wrong amount of arguments ({len(argv)}), expected at 2")

    if command != "run":
        try:
            DOUBLE_COMMAND_FUNC[command](argv[1])
        except PGLError as e:
            print(e)
            sys.exit()
    else:
        try:
            if "-nocompile" in argv:
                run_project(argv[1])
            else:
                build_project(argv[1])
                run_project(argv[1])
        except PGLError as e:
            print(e)
            sys.exit()
