import uiautomator2 as u2
import xml.etree.ElementTree as ET
import json

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
    
result = mobile_dump_ui()
with open("ui_dump.json", "w", encoding="utf-8") as f:
    f.write(result)