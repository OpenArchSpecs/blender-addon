import bpy

class ImportFloorPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_import_floor"
    bl_label = "Import Floor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Floor Import'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("import_scene.floor", text="Import .floor File")

def register():
    bpy.utils.register_class(ImportFloorPanel)

def unregister():
    bpy.utils.unregister_class(ImportFloorPanel)

if __name__ == "__main__":
    register()
