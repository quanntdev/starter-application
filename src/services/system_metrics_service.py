"""Service for monitoring system metrics (CPU, RAM) and running applications."""
import psutil
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import deque
import time


class RunningAppInfo:
    """Information about a running application window."""
    
    def __init__(self, name: str, process_name: str, pid: int):
        self.name = name
        self.process_name = process_name
        self.pid = pid
        self.memory_usage = None  # In MB
        self.cpu_percent = None


class SystemMetricsService:
    """Service for monitoring system metrics and running applications."""
    
    # Store metrics history (timestamp, cpu%, ram%)
    MAX_HISTORY_MINUTES = 60
    
    def __init__(self):
        self.metrics_history = deque(maxlen=60)  # Store up to 60 data points (1 hour)
        self._last_update = None
        self._update_interval = 60  # Update every 60 seconds
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'ram_percent': memory.percent,
            'ram_used_gb': memory.used / (1024 ** 3),
            'ram_total_gb': memory.total / (1024 ** 3),
            'timestamp': datetime.now()
        }
    
    def update_metrics_history(self):
        """Update metrics history with current data."""
        current = self.get_current_metrics()
        
        # Add to history
        self.metrics_history.append({
            'timestamp': current['timestamp'],
            'cpu': current['cpu_percent'],
            'ram': current['ram_percent']
        })
        
        self._last_update = datetime.now()
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict]:
        """
        Get metrics history for the specified number of minutes.
        
        Args:
            minutes: Number of minutes of history to retrieve (default 60)
            
        Returns:
            List of dicts with timestamp, cpu, ram
        """
        # If history is empty or outdated, collect current metrics
        if not self.metrics_history or \
           (self._last_update and (datetime.now() - self._last_update).seconds > self._update_interval):
            self.update_metrics_history()
        
        # Return the requested history
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            m for m in self.metrics_history 
            if m['timestamp'] >= cutoff_time
        ]
    
    def get_running_windows(self) -> List[RunningAppInfo]:
        """
        Get list of running application windows (visible on taskbar).
        
        Returns:
            List of RunningAppInfo objects
        """
        apps = []
        seen_pids = set()
        
        try:
            # Use PowerShell to get visible windows
            ps_script = """
            Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | 
            Select-Object ProcessName, MainWindowTitle, Id | 
            ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    processes = json.loads(result.stdout)
                    
                    # Handle single process (not a list)
                    if isinstance(processes, dict):
                        processes = [processes]
                    
                    # Get process details using psutil
                    for proc_info in processes:
                        try:
                            pid = proc_info['Id']
                            if pid in seen_pids:
                                continue
                            
                            seen_pids.add(pid)
                            
                            app = RunningAppInfo(
                                name=proc_info.get('MainWindowTitle', 'Unknown'),
                                process_name=proc_info.get('ProcessName', 'Unknown'),
                                pid=pid
                            )
                            
                            # Get memory and CPU info from psutil
                            try:
                                process = psutil.Process(pid)
                                memory_info = process.memory_info()
                                app.memory_usage = memory_info.rss / (1024 * 1024)  # Convert to MB
                                app.cpu_percent = process.cpu_percent(interval=0.1)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                            
                            apps.append(app)
                        except (KeyError, ValueError) as e:
                            continue
                
                except json.JSONDecodeError as e:
                    print(f"Error parsing PowerShell JSON output: {e}")
        
        except subprocess.TimeoutExpired:
            print("Timeout getting running windows")
        except Exception as e:
            print(f"Error getting running windows: {e}")
        
        # Sort by name
        apps.sort(key=lambda x: x.name.lower())
        
        return apps
    
    def get_system_info(self) -> Dict:
        """Get general system information."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Format uptime
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = ""
        if days > 0:
            uptime_str += f"{days}d "
        if hours > 0:
            uptime_str += f"{hours}h "
        uptime_str += f"{minutes}m"
        
        return {
            'boot_time': boot_time,
            'uptime': uptime_str,
            'cpu_count': psutil.cpu_count(),
            'total_processes': len(psutil.pids())
        }
    
    def kill_process(self, pid: int) -> bool:
        """
        Kill a process by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait up to 3 seconds for graceful termination
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                # Force kill if still running
                process.kill()
            
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error killing process {pid}: {e}")
            return False

