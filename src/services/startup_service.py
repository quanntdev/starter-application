"""Startup service for Windows autostart via Task Scheduler."""
import subprocess
import sys
import os
from pathlib import Path


class StartupService:
    """Service for managing Windows autostart via Task Scheduler."""
    
    TASK_NAME = "StarterAppLauncher_AutoStart"
    
    def __init__(self):
        pass
    
    def is_enabled(self) -> bool:
        """
        Check if autostart is enabled.
        
        Returns:
            True if autostart task exists and is enabled
        """
        try:
            result = subprocess.run(
                ["schtasks", "/Query", "/TN", self.TASK_NAME],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error checking autostart status: {e}")
            return False
    
    def enable(self) -> bool:
        """
        Enable autostart by creating a Task Scheduler task.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get executable path - handle both frozen and development mode
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - use the exe directly
                exe_path = sys.executable
                task_command = f'"{exe_path}"'
            else:
                # Running as Python script
                main_script = Path(__file__).parent.parent / "app" / "main.py"
                if not main_script.exists():
                    print(f"Main script not found: {main_script}")
                    return False
                
                # Use pythonw to avoid console window
                python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(python_exe):
                    python_exe = sys.executable
                
                task_command = f'"{python_exe}" "{main_script}"'
            
            print(f"Creating autostart task with command: {task_command}")
            
            # Create scheduled task
            # /SC ONLOGON: Run at logon
            # /RL HIGHEST: Run with highest privileges
            # /F: Force create (overwrite if exists)
            
            command = [
                "schtasks",
                "/Create",
                "/TN", self.TASK_NAME,
                "/TR", task_command,
                "/SC", "ONLOGON",
                "/RL", "HIGHEST",
                "/F"
            ]
            
            print(f"Running command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                print(f"Autostart enabled successfully")
                print(f"Task output: {result.stdout}")
                return True
            else:
                print(f"Failed to enable autostart")
                print(f"Return code: {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error enabling autostart: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def disable(self) -> bool:
        """
        Disable autostart by deleting the Task Scheduler task.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["schtasks", "/Delete", "/TN", self.TASK_NAME, "/F"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                print(f"Autostart disabled successfully")
                return True
            else:
                print(f"Failed to disable autostart: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error disabling autostart: {e}")
            return False

