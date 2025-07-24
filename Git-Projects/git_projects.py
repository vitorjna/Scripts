import os
import subprocess
from pathlib import Path
from enum import IntEnum, Enum

from projects_config import PROJECTS, PATH_TORTOISE, USE_TORTOISE

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Commands(IntEnum):
    PULL = 1
    PUSH = 2
    STATUS = 3
    CHECKOUT = 4
    LOG = 5
    POP = 6

class Tools(ExtendedEnum):
    TORT = "tortoise"
    GIT = "git"

def getCommandForTool(command, tool):
    match command:
        case Commands.PULL: return Commands.PULL.name.lower()
        case Commands.PUSH: return Commands.PUSH.name.lower()
        case Commands.STATUS:
            match tool:
                case Tools.TORT: return "repostatus"
                case _: return Commands.STATUS.name.lower()
        case Commands.CHECKOUT:
            match tool:
                case Tools.TORT: return "switch"
                case _: return Commands.CHECKOUT.name.lower()
        case Commands.POP:
            match tool:
                case Tools.GIT:  return "stash pop"
                case Tools.TORT: return "stashpop"
                case _: return Commands.CHECKOUT.name.lower()
        case Commands.LOG: return Commands.LOG.name.lower()
        case _: return ""


if __name__ == "__main__":

    while True:
        project_name = input(f"Select a Project: {', '.join(PROJECTS.keys())}: ").upper()
        
        if project_name == 'Q':
            os.system('pause')
            exit()
            
        if project_name not in PROJECTS:
            print("Invalid project selected.")
        else:
            break

    reposLocation, repos = PROJECTS[project_name]
    print("Selected repos: " + str(repos))

    tool_to_use = Tools.TORT if USE_TORTOISE else Tools.GIT

    while True:
        command_name = input(f"Select a Command: {Commands._member_names_}: ").upper()
        if command_name == 'Q':
            break

        if command_name not in Commands._member_names_:
            print("Invalid command selected.")
            continue

        command_action = getCommandForTool(Commands[command_name], tool_to_use)
        print("Selected command: " + command_action)

        for repo in repos:
            full_repo_path = Path(reposLocation) / repo
            if tool_to_use == Tools.TORT:
                cmd = f'"{PATH_TORTOISE}" /path:"{full_repo_path}" /command:{command_action}'
            else:
                cmd = f'git -C "{full_repo_path}" {command_action}'

            print(f'Running: {cmd}')
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)


    os.system('pause')
