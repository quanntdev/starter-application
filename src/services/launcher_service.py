"""Launcher service for starting apps and URLs."""
import os
import subprocess
import ctypes
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
    
    def _launch_with_normal_user(self, target_path: str) -> bool:
        """
        Launch a file/app with normal user privileges using Windows ShellExecute.
        This ensures the app runs with the current user's token, not admin.
        
        Args:
            target_path: Path to file or executable to launch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use ShellExecuteW with "open" operation (not "runas")
            # This ensures the app runs with normal user privileges
            result = ctypes.windll.shell32.ShellExecuteW(
                None,           # hwnd
                "open",         # lpOperation - open (not runas)
                target_path,    # lpFile
                None,           # lpParameters
                None,           # lpDirectory
                1               # nShowCmd - SW_SHOWNORMAL
            )
            # ShellExecuteW returns > 32 on success
            return result > 32
        except Exception as e:
            print(f"Error launching with ShellExecute: {e}")
            return False
    
    def launch_app(self, lnk_path: str):
        """
        Launch an app from .lnk file with normal user privileges (not admin).
        Uses Windows ShellExecute API to ensure the app runs with normal user privileges,
        preventing inheritance of admin privileges from parent process.
        
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
                    # Use ShellExecute to launch with normal user privileges
                    if self._launch_with_normal_user(resolved):
                        print(f"Successfully launched resolved path: {resolved}")
                        return True
                    else:
                        # Fallback: try os.startfile
                        try:
                            os.startfile(resolved)
                            return True
                        except Exception as e2:
                            print(f"Fallback also failed: {e2}")
                return False
            
            # Use ShellExecute to launch .lnk file with normal user privileges
            # ShellExecute with "open" operation runs with current user token, not admin
            print(f"Launching .lnk file: {lnk_path}")
            if self._launch_with_normal_user(lnk_path):
                print(f"Successfully launched: {lnk_path}")
                return True
            else:
                # Fallback: try os.startfile
                try:
                    os.startfile(lnk_path)
                    print(f"Launched via os.startfile: {lnk_path}")
                    return True
                except Exception as e:
                    print(f"os.startfile also failed: {e}")
                    return False
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
                    # Try ShellExecute first
                    if self._launch_with_normal_user(exe_path):
                        return True
                    # If ShellExecute fails, try os.startfile
                    try:
                        os.startfile(exe_path)
                        return True
                    except:
                        # Last resort: subprocess
                        subprocess.Popen(
                            [exe_path],
                            shell=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        return True
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
            
            return False
    
    def launch_browser_urls(self, browser_lnk: str, urls: list):
        """
        Launch browser with multiple URLs, opening each URL in a new tab.
        
        Args:
            browser_lnk: Path to browser .lnk file
            urls: List of URLs to open
        """
        if not urls:
            return False
        
        try:
            import time
            
            print(f"Launching browser with {len(urls)} URLs: {urls}")
            
            # Strategy: Launch browser with first URL, then open remaining URLs using ShellExecuteW
            # ShellExecuteW with "open" verb will open each URL in a new tab of the running browser
            
            # Step 1: Launch browser with first URL to ensure it starts
            # Resolve .lnk file to get executable path
            exe_path = self._resolve_lnk(browser_lnk)
            
            print(f"Resolved browser path: {exe_path}")
            
            # Launch browser with first URL
            if os.path.exists(exe_path) and exe_path.lower().endswith('.exe'):
                # Launch browser executable with first URL
                print(f"Launching browser with first URL: {urls[0]}")
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,           # hwnd
                    "open",         # lpOperation
                    exe_path,       # lpFile - browser executable
                    urls[0],        # lpParameters - first URL as argument
                    None,           # lpDirectory
                    1               # nShowCmd - SW_SHOWNORMAL
                )
                if result <= 32:
                    print(f"Failed to launch browser with first URL. Error code: {result}")
                    # Fallback: try launching .lnk directly
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None, "open", browser_lnk, None, None, 1
                    )
                    if result <= 32:
                        print(f"Failed to launch browser .lnk. Error code: {result}")
                        return False
            else:
                # Launch .lnk file directly
                print(f"Launching browser .lnk: {browser_lnk}")
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, "open", browser_lnk, None, None, 1
                )
                if result <= 32:
                    print(f"Failed to launch browser .lnk. Error code: {result}")
                    return False
                # Open first URL separately
                print(f"Opening first URL: {urls[0]}")
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, "open", urls[0], None, None, 1
                )
                if result <= 32:
                    print(f"Failed to open first URL. Error code: {result}")
            
            # Wait for browser to fully start before opening additional URLs
            print("Waiting for browser to start...")
            time.sleep(1.0)  # Increased delay to ensure browser is ready
            
            # Step 2: Open remaining URLs - each will open in a new tab
            success_count = 1  # First URL already opened
            for i, url in enumerate(urls[1:], start=2):
                try:
                    print(f"Opening URL {i}/{len(urls)}: {url}")
                    # Use ShellExecuteW with "open" verb - this will open URL in a new tab
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None,           # hwnd
                        "open",         # lpOperation
                        url,            # lpFile - URL to open
                        None,           # lpParameters
                        None,           # lpDirectory
                        1               # nShowCmd - SW_SHOWNORMAL
                    )
                    
                    if result > 32:
                        print(f"✅ Successfully opened URL {i}: {url}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to open URL {i}: {url}. Error code: {result}")
                    
                    # Small delay between URLs to avoid overwhelming the browser
                    if i < len(urls):  # Don't delay after the last one
                        time.sleep(0.3)
                except Exception as e:
                    print(f"❌ Error opening URL {url}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"Successfully opened {success_count}/{len(urls)} URLs")
            return success_count > 0
            
        except Exception as e:
            print(f"Error launching browser URLs: {e}")
            import traceback
            traceback.print_exc()
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

