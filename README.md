# Android Mobile MCP

## Description

Android Mobile MCP is a server implementation that bridges the Model Context Protocol with Android device automation capabilities. It provides a comprehensive set of tools for interacting with Android devices, including UI element detection, touch interactions, text input, app management, and screenshot capture.

## Available Tools

### UI Interaction
- **`mobile_dump_ui`** - Get UI elements from Android screen as JSON with text and coordinates
- **`mobile_click`** - Click on a specific coordinate on the Android screen
- **`mobile_type`** - Input text into the currently focused text field with optional submit
- **`mobile_key_press`** - Press physical or virtual buttons (BACK, HOME, ENTER, VOLUME_UP, etc.)
- **`mobile_swipe`** - Perform swipe gestures with customizable duration
- **`mobile_take_screenshot`** - Capture screenshots of the current screen state

### App Management
- **`mobile_list_apps`** - List all installed applications with package names and labels
- **`mobile_launch_app`** - Launch applications by package name

## Installation

Install using uvx:

```bash
uvx android-mobile-mcp
```

### Prerequisites

1. Ensure your Android device has USB debugging enabled
2. Install ADB (Android Debug Bridge) on your system
3. Connect your Android device via USB or ensure it's accessible over the network
