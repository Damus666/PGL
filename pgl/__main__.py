import sys
from pgl.main import run_project, build_project, create_project, set_directory

if __name__ == "__main__":
    MIN_ARGV = 2

    COMMAND_FUNC = {
        "run": run_project,
        "build": build_project,
        "create": create_project,
        "set_dir": set_directory,
    }

    argv = sys.argv[1:]

    if len(argv) == 1 and argv[0] == "help":
        print(
            "Available commands: run <path>, build <path>, create <name>, set_dir <path>"
        )
        sys.exit()

    if len(argv) < MIN_ARGV:
        print(f"Wrong amount of arguments ({len(argv)}), expected {MIN_ARGV}")
        sys.exit()

    command = argv[0]
    if command not in COMMAND_FUNC:
        print(f"Unknown command '{command}'")
        sys.exit()

    if command != "run":
        COMMAND_FUNC[command](argv[1])
    else:
        if "-nocompile" in argv:
            run_project(argv[1])
        else:
            build_project(argv[1])
            run_project(argv[1])
