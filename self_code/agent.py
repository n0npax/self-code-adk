import os
import sys
import re
from google.adk.agents import Agent


def get_my_application_code(
    root_dir: str, only_py_files: bool = False, max_files: int = 100
) -> list[dict[str, str], dict[str, str]]:
    """Retrieves the content of all files within a directory and its subdirectories.

    Builds a dictionary where keys are file paths relative to the input directory
    and values are the content of the files. Handles text files with UTF-8 encoding.
    Files that cannot be decoded as UTF-8 are stored with an error message
    as their value.

    Args:
        root_dir (str): The path to the root directory of the application
                        or codebase.
        only_py_files (bool): Include only .py files, ignore all other.
        max_files (int): Read no more than given number of files.

    Returns:
        dict: A dictionary mapping relative file paths (str) to file content (str).
        dict: A dictionary mapping relative file paths (str) to error encoutered during the read attempt (str)
    """
    file_contents = {}
    file_read_errors = {}

    if not os.path.isdir(root_dir):
        file_read_errors[root_dir] = "specified root directory is not directory"
        return file_contents, file_read_errors

    # Ensure the root_dir is an absolute path for reliable relative path calculation
    root_dir = os.path.abspath(root_dir)

    read_files_cnt = 0
    # Walk through the directory
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_file_path = os.path.join(dirpath, filename)

            # Calculate the path relative to the starting directory
            # This will be the key in our dictionary
            try:
                relative_file_path = os.path.relpath(full_file_path, root_dir)
            except ValueError:
                # Handle cases where full_file_path and root_dir are on different drives on Windows
                relative_file_path = full_file_path  # Use full path as fallback

            # Skip common non-code/binary files or directories if necessary
            # You might want to add more filters here (e.g., images, logs, .git)
            # Example check:
            if any(part.startswith(".") for part in relative_file_path.split(os.sep)):
                # Skip hidden files/directories
                continue
            if relative_file_path.endswith((".pyc", ".git", ".DS_Store")):
                continue
            if only_py_files and not relative_file_path.endswith(".py"):
                continue
            try:
                if read_files_cnt > max_files:
                    file_read_errors[relative_file_path] = (
                        "already read {max_files}. This read exceeds defined limit, so skipping it. You can rerun function with bigger max_files param."
                    )
                    continue
                # Attempt to read the file content as UTF-8 text
                # You might need to adjust encoding for specific projects
                with open(full_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_contents[relative_file_path] = content
                read_files_cnt += 1

            except UnicodeDecodeError:
                # Handle binary files or files with different encodings that
                # cannot be read as standard UTF-8 text.
                error_msg = (
                    f"[Error: Could not decode file as UTF-8 text: {full_file_path}]"
                )
                file_read_errors[relative_file_path] = error_msg
            except PermissionError as e:
                error_msg = f"[Error: Permission denied reading file: {full_file_path} - {type(e).__name__} - {e}]"
                file_read_errors[relative_file_path] = error_msg
            except Exception as e:
                # Catch other potential errors during file reading (e.g., permissions, large files)
                error_msg = f"[Error reading file: {full_file_path} - {e}]"
                file_read_errors[relative_file_path] = error_msg

    return file_contents, file_read_errors


def autodiscover_possible_root_dir() -> list[str]:
    """Finds possible root directories of current application

    Returns:
        list[str]: list of directories which may be the root of the application.
    """
    possible_roots = [os.getcwd()]
    try:
        main_script_path = os.path.abspath(sys.modules["__main__"].__file__)
        app_root_main = os.path.dirname(main_script_path)
        possible_roots.append(app_root_main)

        # handle venv, if `.anything/bin` or `.anything\Scripts` is at and of string, trim it and add again.
        # Modified regex to handle both forward and backslashes for different OS.
        pattern = r"[/\\]\..+[/\\](bin|Scripts)$" # Also added Scripts for Windows venv
        match = re.search(pattern, app_root_main)
        if match is not None:
            possible_roots.append(re.sub(pattern, "", app_root_main))

    except (AttributeError, KeyError):
        pass  # Continue to next fallback

    return list(set(possible_roots))


def SelfCodeAgent(model:str = "gemini-2.0-flash-001"):
    return Agent(
        name="self_code",
        model=model,
        description=(
            "Agent to read it's own multiagent application code and help with debugging and understanding of running multi agent ADK application"
        ),
        instruction="""
            You are an agent that can access and analyze the source code of the application you are running within. You are expert programmer who specializes in python, LLMs and agentic app development.

            Important: Before attempting to read any code, ALWAYS use the 'autodiscover_possible_root_dir' tool to identify potential root directories. Present these options to the user and wait for confirmation before proceeding to read any files.

            User 'autodiscover_possible_root_dir' tool to find out possible directories where app code is stored.
            Use the 'get_my_application_code' tool when you need to see the application's source code to answer questions or understand its structure.
            Focus on explaining the code based on the user's query.

            Important: user has to confirm directory with code before calling get_my_application_code. If not specified in prompts, you must suggest possible paths(call autodiscover_possible_root_dir), but you can't decide on root on your own.
            If not specified by user, call get_my_application_code with only_py_files=True. Let them know you done it.
            Do not require any additional confirmations just to show all possible root dirs.

            when returning results from autodiscover_possible_root_dir return list enumerated.
            if reading files fails due to exceeding limit of allowed files, you can ask user if they want to run it again with increased param.

            Important, in most scenarios you prefer to not get_my_application_code multiple times. For any subsequential call you need to confirm it with user. **YOU MUST AVOID REDUNDANT CALLS. Prioritize using the information from PREVIOUS get_my_application_code TOOL CALLS. Only call get_my_application_code if ABSOLUTELY necessary and you don't already have the required information.**    
            """,
        tools=[get_my_application_code, autodiscover_possible_root_dir],
    )

# uncomment if you want to via: uv run adk web
#root_agent = SelfCodeAgent()