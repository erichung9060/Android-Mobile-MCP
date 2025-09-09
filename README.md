# Android Mobile MCP

## Overview

Android Mobile MCP bridges the Model Context Protocol with Android device automation, enabling AI agents to interact with Android devices through UI manipulation, app management, and screen capture.

## MCP Configuration
```json
{
  "mcpServers": {
    "android-mobile-mcp": {
      "command": "uvx",
      "args": ["android-mobile-mcp"]
    }
  }
}
```

### Prerequisites

1. Enable USB debugging on your Android device
2. Install ADB (Android Debug Bridge)
3. Connect device via USB or network

## Tools Reference

### Screen Analysis

**`mobile_dump_ui`** - Extract UI elements as hierarchical JSON
- Parses screen XML to identify focusable elements and text content
- Calculates center coordinates for each interactive element
- Returns structured parent-child element relationships

**`mobile_take_screenshot`** - Capture current screen state
- Returns PNG image data for visual analysis

### Touch Interactions

**`mobile_click`** - Click at specific coordinates
- Validates coordinates against current UI state
- Requires prior `mobile_dump_ui` call for coordinate verification
- Prevents clicking on invalid or non-interactive areas

**`mobile_swipe`** - Perform swipe gestures
- Executes directional swipes between two coordinate points
- Configurable duration for gesture speed control

### Text Input

**`mobile_type`** - Input text into focused fields
- Sends text to currently active input field
- Optional automatic submission with Enter key

### Navigation

**`mobile_key_press`** - Press system buttons
- Supports hardware and virtual keys: BACK, HOME, RECENT, ENTER

### App Management

**`mobile_list_apps`** - List installed applications
- Filters out system apps and non-launchable packages
- Returns only user-accessible applications

**`mobile_launch_app`** - Start applications by package name
- Validates package existence before launch attempt
