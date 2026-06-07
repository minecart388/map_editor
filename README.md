# Schematic-Edit

Multi-layer map editor with support for custom textures, a preset system, a command console, and PNG export.

## Features

- **Multi-layer editing** – create and manage layers
- **Support for custom textures** – load PNG images
- **Save to JSON** – fully save all layers, borders, and settings
- **Export to PNG** – save the map as an image
- **Preset System** – saving and loading ready-made map templates
- **Undo / Redo** – up to 100 steps of history
- **Boundary Editing** – creating fences and borders between cells
- **Fill and Eyedropper** – quickly copying and filling textures
- **Control Console** – drawing shapes, managing layers, and presets through text commands
- **Grid** – convenient navigation through the map
- **Hotbar** – quick access to 9 texture slots
- **Custom Brushes** – define your own brush shapes
- **Selection Tools** – select, copy, cut, paste, and move rectangular areas
- **Clone Stamp** – copy textures from one place and paint them elsewhere
- **Shape Primitives** – draw circles, rectangles, and lines with one click
- **Viewport Controls** – zoom, pan, and center the map

### Launching

1. Launch the application `Schematic-Edit` (or `main.py` from the source code).
2. The editor window will open with an empty 100×50 map.

### Console commands

Type commands into the console at the bottom‑right. Press `Ctrl+Enter` to execute multi‑line commands.

| Command | Description |
|---------|-------------|
| `help` | Show this help |
| `circle x y radius fill [texture.png]` | Draw a circle |
| `rect x1 y1 x2 y2 fill [texture.png]` | Draw a rectangle |
| `line x1 y1 x2 y2 thickness [texture.png]` | Draw a line |
| `clear <all/layer>` | Clear all layers or the current layer |
| `layers` | Show layer information |
| `layer <number>` | Switch to a layer |
| `layer <number> show` | Show/hide a layer |
| `layer <number> del` | Delete a layer |
| `tool` | Show the current tool |
| `presets` | List available presets |
| `save_preset` | Save the current map as a preset |
| `load_preset` | Load a preset |
| `delete_preset <name>` | Delete a preset |
| `replace <old_texture> <new_texture>` | Replace a texture across all layers |
| `brush <size>` | Set brush size (1‑10) |
| `clear_console` | Clear the console |

**Parameters:**
- `fill`: `true` / `false` – fill the shape
- Coordinates `x`, `y` – in map cells (from 0 to width/height)
- `thickness` – from 1 to 10
- Texture names must match the filenames in `assets/textures/block/`

### Editing the map

#### Drawing with a texture
1. Select a texture in the toolbar or in the hotbar.
2. Left‑click on a cell – the texture will be placed.
3. Hold the left button and drag the mouse to draw a line.
4. You can change the brush size using the `+` / `-` buttons or the `brush` command.

#### Using the eyedropper
- **Method 1:** Click the `Eyedropper` button, then click on a texture on the map.
- **Method 2:** hold down `Alt` and left‑click on the texture.

#### Fill area
1. Select the texture (brush).
2. Click the button `Fill`.
3. Click on the area you want to fill.
4. All adjacent cells with the same texture will be replaced.

#### Clear
- **Clear the current layer** – via console: `clear layer`
- **Clear all layers** – via console: `clear all` or the button `Clear`.

#### Undo / Redo
- Press `Ctrl+Z` to undo, `Ctrl+Y` to redo (or use the toolbar buttons).

### Working with textures

#### Loading textures
1. Click `Load textures` .
2. Select PNG files in the dialog box.
3. The textures will appear in the toolbar, hotbar, and will be available for selection.

#### Deleting textures
1. Click **"Delete textures"** .
2. A dialog with a list of all loaded textures will open.
3. Enter the numbers to delete (separated by spaces) or `all` to delete all.
4. The toolbar and hotbar update automatically.

### Working with layers

- Use the spinbox and `+` / `-` buttons to switch, add, or remove layers.
- The `Visibility` checkbox shows/hides the current layer.
- Click `List` to print layer information in the console.
- Maximum number of layers: 383.

### Selection tools (copy / cut / paste / move)

1. Click the `Select` button.
2. Drag the mouse to create a rectangular selection.
3. Use the `Copy`, `Cut`, or `Paste` buttons.
4. Press `Escape` to clear the selection.

### Custom brushes

1. Click `Brush settings`.
2. Switch to `Custom` mode.
3. Create a new brush: set a name, size, and click on the grid cells to define the shape.
4. Save the brush – it will appear in the custom brush list.
5. Select it to use as your active brush.

### Hotbar customization

- The hotbar shows 9 slots with thumbnails of your textures.
- Click `Replace hotbar`to open a full configuration window:
    - Clear individual slots or all slots
    - Assign any loaded texture to an empty slot
    - Search and filter textures
- The hotbar configuration is saved automatically.

### Centering and navigation

- `Center` – automatically zooms and pans to fit the whole map.
- Right‑click and drag to pan the view.
- Use the mouse wheel or `Ctrl+Plus` / `Ctrl+Minus` to zoom.

### Theme switching

Click `Theme` to toggle between light and dark mode. The theme choice is saved.

### Working with presets

#### Saving a preset
1. Click `Save preset` or enter `save_preset` in the console.
2. Enter a name.
3. The preset will be saved in the `assets/presets/` folder.

#### Loading a preset
1. Click `Load preset` or enter `load_preset` in the console.
2. Select a preset from the list.
3. The map will load.

#### Deleting a preset
1. Enter `delete_preset <name>` in the console.
2. Confirm the deletion.

## System requirements

- **OS:** Windows 7/8/10/11 (also works on Linux/macOS when run from source)
- **Python:** 3.8+ (to run from source)
- **RAM:** 256 MB (512 MB recommended for large maps)
- **Dependencies:** Pillow (for image processing)

## Note for version 2.0.4

By default, the maximum map size is limited to **500 cells in width** and **250 cells in height**. If you need a larger map, download the source code, locate `scripts/editor.py`, and modify lines 406–411:

```python
if new_w > 500:
    self.console._print("Width cannot exceed 500 cells", "error")
    return
if new_h > 250:
    self.console._print("Height cannot exceed 250 cells", "error")
    return
```

After changing the limits, you can either run the source directly via `main.py` or recompile the executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

## License and distribution

Allowed:
- Personal and commercial use
- Modification of the source code
- Distribution of copies

Prohibited:
- Passing off the program as your own
- Removing the author's information