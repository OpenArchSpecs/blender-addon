bl_info = {
    "name": "Floor File Importer",
    "blender": (4, 0, 0),
    "category": "Import-Export",
    "description": "Import .floor files and create 3D models based on floor plan data",
    "author": "Your Name",
    "version": (1, 0, 0)
}

import bpy
from . import floor_importer, ui

def register():
    floor_importer.register()
    ui.register()

def unregister():
    floor_importer.unregister()
    ui.unregister()

if __name__ == "__main__":
    register()
