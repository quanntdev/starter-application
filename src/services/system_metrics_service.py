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
        
        # Network speed tracking
        self._last_net_io = None
        self._last_net_time = None
        self._download_speeds = deque(maxlen=3)  # For smoothing
        self._upload_speeds = deque(maxlen=3)  # For smoothing
        self._cpu_samples = deque(maxlen=3)  # For smoothing
        self._ram_samples = deque(maxlen=3)  # For smoothing
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics with smoothing."""
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        
        # Add to smoothing samples
        self._cpu_samples.append(cpu_percent)
        self._ram_samples.append(memory.percent)
        
        # Calculate smoothed values (average of last 3 samples)
        cpu_smoothed = sum(self._cpu_samples) / len(self._cpu_samples) if self._cpu_samples else cpu_percent
        ram_smoothed = sum(self._ram_samples) / len(self._ram_samples) if self._ram_samples else memory.percent
        
        return {
            'cpu_percent': cpu_smoothed,
            'ram_percent': ram_smoothed,
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
        
        # Format uptime as "xh ym"
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{hours}h {minutes}m"
        
        return {
            'boot_time': boot_time,
            'uptime': uptime_str,
            'cpu_count': psutil.cpu_count(),
            'total_processes': len(psutil.pids())
        }
    
    def get_disk_metrics(self) -> Dict:
        """Get disk metrics for system drive."""
        try:
            import platform
            if platform.system() == 'Windows':
                # Get system drive (usually C:)
                disk = psutil.disk_usage('C:\\')
            else:
                disk = psutil.disk_usage('/')
            
            used_gb = disk.used / (1024 ** 3)
            total_gb = disk.total / (1024 ** 3)
            free_gb = disk.free / (1024 ** 3)
            percent_used = (disk.used / disk.total) * 100
            
            return {
                'used_gb': used_gb,
                'total_gb': total_gb,
                'free_gb': free_gb,
                'percent_used': percent_used
            }
        except Exception as e:
            print(f"Error getting disk metrics: {e}")
            return {
                'used_gb': 0,
                'total_gb': 0,
                'free_gb': 0,
                'percent_used': 0
            }
    
    def get_network_metrics(self) -> Dict:
        """Get network status and speed metrics."""
        try:
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            # Get network interfaces
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            # Determine connection status and type
            is_connected = False
            connection_type = "Network"
            
            for interface_name, addrs in net_if_addrs.items():
                if interface_name in net_if_stats:
                    stats = net_if_stats[interface_name]
                    if stats.isup:
                        is_connected = True
                        # Try to determine connection type
                        if 'Wi-Fi' in interface_name or 'WLAN' in interface_name:
                            connection_type = "Wi-Fi"
                        elif 'Ethernet' in interface_name or 'LAN' in interface_name:
                            connection_type = "Ethernet"
                        break
            
            # Calculate network speed
            download_speed = 0.0
            upload_speed = 0.0
            
            if self._last_net_io and self._last_net_time:
                time_diff = current_time - self._last_net_time
                if time_diff > 0:
                    bytes_recv_diff = net_io.bytes_recv - self._last_net_io.bytes_recv
                    bytes_sent_diff = net_io.bytes_sent - self._last_net_io.bytes_sent
                    
                    download_speed = bytes_recv_diff / time_diff  # bytes per second
                    upload_speed = bytes_sent_diff / time_diff  # bytes per second
                    
                    # Add to smoothing samples
                    self._download_speeds.append(download_speed)
                    self._upload_speeds.append(upload_speed)
                    
                    # Calculate smoothed values
                    if self._download_speeds:
                        download_speed = sum(self._download_speeds) / len(self._download_speeds)
                    if self._upload_speeds:
                        upload_speed = sum(self._upload_speeds) / len(self._upload_speeds)
            
            # Update last values
            self._last_net_io = net_io
            self._last_net_time = current_time
            
            return {
                'is_connected': is_connected,
                'connection_type': connection_type,
                'download_speed_bps': download_speed,
                'upload_speed_bps': upload_speed
            }
        except Exception as e:
            print(f"Error getting network metrics: {e}")
            return {
                'is_connected': False,
                'connection_type': 'Network',
                'download_speed_bps': 0.0,
                'upload_speed_bps': 0.0
            }
    
    def get_battery_metrics(self) -> Dict:
        """Get battery metrics if available."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {
                    'has_battery': False,
                    'percent': None,
                    'is_charging': None
                }
            
            return {
                'has_battery': True,
                'percent': battery.percent,
                'is_charging': battery.power_plugged is False  # True if on battery
            }
        except Exception as e:
            print(f"Error getting battery metrics: {e}")
            return {
                'has_battery': False,
                'percent': None,
                'is_charging': None
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

