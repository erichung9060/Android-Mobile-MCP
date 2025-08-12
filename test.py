import uiautomator2 as u2
import xml.etree.ElementTree as ET
import json

device = u2.connect()
device.press("recent")
