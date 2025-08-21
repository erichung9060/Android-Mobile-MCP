from fastmcp import FastMCP
from fastmcp.utilities.types import Image
import xml.etree.ElementTree as ET
import json
import io
import subprocess
import re
import tempfile
import os
from PIL import Image as PILImage

mcp = FastMCP("Android Mobile MCP Server")

class ADBDevice:
    """ADB-based device controller using native adb commands"""
    
    def __init__(self):
        self._adb_checked = False
        self._adb_available = False
    
    def _ensure_adb_available(self):
        """Check if adb is available on first use"""
        if not self._adb_checked:
            try:
                subprocess.run(["adb", "version"], check=True, capture_output=True)
                self._adb_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._adb_available = False
            self._adb_checked = True
        
        if not self._adb_available:
            raise RuntimeError("ADB is not installed or not in PATH")
    
    def _run_adb_command(self, cmd, check=True):
        """Run an adb command and return the result"""
        self._ensure_adb_available()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ADB command failed: {e.stderr}")
    
    def dump_hierarchy(self):
        """Get UI hierarchy XML using adb uiautomator dump"""
        # Dump UI to device
        self._run_adb_command("adb shell uiautomator dump")
        
        # Pull the XML file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.xml', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            self._run_adb_command(f"adb pull /sdcard/window_dump.xml {tmp_path}")
            with open(tmp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            return xml_content
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def click(self, x, y):
        """Click on coordinates using adb input tap"""
        self._run_adb_command(f"adb shell input tap {x} {y}")
    
    def send_keys(self, text):
        """Send text using adb input text"""
        # Escape special characters for shell
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        self._run_adb_command(f"adb shell input text \"{escaped_text}\"")
    
    def press(self, key):
        """Press a key using adb input keyevent"""
        key_codes = {
            'back': 'KEYCODE_BACK',
            'home': 'KEYCODE_HOME', 
            'recent': 'KEYCODE_APP_SWITCH',
            'enter': 'KEYCODE_ENTER'
        }
        
        keycode = key_codes.get(key.lower(), f'KEYCODE_{key.upper()}')
        self._run_adb_command(f"adb shell input keyevent {keycode}")
    
    def shell(self, cmd):
        """Execute shell command via adb"""
        self._run_adb_command(f"adb shell {cmd}")
    
    def app_list(self):
        """List installed packages using adb"""
        output = self._run_adb_command("adb shell pm list packages -3")  # -3 for third party only
        packages = []
        for line in output.split('\n'):
            if line.startswith('package:'):
                package = line.replace('package:', '').strip()
                packages.append(package)
        return packages
    
    def app_start(self, package_name):
        """Start an app using adb am start"""
        # Try to start with monkey first (simpler)
        try:
            self._run_adb_command(f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        except RuntimeError:
            # Fallback to am start
            self._run_adb_command(f"adb shell am start -n {package_name}")
    
    def screenshot(self):
        """Take screenshot using adb screencap"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Take screenshot on device
            self._run_adb_command("adb shell screencap -p /sdcard/screenshot.png")
            # Pull screenshot
            self._run_adb_command(f"adb pull /sdcard/screenshot.png {tmp_path}")
            # Clean up device
            self._run_adb_command("adb shell rm /sdcard/screenshot.png")
            
            # Load and return PIL Image
            return PILImage.open(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

device = ADBDevice()
