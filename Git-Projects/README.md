# Git Projects Automation

This script (`git_projects.py`) is a Python-based tool for executing Git commands across multiple local repositories associated with specific projects.

## Features

- **Project-based Repository Management**: Define projects, each with its own set of Git repositories.
- **Configurable Paths**: Easily configure base paths for your repositories and external tools (like TortoiseGit or WinMerge).
- **Git Command Execution**: Execute common Git commands (pull, push, status, checkout, log, pop) across all repositories within a selected project.
- **Tool Integration**: Supports both TortoiseGit and standard Git CLI commands.

## Setup and Usage

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/vitorjna/Scripts.git
    cd Scripts/Git-Projects
    ```

2.  **Configure Your Projects**:
    This project uses a separate configuration file, `projects_config.py`, to define your local repository paths and projects. This file is intentionally excluded from Git version control to protect your local setup details.

    -   **Create `projects_config.py`**:
        Copy the provided sample file `projects_config.py.sample` to `projects_config.py`:
        ```bash
        cp projects_config.py.sample projects_config.py
        ```

    -   **Edit `projects_config.py`**:
        Open `projects_config.py` and update the following variables with your actual local paths and project definitions:

        -   `PATH_CPP`: Base path for your C++ related repositories.
        -   `PATH_JAVA`: Base path for your Java related repositories.
        -   `PATH_WINMERGE`: Path to your WinMerge executable (if used).
        -   `PATH_TORTOISE`: Path to your TortoiseGitProc.exe executable.
        -   `USE_TORTOISE`: Set to `True` to use TortoiseGit commands, `False` to use standard Git CLI commands.
        -   `PROJECTS`: A dictionary where the keys are your project names and the values are tuples containing the base path and a set of repository names within that path.

        Example `projects_config.py` content:
        ```python
        # Configuration for Git Projects
        import os

        # Base paths for repositories
        PATH_CPP = r'C:\path\to\your\cpp\repos'
        PATH_JAVA = r'C:\path\to\your\java\repos'

        # Paths to external tools
        PATH_WINMERGE = r'C:\Program Files\WinMerge\WinMergeU.exe'
        PATH_TORTOISE = r'c:\Program Files\TortoiseGit\bin\TortoiseGitProc.exe'

        # Use TortoiseGit (True) or Git CLI (False)
        USE_TORTOISE = True

        # Project definitions: { "PROJECT_NAME": (base_path, {"repo1", "repo2", ...}) }
        PROJECTS = {
            "PROJECT_CPP": (PATH_CPP, {"cpp-repo-1", "cpp-lib-1"}),
            "PROJECT_JAVA": (PATH_JAVA, {"java-repo-1", "java-lib-1", "java-dependency-1"}),
        }
        ```

3.  **Run the Script**:
    Execute the `git_projects.py` script from your terminal:
    ```bash
    python git_projects.py
    ```

    The script will prompt you to:
    -   Select a project from the defined list.
    -   Select a Git command to execute (e.g., PULL, PUSH, STATUS, CHECKOUT, LOG, POP).
    -   The selected command will then be executed on all repositories associated with the chosen project.

## Project Structure

-   `git_projects.py`: The main script that orchestrates Git commands.
-   `projects_config.py`: (Local, untracked) Your personal configuration file with repository paths and project definitions.
-   `projects_config.py.sample`: A sample configuration file to guide you in creating `projects_config.py`.
-   `.gitignore`: Ensures `projects_config.py` is not committed to your Git repository.