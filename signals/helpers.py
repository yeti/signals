import os.path
import glob


def recursively_find_parent_containing_file(current_path, search_files):
    # Convert to absolute path, in case we received relative path
    current_path = os.path.abspath(current_path)
    while current_path != os.sep:
        for current_file in search_files:
            # Check if this path has any of the files we're looking for
            if len(glob.glob(current_path + os.sep + current_file)) > 0:
                return current_path, current_file

        current_path = os.path.normpath(os.path.join(current_path, ".."))

    return None, None
