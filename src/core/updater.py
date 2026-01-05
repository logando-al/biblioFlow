"""
Auto-Update Module for BiblioFlow

Handles checking for updates from GitHub Releases and performing
self-update on Windows via batch script.
"""
import os
import sys
import tempfile
import subprocess
import requests
from packaging import version

from .version import __version__, GITHUB_API_URL, APP_NAME


class UpdateChecker:
    """Checks for and applies updates from GitHub Releases."""

    def __init__(self):
        self.current_version = __version__
        self.latest_version = None
        self.download_url = None
        self.release_notes = None

    def check_for_updates(self) -> bool:
        """
        Check GitHub Releases API for newer version.
        
        Returns:
            bool: True if update available, False otherwise
        """
        try:
            response = requests.get(
                GITHUB_API_URL,
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Extract version from tag (e.g., "v0.2.0" -> "0.2.0")
            tag = data.get("tag_name", "")
            self.latest_version = tag.lstrip("v")
            self.release_notes = data.get("body", "")

            # Find Windows exe asset
            assets = data.get("assets", [])
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    self.download_url = asset["browser_download_url"]
                    break

            # Compare versions
            if self.latest_version and self.download_url:
                return version.parse(self.latest_version) > version.parse(self.current_version)

        except Exception as e:
            print(f"Update check failed: {e}")

        return False

    def download_update(self, progress_callback=None) -> str:
        """
        Download the latest release executable.
        
        Args:
            progress_callback: Optional callback(downloaded, total) for progress
            
        Returns:
            str: Path to downloaded file, or None on failure
        """
        if not self.download_url:
            return None

        try:
            response = requests.get(self.download_url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            
            # Download to temp file
            temp_dir = tempfile.gettempdir()
            filename = f"{APP_NAME}-v{self.latest_version}-win64.exe"
            download_path = os.path.join(temp_dir, filename)

            downloaded = 0
            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            return download_path

        except Exception as e:
            print(f"Download failed: {e}")
            return None

    def apply_update(self, new_exe_path: str) -> bool:
        """
        Apply update by creating a batch script that:
        1. Waits for current process to exit
        2. Replaces the old exe with new exe
        3. Relaunches the application
        
        Args:
            new_exe_path: Path to the downloaded new executable
            
        Returns:
            bool: True if update script was launched successfully
        """
        if not os.path.exists(new_exe_path):
            return False

        # Get current executable path
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            # Running from source - can't auto-update
            print("Auto-update only works with packaged executable")
            return False

        # Create update batch script
        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, "biblioflow_update.bat")

        batch_script = f'''@echo off
title {APP_NAME} Updater
echo Updating {APP_NAME} to v{self.latest_version}...
echo.
echo Waiting for application to close...

:waitloop
tasklist /FI "PID eq {os.getpid()}" 2>NUL | find /I "{os.getpid()}" >NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >NUL
    goto waitloop
)

echo Application closed. Applying update...
timeout /t 1 /nobreak >NUL

echo Replacing executable...
copy /Y "{new_exe_path}" "{current_exe}"
if %ERRORLEVEL% NEQ 0 (
    echo Update failed! Could not replace executable.
    echo Please download manually from GitHub.
    pause
    exit /b 1
)

echo Update successful!
echo Starting {APP_NAME}...
start "" "{current_exe}"

echo Cleaning up...
del "{new_exe_path}" 2>NUL
del "%~f0" 2>NUL
'''

        try:
            with open(batch_path, "w") as f:
                f.write(batch_script)

            # Launch the batch script (detached)
            subprocess.Popen(
                ["cmd", "/c", batch_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                close_fds=True
            )

            return True

        except Exception as e:
            print(f"Failed to launch updater: {e}")
            return False


def check_for_updates_on_startup():
    """
    Convenience function to check for updates.
    Returns tuple of (has_update, checker_instance)
    """
    checker = UpdateChecker()
    has_update = checker.check_for_updates()
    return has_update, checker
