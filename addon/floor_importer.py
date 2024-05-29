import bpy
import json

def create_wall(start, end, height, thickness):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, height / 2))
    obj = bpy.context.object
    obj.scale = ((end[0] - start[0]) / 2, thickness / 2, height / 2)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

class ImportFloorFile(bpy.types.Operator):
    bl_idname = "import_scene.floor"
    bl_label = "Import .floor File"
    bl_options = {'PRESET', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        with open(self.filepath, 'r') as file:
            data = json.load(file)

        for floor in data.get('floors', []):
            for room in floor.get('rooms', []):
                for wall in room.get('walls', []):
                    create_wall(
                        (wall['start_point']['x'], wall['start_point']['y'], wall['start_point']['z']),
                        (wall['end_point']['x'], wall['end_point']['y'], wall['end_point']['z']),
                        wall['wall_height'],
                        wall['wall_thickness']
                    )
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportFloorFile.bl_idname, text="Floor File (.floor)")

def register():
    bpy.utils.register_class(ImportFloorFile)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportFloorFile)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
