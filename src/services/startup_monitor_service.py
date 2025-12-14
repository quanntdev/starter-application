"""Service for monitoring startup applications and running processes."""
import subprocess
import os
import winreg
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class StartupAppInfo:
    """Information about a startup application."""
    
    def __init__(self, name: str, source: str, path: str = "", status: str = "unknown"):
        self.name = name
        self.source = source  # registry, task_scheduler, startup_folder, etc.
        self.path = path
        self.status = status  # running, stopped, error
        self.process_id = None
        self.memory_usage = None
        self.start_time = None


class StartupMonitorService:
    """Service for monitoring startup applications."""
    
    def __init__(self):
        pass
    
    def get_startup_apps(self) -> List[StartupAppInfo]:
        """
        Get list of applications configured to start with Windows.
        
        Returns:
            List of StartupAppInfo objects
        """
        apps = []
        
        # 1. Registry Run keys
        apps.extend(self._get_registry_startup_apps())
        
        # 2. Startup folders
        apps.extend(self._get_startup_folder_apps())
        
        # 3. Task Scheduler startup tasks
        apps.extend(self._get_scheduled_tasks())
        
        # Update running status
        self._update_running_status(apps)
        
        return apps
    
    def _get_registry_startup_apps(self) -> List[StartupAppInfo]:
        """Get apps from Windows Registry Run keys."""
        apps = []
        
        # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    apps.append(StartupAppInfo(
                        name=name,
                        source="Registry (User)",
                        path=value
                    ))
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading user registry: {e}")
        
        # HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    apps.append(StartupAppInfo(
                        name=name,
                        source="Registry (System)",
                        path=value
                    ))
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading system registry: {e}")
        
        return apps
    
    def _get_startup_folder_apps(self) -> List[StartupAppInfo]:
        """Get apps from Startup folders."""
        apps = []
        
        # User Startup folder
        user_startup = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if user_startup.exists():
            for item in user_startup.iterdir():
                if item.suffix == ".lnk":
                    apps.append(StartupAppInfo(
                        name=item.stem,
                        source="Startup Folder (User)",
                        path=str(item)
                    ))
        
        # All Users Startup folder
        all_users_startup = Path(os.getenv("PROGRAMDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if all_users_startup.exists():
            for item in all_users_startup.iterdir():
                if item.suffix == ".lnk":
                    apps.append(StartupAppInfo(
                        name=item.stem,
                        source="Startup Folder (All Users)",
                        path=str(item)
                    ))
        
        return apps
    
    def _get_scheduled_tasks(self) -> List[StartupAppInfo]:
        """Get apps from Task Scheduler (ONLOGON trigger)."""
        apps = []
        
        try:
            # Query tasks with ONLOGON trigger
            result = subprocess.run(
                ["schtasks", "/Query", "/FO", "LIST", "/V"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_task = None
                
                for i, line in enumerate(lines):
                    if line.startswith("TaskName:"):
                        task_name = line.split(":", 1)[1].strip()
                        # Check if it's a logon task
                        if i + 1 < len(lines):
                            next_lines = '\n'.join(lines[i:i+10])
                            if "ONLOGON" in next_lines or "At log on" in next_lines:
                                apps.append(StartupAppInfo(
                                    name=task_name,
                                    source="Task Scheduler",
                                    path=""
                                ))
        except Exception as e:
            print(f"Error reading scheduled tasks: {e}")
        
        return apps
    
    def _update_running_status(self, apps: List[StartupAppInfo]):
        """Update running status for each app."""
        try:
            # Get running processes
            result = subprocess.run(
                ["tasklist", "/FO", "CSV"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                running_processes = {}
                lines = result.stdout.split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split('","')
                        if len(parts) >= 2:
                            process_name = parts[0].strip('"')
                            pid = parts[1].strip('"')
                            memory = parts[4].strip('"') if len(parts) > 4 else "0"
                            running_processes[process_name.lower()] = {
                                'pid': pid,
                                'memory': memory
                            }
                
                # Match apps with running processes
                for app in apps:
                    app_name_lower = app.name.lower()
                    exe_name = Path(app.path).stem.lower() if app.path else ""
                    
                    # Try to match by name or executable
                    for proc_name, proc_info in running_processes.items():
                        if app_name_lower in proc_name or proc_name in app_name_lower or exe_name in proc_name:
                            app.status = "running"
                            app.process_id = proc_info['pid']
                            app.memory_usage = proc_info['memory']
                            break
                    else:
                        app.status = "stopped"
        except Exception as e:
            print(f"Error checking running status: {e}")
            for app in apps:
                app.status = "unknown"
    
    def get_system_info(self) -> Dict:
        """Get system information."""
        info = {
            "boot_time": None,
            "uptime": None,
            "total_processes": 0,
            "startup_apps_count": 0
        }
        
        try:
            # Get system uptime
            result = subprocess.run(
                ["systeminfo"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "System Boot Time" in line:
                        info["boot_time"] = line.split(":", 1)[1].strip()
                    elif "System Up Time" in line:
                        info["uptime"] = line.split(":", 1)[1].strip()
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return info
    
    def kill_process(self, process_id: str) -> bool:
        """
        Kill a process by its PID.
        
        Args:
            process_id: Process ID as string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["taskkill", "/F", "/PID", process_id],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                print(f"Successfully killed process {process_id}")
                return True
            else:
                print(f"Failed to kill process {process_id}: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error killing process {process_id}: {e}")
            return False
    
    def remove_from_startup(self, app_info: StartupAppInfo) -> bool:
        """
        Remove an app from Windows startup.
        
        Args:
            app_info: StartupAppInfo object with name, source, and path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "Registry (User)" in app_info.source:
                # Remove from HKEY_CURRENT_USER
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE
                )
                try:
                    winreg.DeleteValue(key, app_info.name)
                    winreg.CloseKey(key)
                    print(f"Removed {app_info.name} from user registry")
                    return True
                except FileNotFoundError:
                    winreg.CloseKey(key)
                    print(f"Value {app_info.name} not found in user registry")
                    return False
                except Exception as e:
                    winreg.CloseKey(key)
                    print(f"Error removing from user registry: {e}")
                    return False
            
            elif "Registry (System)" in app_info.source:
                # Remove from HKEY_LOCAL_MACHINE (requires admin)
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE
                )
                try:
                    winreg.DeleteValue(key, app_info.name)
                    winreg.CloseKey(key)
                    print(f"Removed {app_info.name} from system registry")
                    return True
                except FileNotFoundError:
                    winreg.CloseKey(key)
                    print(f"Value {app_info.name} not found in system registry")
                    return False
                except PermissionError:
                    winreg.CloseKey(key)
                    print(f"Permission denied - need admin rights for system registry")
                    return False
                except Exception as e:
                    winreg.CloseKey(key)
                    print(f"Error removing from system registry: {e}")
                    return False
            
            elif "Startup Folder" in app_info.source:
                # Remove from Startup folder
                if app_info.path:
                    try:
                        path = Path(app_info.path)
                        if path.exists():
                            path.unlink()
                            print(f"Removed {app_info.name} from startup folder")
                            return True
                        else:
                            print(f"File not found: {app_info.path}")
                            return False
                    except Exception as e:
                        print(f"Error removing from startup folder: {e}")
                        return False
            
            elif "Task Scheduler" in app_info.source:
                # Remove from Task Scheduler
                try:
                    result = subprocess.run(
                        ["schtasks", "/Delete", "/TN", app_info.name, "/F"],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if result.returncode == 0:
                        print(f"Removed {app_info.name} from Task Scheduler")
                        return True
                    else:
                        print(f"Failed to remove task: {result.stderr}")
                        return False
                except Exception as e:
                    print(f"Error removing from Task Scheduler: {e}")
                    return False
            
            return False
        except Exception as e:
            print(f"Error removing from startup: {e}")
            return False

