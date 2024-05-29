bl_info = {
    "name": "Floor File Importer",
    "blender": (2, 80, 0),
    "category": "Import-Export",
    "description": "Import .floor files and create 3D models based on floor plan data",
    "author": "Your Name",
    "version": (1, 0, 0)
}

import bpy
from . import floor_importer, ui

def register():
    bpy.utils.register_class(floor_importer.ImportFloorFile)
    bpy.utils.register_class(ui.ImportFloorPanel)

def unregister():
    bpy.utils.unregister_class(floor_importer.ImportFloorFile)
    bpy.utils.unregister_class(ui.ImportFloorPanel)

if __name__ == "__main__":
    register()
