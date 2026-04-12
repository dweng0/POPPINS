def is_package_installed(package_name: str) -> bool:
    """Determines if a specific Python package is currently available in the execution environment."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False