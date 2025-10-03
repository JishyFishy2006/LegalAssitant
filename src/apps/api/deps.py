"""Dependencies for the API."""

from typing import Dict

# Global components (loaded at startup)
app_components = {}


def get_app_components() -> Dict:
    """Dependency to get app components."""
    return app_components


def set_app_components(components: Dict):
    """Set app components (used during startup)."""
    global app_components
    app_components = components