from typing import List, Set, Any

# Define the expected interface for the filesystem object (for type hinting)
class FilesystemInterface(Any):
    """Defines the minimum required methods for a filesystem implementation."""
    def traverse(self) -> List[str]:
        """Recursively traverses and returns a flat list of all file paths found.
        This method is mocked in tests but required for the structure to pass type checks if implemented properly.
        """
        raise NotImplementedError

# --- Helper Unit ---
def _is_excluded(path: str, excluded_dirs: Set[str]) -> bool:
    """Checks if a given file or directory path matches any of the predefined exclusion patterns.
    The comparison is done based on prefixes matching the exclusion list.
    """
    for excluded in excluded_dirs:
        # Check if the path starts with the excluded directory name followed by a separator
        if path.startswith(excluded + '/'):
            return True
        # Also check for exact matches if the path itself is an exclusion (e.g., if we are checking the root)
        if path == excluded:
             return True
    return False

# --- Main Unit ---
def list_files(path: str, excluded_dirs: Set[str], fs: FilesystemInterface) -> List[str]:
    """Recursively traverses a directory and returns a flat list of all file paths,
    excluding specified directories.

    Args:
        path (str): The starting path to traverse.
        excluded_dirs (Set[str]): A set of directory names/prefixes to exclude (e.g., {'.git', 'node_modules'}).
        fs (FilesystemInterface): An object implementing filesystem operations.

    Returns:
        List[str]: A flat list of file paths that are not excluded.
    """
    all_paths = fs.traverse()
    filtered_files = []

    for full_path in all_paths:
        # Assuming the structure returned by traverse() is relative to the starting point (path)
        # We need to check if any part of the path matches an exclusion pattern.
        
        is_excluded_path = False
        current_path_parts = full_path.split('/')

        for part in current_path_parts:
            if part in excluded_dirs:
                # If any directory component matches the exclusion list, skip the file.
                is_excluded_path = True
                break
        
        if not is_excluded_path:
            filtered_files.append(full_path)

    return filtered_files
