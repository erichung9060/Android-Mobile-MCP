import uiautomator2 as u2
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
import xml.etree.ElementTree as ET
import json
import io

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

def extract_ui_elements(element, seen_texts=None):
    if seen_texts is None:
        seen_texts = set()
    
    elements = []
    
    resource_id = element.get('resource-id', '')
    
    if resource_id.startswith('com.android.systemui'):
        return elements
    
    class_name = element.get('class', '')
    text = element.get('text', '').strip()
    content_desc = element.get('content-desc', '').strip()
    bounds = parse_bounds(element.get('bounds', ''))
    
    display_text = text or content_desc
    if (display_text and bounds and display_text not in seen_texts) or (resource_id and bounds):
        if display_text:
            seen_texts.add(display_text)
            
        element_info = {
            "text": display_text,
            "coordinates": {"x": bounds["x"], "y": bounds["y"]},
            "class": class_name
        }
        if resource_id:
            element_info["resource_id"] = resource_id
        elements.append(element_info)
    
    for child in element:
        elements.extend(extract_ui_elements(child, seen_texts))
    
    return elements


def mobile_dump_ui() -> str:
    """Get UI elements from Android screen as JSON with text and coordinates.
    
    Returns a JSON array of UI elements with their text content and clickable coordinates.
    """
    try:
        xml_content = device.dump_hierarchy()
        with open("ui_dump.xml", "w", encoding="utf-8") as xml_file:
            xml_file.write(xml_content)
        root = ET.fromstring(xml_content)
        
        ui_elements = extract_ui_elements(root)
        
        return json.dumps(ui_elements, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"Error processing XML: {str(e)}"

@mcp.tool()
def mobile_dump_ui() -> str:
    """Get UI elements from Android screen as JSON with text and coordinates.
    
    Returns a JSON array of UI elements with their text content and clickable coordinates.
    """
    try:
        xml_content = device.dump_hierarchy()
        root = ET.fromstring(xml_content)
        
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
        button: Button name (BACK, HOME, ENTER, VOLUME_UP, VOLUME_DOWN, MENU, RECENT, etc.)
    """
    button_map = {
        "BACK": "back",
        "HOME": "home", 
        "RECENT": "recent",
        "OVERVIEW": "recent",
        "APP_SWITCH": "recent",
        "VOLUME_UP": "volume_up",
        "VOLUME_DOWN": "volume_down",
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

@mcp.tool()
def mobile_list_apps() -> str:
    """List all installed applications on the Android device.
    
    Returns a JSON array with package names and application labels.
    """
    try:
        apps = device.app_list()
        app_info = []
        for app in apps:
            app_info.append({
                "package": app,
                "name": device.app_info(app).get('label', app)
            })
        return json.dumps(app_info, ensure_ascii=False, indent=2)
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
        # For errors, we need to raise an exception rather than return a dict
        raise Exception(f"Error taking screenshot: {str(e)}")

def main():
    mcp.run()

if __name__ == "__main__":
    main()