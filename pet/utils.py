import os


def environment_callback(request):
    """
    Callback function for Unfold admin to show environment badge.
    Returns environment name and color based on DEBUG setting.
    """
    debug = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

    if debug:
        return ["Development", "danger"]  # Red badge for development
    else:
        return ["Production", "success"]  # Green badge for production
