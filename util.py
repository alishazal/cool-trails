import os

def list_files_and_folders(path):
    """Lists all files and folders in a given directory.

    Args:
        path: The path to the directory.
    """
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return []

    ret = []
    items = os.listdir(path)
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            ret.append(f"File: {item}")
        elif os.path.isdir(full_path):
            ret.append(f"Folder: {item}")
        else:
            ret.append(f"Other: {item}")
