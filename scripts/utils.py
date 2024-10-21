import os

def get_latest_version(objDir):
    """
    Looks for the highest version folder in the specified directory
    that starts with 'v' followed by an integer, and returns the 
    full path of that folder.

    Parameters:
    objDir (str): The path to the directory to search for version folders.

    Returns:
    str: The full path of the highest version folder, or None if no such folder exists.
    """
    # Ensure the directory exists
    if not os.path.isdir(objDir):
        raise ValueError(f"The directory '{objDir}' does not exist.")
    
    latest_version = None
    latest_version_path = None

    # Iterate through items in the directory
    for item in os.listdir(objDir):
        item_path = os.path.join(objDir, item)
        
        # Check if it's a directory and starts with 'v' followed by an integer
        if os.path.isdir(item_path) and item.startswith('v'):
            try:
                # Extract the version number by converting the substring after 'v' to an integer
                version_number = int(item[1:])
                
                # Update latest version if this one is greater
                if latest_version is None or version_number > latest_version:
                    latest_version = version_number
                    latest_version_path = item_path
            except ValueError:
                # If conversion fails, continue to the next item
                continue

    return latest_version_path
