import uiautomator2 as u2
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
import xml.etree.ElementTree as ET
import json
import io
import subprocess
import re

mcp = FastMCP("Android Mobile MCP Server")
device = u2.connect()

def parse_bounds(bounds_str):
    if not bounds_str or bounds_str == '':
        return None
    try:
        bounds = bounds_str.replace('[', '').replace(']', ',').split(',')
        x1, y1, x2, y2 = map(int, bounds[:4])
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return {"x": center_x, "y": center_y, "bounds": [x1, y1, x2, y2]}
    except:
        return None

def get_children_texts(element):
    child_texts = []
    """Check if element has any focusable children"""
    for child in list(element.iter())[1:]:
        child_text = child.get('text', '').strip()
        if child_text and child_text not in child_texts:
            child_texts.append(child_text)

    return child_texts

def extract_ui_elements(element):
    resource_id = element.get('resource-id', '')
    if resource_id.startswith('com.android.systemui'):
        return []
    
    text = element.get('text', '').strip()
    content_desc = element.get('content-desc', '').strip()
    hint = element.get('hint', '').strip()
    bounds = parse_bounds(element.get('bounds', ''))
    focusable = element.get('focusable', 'false').lower() == 'true'
    
    has_text = bool(text or content_desc or hint)
    
    children = []
    for child in element:
        children.extend(extract_ui_elements(child))

    if not (focusable or has_text):
        return children
    
    display_text = text or content_desc or hint
    if focusable and not display_text:
        child_texts = get_children_texts(element)
        display_text = ' '.join(child_texts).strip()
    
    element_info = {
        "text": display_text,
        "class": element.get('class', ''),
        "package": element.get('package', ''),
        "coordinates": {"x": bounds["x"], "y": bounds["y"]} if bounds else None
    }
    
    if resource_id:
        element_info["resource_id"] = resource_id
    
    if children:
        filtered_children = []
        for child in children:
            child_text = child.get("text", "")
            child_coords = child.get("coordinates")

            if not (child_text == element_info["text"] and child_coords == element_info["coordinates"]):
                filtered_children.append(child)

        if filtered_children:
            element_info["children"] = filtered_children
    
    return [element_info]


@mcp.tool()
def mobile_dump_ui() -> str:
    """Get UI elements from Android screen as JSON with hierarchical structure.
    
    Returns a JSON structure where elements contain their child elements, showing parent-child relationships.
    Only includes focusable elements or elements with text/content_desc/hint attributes.
    """
    try:
        xml_content = device.dump_hierarchy()
        root = ET.fromstring(xml_content)
        
        # with open("last_ui_dump.xml", "w", encoding="utf-8") as f:
        #     f.write(xml_content)

        ui_elements = extract_ui_elements(root)
        return json.dumps(ui_elements, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Error processing XML: {str(e)}"

@mcp.tool()
def mobile_click(x: int, y: int) -> str:
    """Click on a specific coordinate on the Android screen.
    
    Args:
        x: X coordinate to click
        y: Y coordinate to click
    """
    try:
        device.click(x, y)
        return f"Successfully clicked on coordinate ({x}, {y})"
    except Exception as e:
        return f"Error clicking coordinate ({x}, {y}): {str(e)}"

@mcp.tool()
def mobile_type(text: str, submit: bool = False) -> str:
    """Input text into the currently focused text field on Android.
    
    Args:
        text: The text to input
        submit: Whether to submit text (press Enter key) after typing
    """
    try:
        device.send_keys(text)
        if submit:
            device.press("enter")
            return f"Successfully input text: {text} and pressed Enter"
        return f"Successfully input text: {text}"
    except Exception as e:
        return f"Error inputting text: {str(e)}"

@mcp.tool()
def mobile_key_press(button: str) -> str:
    """Press a physical or virtual button on the Android device.
    
    Args:
        button: Button name (BACK, HOME, RECENT, ENTER)
    """
    button_map = {
        "BACK": "back",
        "HOME": "home",
        "RECENT": "recent",
        "ENTER": "enter"
    }
    
    key = button_map.get(button.upper(), button.lower())
    
    try:
        device.press(key)
        return f"Successfully pressed {button} button"
    except Exception as e:
        return f"Error pressing {button} button: {str(e)}"

@mcp.tool()
def mobile_swipe(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> str:
    """Perform a swipe gesture on the Android screen.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Duration of swipe in seconds (default: 0.5)
    """
    try:
        device.swipe(start_x, start_y, end_x, end_y, duration)
        return f"Successfully swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})"
    except Exception as e:
        return f"Error swiping: {str(e)}"


def is_system_app(package):
    exclude_patterns = [
        r"^com\.android\.systemui",
        r"^com\.android\.providers\.",
        r"^com\.android\.internal\.",
        r"^com\.android\.cellbroadcast",
        r"^com\.android\.phone",
        r"^com\.android\.bluetooth",
        r"^com\.google\.android\.overlay",
        r"^com\.google\.mainline",
        r"^com\.google\.android\.ext",
        r"\.auto_generated_rro_",
        r"^android$",
    ]
    return any(re.search(p, package) for p in exclude_patterns)

def is_launchable_app(package):
    if is_system_app(package):
        return False
    
    try:
        output = subprocess.check_output(
            ["adb", "shell", "cmd", "package", "resolve-activity", "--brief", package],
            text=True
        ).strip()
        print(output)
        return "/" in output

    except subprocess.CalledProcessError:
        return False

@mcp.tool()
def mobile_list_apps() -> str:
    """List all installed applications on the Android device.
    
    Returns a JSON array with package names and application labels.
    """
    try:
        apps = device.app_list()
        launchable_apps = [pkg for pkg in apps if is_launchable_app(pkg)]
        return json.dumps(launchable_apps, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error listing apps: {str(e)}"

@mcp.tool()
def mobile_launch_app(package_name: str) -> str:
    """Launch an application by its package name.
    
    Args:
        package_name: The package name of the app to launch (e.g., 'com.android.chrome')
    """
    try:
        device.app_start(package_name)
        return f"Successfully launched app: {package_name}"
    except Exception as e:
        return f"Error launching app {package_name}: {str(e)}"

@mcp.tool()
def mobile_take_screenshot() -> Image:
    """Take a screenshot of the current Android screen.
    
    Returns an image object that can be viewed by the LLM.
    """
    try:
        screenshot = device.screenshot()
    
        buf = io.BytesIO()
        screenshot.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        return Image(data=img_bytes, format="png")
        
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()