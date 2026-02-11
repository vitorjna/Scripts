import os
import subprocess
from pathlib import Path
from enum import IntEnum, Enum

from projects_config import PROJECTS, PATH_TORTOISE, GIT_TOOL

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Commands(IntEnum):
    CHECKOUT = 1
    COMMIT = 2
    LOG = 3
    POP = 4
    PULL = 5
    PUSH = 6
    STATUS = 7
    CMD = 8
    OPEN = 9

class Tools(ExtendedEnum):
    TORT = "tortoise"
    GIT = "git"

def getCommandForTool(command, tool):
    match command:
        case Commands.CHECKOUT:
            match tool:
                case Tools.TORT: return "switch"
                case Tools.GIT:
                    branch = input("Enter branch name: ")
                    return f"{Commands.CHECKOUT.name.lower()} {branch}"
                case _: return Commands.CHECKOUT.name.lower()

        case Commands.COMMIT:
            match tool:
                case Tools.GIT:
                    message = input("Enter commit message: ")
                    return f"commit -a -m \"{message}\""
                case _: return Commands.COMMIT.name.lower()

        case Commands.LOG: return Commands.LOG.name.lower()

        case Commands.POP:
            match tool:
                case Tools.GIT:  return "stash pop"
                case Tools.TORT: return "stashpop"
                case _: return Commands.CHECKOUT.name.lower()

        case Commands.PULL: return Commands.PULL.name.lower()

        case Commands.PUSH: return Commands.PUSH.name.lower()

        case Commands.STATUS:
            match tool:
                case Tools.TORT: return "repostatus"
                case _: return Commands.STATUS.name.lower()

        case Commands.CMD: return input("Enter command: ")

        case _: return ""


if __name__ == "__main__":

    while True:
        project_name = input(f"\nSelect a Project: {', '.join(PROJECTS.keys())}: ").upper()

        if project_name == 'Q':
            break

        if project_name not in PROJECTS:
            print("Invalid project selected.")
            continue

        reposLocation, repos = PROJECTS[project_name]
        print("Selected repos: " + str(repos))

        tool_to_use = Tools(GIT_TOOL)

        while True:
            git_commands = sorted([name for name in Commands._member_names_ if Commands[name] < Commands.CMD])
            other_commands = sorted([name for name in Commands._member_names_ if Commands[name] >= Commands.CMD])
            commands_display = f'[{", ".join(git_commands)}], [{", ".join(other_commands)}], [BACK], [Q]'

            command_name = input(f"\n[{project_name}] Select a Command: {commands_display}: ").upper()
            if command_name == 'Q':
                os.system('pause')
                exit()

            if command_name == 'BACK':
                break

            if command_name == 'OPEN':
                first_repo = next(iter(repos))
                full_repo_path = Path(reposLocation) / first_repo
                print(f"Opening {full_repo_path} in Explorer...")
                os.startfile(full_repo_path)
                continue

            if command_name not in Commands._member_names_:
                print("Invalid command selected.")
                continue

            command_enum = Commands[command_name]
            command_action = getCommandForTool(command_enum, tool_to_use)
            print("Selected command: " + command_action)

            for repo in repos:
                full_repo_path = Path(reposLocation) / repo
                if command_enum == Commands.CMD:
                    cmd = f'start /wait cmd /c "cd /d "{full_repo_path}" && {command_action} && pause"'
                elif tool_to_use == Tools.TORT:
                    cmd = f'"{PATH_TORTOISE}" /path:"{full_repo_path}" /command:{command_action}'
                else:
                    cmd = f'start /wait cmd /c "git -C "{full_repo_path}" {command_action} && pause"'

                print(f'Running: {cmd}')
                subprocess.run(cmd, shell=True)

    os.system('pause')
