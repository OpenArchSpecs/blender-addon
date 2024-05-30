import bpy
import json
from bpy.props import StringProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup

def update_wall(self, context):
    # Remove the old wall
    old_obj = bpy.data.objects.get(self.wall_id)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)
    
    # Create the new wall
    start = (self.start_point_x, self.start_point_y, self.start_point_z)
    end = (self.end_point_x, self.end_point_y, self.end_point_z)
    create_wall(start, end, self.wall_height, self.wall_thickness, self.wall_id)

class WallProperty(PropertyGroup):
    start_point_x: FloatProperty(name="Start X", update=update_wall)
    start_point_y: FloatProperty(name="Start Y", update=update_wall)
    start_point_z: FloatProperty(name="Start Z", update=update_wall)
    end_point_x: FloatProperty(name="End X", update=update_wall)
    end_point_y: FloatProperty(name="End Y", update=update_wall)
    end_point_z: FloatProperty(name="End Z", update=update_wall)
    wall_height: FloatProperty(name="Height", update=update_wall)
    wall_thickness: FloatProperty(name="Thickness", update=update_wall)
    wall_id: StringProperty(name="Wall ID")

def create_wall(start, end, height, thickness, wall_id):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, height / 2))
    obj = bpy.context.object
    obj.scale = ((end[0] - start[0]) / 2, thickness / 2, height / 2)
    obj.name = wall_id
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

    # Parent the wall to the empty
    empty_obj = bpy.data.objects.get("FloorEmpty")
    if empty_obj:
        obj.parent = empty_obj

def create_floor_outline(outline):
    vertices = [(coord['x'], coord['y'], 0) for coord in outline]
    edges = [(i, (i + 1) % len(vertices)) for i in range(len(vertices))]
    mesh = bpy.data.meshes.new("FloorOutline")
    mesh.from_pydata(vertices, edges, [])
    obj = bpy.data.objects.new("FloorOutline", mesh)
    bpy.context.collection.objects.link(obj)

    # Parent the floor outline to the empty
    empty_obj = bpy.data.objects.get("FloorEmpty")
    if empty_obj:
        obj.parent = empty_obj

def create_room_outline(outline):
    vertices = [(coord['x'], coord['y'], 0) for coord in outline]
    edges = [(i, (i + 1) % len(vertices)) for i in range(len(vertices))]
    mesh = bpy.data.meshes.new("RoomOutline")
    mesh.from_pydata(vertices, edges, [])
    obj = bpy.data.objects.new("RoomOutline", mesh)
    bpy.context.collection.objects.link(obj)

    # Parent the room outline to the empty
    empty_obj = bpy.data.objects.get("FloorEmpty")
    if empty_obj:
        obj.parent = empty_obj

class ImportFloorFile(bpy.types.Operator):
    bl_idname = "import_scene.floor"
    bl_label = "Import .floor File"
    bl_options = {'PRESET', 'UNDO'}
    
    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        with open(self.filepath, 'r') as file:
            data = json.load(file)

        header = data.get('header', {})
        metadata = data.get('metadata', {})
        floors = data.get('floors', [])
        additional_metadata = data.get('additional_metadata', {})

        # Create a collection for the floor objects
        if "FloorCollection" in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections["FloorCollection"])

        floor_collection = bpy.data.collections.new("FloorCollection")
        bpy.context.scene.collection.children.link(floor_collection)

        # Create an empty object to parent all imported objects
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        empty_obj = bpy.context.object
        empty_obj.name = "FloorEmpty"
        floor_collection.objects.link(empty_obj)

        context.scene.walls.clear()

        for floor in floors:
            floor_outline = floor.get('floor_outline', [])
            if floor_outline:
                create_floor_outline(floor_outline)

            for room in floor.get('rooms', []):
                room_outline = room.get('room_outline', [])
                if room_outline:
                    create_room_outline(room_outline)

                for wall in room.get('walls', []):
                    wall_prop = context.scene.walls.add()
                    wall_prop.start_point_x = wall['start_point']['x']
                    wall_prop.start_point_y = wall['start_point']['y']
                    wall_prop.start_point_z = wall['start_point']['z']
                    wall_prop.end_point_x = wall['end_point']['x']
                    wall_prop.end_point_y = wall['end_point']['y']
                    wall_prop.end_point_z = wall['end_point']['z']
                    wall_prop.wall_height = wall['wall_height']
                    wall_prop.wall_thickness = wall['wall_thickness']
                    wall_prop.wall_id = wall['wall_id']

                    create_wall(
                        (wall['start_point']['x'], wall['start_point']['y'], wall['start_point']['z']),
                        (wall['end_point']['x'], wall['end_point']['y'], wall['end_point']['z']),
                        wall['wall_height'],
                        wall['wall_thickness'],
                        wall['wall_id']
                    )
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportFloorFile(bpy.types.Operator):
    bl_idname = "export_scene.floor"
    bl_label = "Export .floor File"
    bl_options = {'PRESET', 'UNDO'}
    
    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        walls_data = []
        for wall in context.scene.walls:
            walls_data.append({
                "wall_id": wall.wall_id,
                "start_point": {"x": wall.start_point_x, "y": wall.start_point_y, "z": wall.start_point_z},
                "end_point": {"x": wall.end_point_x, "y": wall.end_point_y, "z": wall.end_point_z},
                "wall_height": wall.wall_height,
                "wall_thickness": wall.wall_thickness
            })
        
        data = {
            "version": "1.0",
            "creation_date": "2024-05-30",
            "author": "Your Name",
            "metadata": {
                "project_name": "Exported Project",
                "location": "Unknown",
                "client_info": "Unknown",
                "building_dimensions": {
                    "length": 0,
                    "width": 0,
                    "height": 0
                },
                "number_of_floors": 1
            },
            "floors": [
                {
                    "floor_id": "Floor 1",
                    "floor_outline": [],
                    "rooms": [
                        {
                            "room_id": "Room 1",
                            "room_name": "Exported Room",
                            "room_outline": [],
                            "walls": walls_data
                        }
                    ]
                }
            ],
            "additional_metadata": {}
        }
        
        with open(self.filepath, 'w') as file:
            json.dump(data, file, indent=4)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportFloorFile.bl_idname, text="Floor File (.floor)")

def menu_func_export(self, context):
    self.layout.operator(ExportFloorFile.bl_idname, text="Floor File (.floor)")

def register():
    bpy.utils.register_class(WallProperty)
    bpy.utils.register_class(ImportFloorFile)
    bpy.utils.register_class(ExportFloorFile)
    bpy.types.Scene.walls = CollectionProperty(type=WallProperty)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(WallProperty)
    bpy.utils.unregister_class(ImportFloorFile)
    bpy.utils.unregister_class(ExportFloorFile)
    del bpy.types.Scene.walls
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
