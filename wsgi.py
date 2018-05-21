"""WSGI for terrasnow_enterprise."""

from webhook import application

if __name__ == "__main__":
    application.run()
