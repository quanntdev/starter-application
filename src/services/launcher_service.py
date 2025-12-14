"""Launcher service for starting apps and URLs."""
import os
import subprocess
from pathlib import Path


class LauncherService:
    """Service for launching apps and browser URLs."""
    
    def __init__(self):
        pass
    
    def _resolve_lnk(self, lnk_path: str) -> str:
        """
        Resolve .lnk file to get the actual executable path using PowerShell.
        
        Args:
            lnk_path: Path to the .lnk shortcut file
            
        Returns:
            Path to the executable, or original path if resolution fails
        """
        try:
            # Use PowerShell to resolve .lnk file
            ps_command = f'''
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut("{lnk_path}")
            $shortcut.TargetPath
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                return lnk_path
        except Exception as e:
            print(f"Error resolving .lnk file {lnk_path}: {e}")
            return lnk_path
    
    def launch_app(self, lnk_path: str):
        """
        Launch an app from .lnk file.
        
        Args:
            lnk_path: Path to the .lnk shortcut file
        """
        try:
            print(f"Attempting to launch app from: {lnk_path}")
            
            # Check if file exists
            if not os.path.exists(lnk_path):
                print(f"File not found: {lnk_path}")
                # Try to resolve .lnk to see if target exists
                resolved = self._resolve_lnk(lnk_path)
                if resolved != lnk_path and os.path.exists(resolved):
                    print(f"Resolved path exists, trying to launch: {resolved}")
                    try:
                        os.startfile(resolved)
                        return True
                    except Exception as e:
                        print(f"Error launching resolved path: {e}")
                return False
            
            # Use os.startfile on Windows to open .lnk files
            print(f"Launching .lnk file: {lnk_path}")
            os.startfile(lnk_path)
            print(f"Successfully launched: {lnk_path}")
            return True
        except Exception as e:
            print(f"Error launching app {lnk_path}: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: try to resolve and launch executable directly
            try:
                print(f"Trying fallback: resolve and launch executable")
                exe_path = self._resolve_lnk(lnk_path)
                if exe_path != lnk_path and os.path.exists(exe_path):
                    print(f"Launching resolved executable: {exe_path}")
                    os.startfile(exe_path)
                    return True
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
            
            return False
    
    def launch_browser_urls(self, browser_lnk: str, urls: list):
        """
        Launch browser with multiple URLs.
        
        Args:
            browser_lnk: Path to browser .lnk file
            urls: List of URLs to open
        """
        if not urls:
            return False
        
        try:
            # Resolve .lnk file to get executable path
            exe_path = self._resolve_lnk(browser_lnk)
            
            # Check if resolved path exists and is an executable
            if not os.path.exists(exe_path) or not (exe_path.lower().endswith('.exe') or exe_path.lower().endswith('.lnk')):
                print(f"Resolved path invalid: {exe_path}, trying direct launch")
                # Try launching browser first, then URLs
                try:
                    os.startfile(browser_lnk)
                    import time
                    time.sleep(0.3)  # Wait for browser to start
                except Exception as e:
                    print(f"Error launching browser: {e}")
                
                # Open URLs - browser should handle them
                success_count = 0
                for url in urls:
                    try:
                        os.startfile(url)
                        success_count += 1
                        time.sleep(0.1)  # Small delay between URLs
                    except Exception as e:
                        print(f"Error opening URL {url}: {e}")
                return success_count > 0
            
            # Launch browser with URLs
            # Strategy: Launch browser first, then open URLs
            import time
            
            # First, launch browser (if not already running, this will start it)
            try:
                # Launch browser with first URL to ensure it starts
                subprocess.Popen(
                    [exe_path, urls[0]],
                    shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                success_count = 1
                time.sleep(0.3)  # Wait for browser to start
                
                # Open remaining URLs
                for url in urls[1:]:
                    try:
                        # For subsequent URLs, pass as argument to browser
                        subprocess.Popen(
                            [exe_path, url],
                            shell=False,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        success_count += 1
                        time.sleep(0.1)  # Small delay between URLs
                    except Exception as e:
                        # Fallback: try using os.startfile with URL directly
                        try:
                            print(f"Trying fallback for URL {url}: {e}")
                            os.startfile(url)
                            success_count += 1
                        except Exception as e2:
                            print(f"Error launching URL {url}: {e2}")
            except Exception as e:
                # If launching with exe fails, try fallback
                print(f"Error launching browser with exe: {e}")
                try:
                    # Launch browser first
                    os.startfile(browser_lnk)
                    time.sleep(0.3)
                    # Then open URLs
                    success_count = 0
                    for url in urls:
                        try:
                            os.startfile(url)
                            success_count += 1
                            time.sleep(0.1)
                        except Exception as e2:
                            print(f"Error opening URL {url}: {e2}")
                except Exception as e2:
                    print(f"Error in fallback: {e2}")
                    return False
            
            return success_count > 0
        except Exception as e:
            print(f"Error launching browser URLs: {e}")
            # Final fallback: try opening URLs directly
            try:
                success_count = 0
                for url in urls:
                    try:
                        os.startfile(url)
                        success_count += 1
                        import time
                        time.sleep(0.1)
                    except Exception as e2:
                        print(f"Error in fallback URL launch {url}: {e2}")
                return success_count > 0
            except Exception as e2:
                print(f"Error in fallback URL launch: {e2}")
                return False
    
    def test_favourite(self, favourite):
        """
        Test launch a favourite (app or browser with URLs).
        
        Args:
            favourite: Favourite object
        """
        if favourite.kind == "browser" and favourite.browser_links:
            return self.launch_browser_urls(favourite.lnk_path, favourite.browser_links)
        else:
            return self.launch_app(favourite.lnk_path)

