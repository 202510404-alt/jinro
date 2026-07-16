import os

import pygame

import settings
from map_editor_tool import input_handler, map_selector, renderer, selection, serializer
from map_editor_tool.object_registry import EditorObjectDefinition, EditorObjectRegistry


class MapEditor:
    SIDEBAR_W = 330
    GRID_SIZE = 40
    PANEL_PAD = 24
    SAVE_BUTTON_RECT = pygame.Rect(settings.VIRTUAL_WIDTH - SIDEBAR_W + PANEL_PAD, 168, SIDEBAR_W - PANEL_PAD * 2, 48)

    def __init__(self, map_name=None, save_name=None):
        EditorObjectRegistry.ensure_defaults()
        EditorObjectRegistry.discover_fabric_definitions()
        self.maps_dir = self._ensure_maps_dir()
        self.map_files = map_selector.scan_map_files(self)
        self.map_name = map_name
        self.save_name = save_name or map_name
        self.selected_map_file = self._map_name_to_file(map_name) if map_name else None
        self.map_manager = None
        self.palette = EditorObjectRegistry.definitions()
        self.palette_index = 0
        self.tool = "place"
        self.mode = "select" if map_name is None else "edit"
        self.camera = pygame.Vector2(0, 0)
        self.selected_platform = None
        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        self.status_message = "Select a map to edit"
        self.selected_trigger_idx = -1
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)
        self.header_font = pygame.font.SysFont("malgungothic", 30, bold=True)
        self._build_map_selection_buttons()
        if map_name is not None:
            self.load_map(map_name, self.selected_map_file)

    def _ensure_maps_dir(self):
        maps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map_system", "maps")
        os.makedirs(maps_dir, exist_ok=True)
        return maps_dir

    def _build_map_selection_buttons(self):
        map_selector.build_map_selection_buttons(self)

    def get_object_visibility(self, obj):
        return selection.get_object_visibility(self, obj)

    def calculate_placement_pos(self, mouse_world_x, mouse_world_y, current_definition):
        return input_handler.calculate_placement_pos(self, mouse_world_x, mouse_world_y, current_definition)

    def load_map(self, map_name, file_name=None):
        self.map_name = map_name
        self.save_name = map_name
        self.selected_map_file = file_name or self._map_name_to_file(map_name)

        from map_system.map_main import GameMap
        self.map_manager = GameMap(map_id=map_name)

        if not hasattr(self.map_manager, "structures"):
            self.map_manager.structures = []

        self.mode = "edit"
        self.camera.x = 0
        self.camera.y = 0
        self.selected_platform = None
        self.dragging = False
        self.status_message = f"Editing {self.selected_map_file}"

    def _file_to_map_name(self, file_name):
        return map_selector.file_to_map_name(file_name)

    def _map_name_to_file(self, map_name):
        return map_selector.map_name_to_file(map_name)

    def _next_new_map_file(self):
        return map_selector.next_new_map_file(self)

    def run(self, window_screen, virtual_screen, clock):
        pygame.display.set_caption("Jin Ro Project - Map Editor")
        while True:
            dt = clock.tick(settings.FPS) / 1000.0
            mouse_virtual = self._window_to_virtual(pygame.mouse.get_pos())

            for event in pygame.event.get():
                result = self._handle_event(event, mouse_virtual)
                if result is not None:
                    return result

            if self.mode == "edit":
                self._update_camera(dt)
                self._draw(virtual_screen)
            else:
                self._draw_map_select(virtual_screen, mouse_virtual)
            scaled_surface = pygame.transform.smoothscale(
                virtual_screen,
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            )
            window_screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()

    def _handle_event(self, event, mouse_virtual):
        return input_handler.handle_event(self, event, mouse_virtual)

    def _handle_select_event(self, event, mouse_virtual):
        return map_selector.handle_select_event(self, event, mouse_virtual)

    def _handle_keydown(self, event):
        return input_handler.handle_keydown(self, event)

    def _handle_selected_shortcuts(self, event):
        return input_handler.handle_selected_shortcuts(self, event)

    def _handle_mouse_down(self, event, mouse_virtual):
        return input_handler.handle_mouse_down(self, event, mouse_virtual)

    def _handle_sidebar_click(self, mouse_virtual):
        return input_handler.handle_sidebar_click(self, mouse_virtual)

    def _update_camera(self, dt):
        return input_handler.update_camera(self, dt)

    def place_selected(self, world):
        return selection.place_selected(self, world)

    def find_platform_at(self, world):
        return selection.find_platform_at(self, world)

    def delete_selected(self):
        return selection.delete_selected(self)

    def save_map(self):
        return serializer.save_map(self)

    def load_saved_or_source(self):
        return serializer.load_saved_or_source(self)

    def serialize_map(self):
        return serializer.serialize_map(self)

    def _serialize_platform(self, platform):
        return serializer._serialize_platform(self, platform)

    def _serialize_structure(self, struct):
        return serializer._serialize_structure(self, struct)

    def _serialize_entity(self, entity):
        return serializer._serialize_entity(self, entity)

    def _serialize_trigger(self, trigger):
        return serializer._serialize_trigger(self, trigger)

    def _infer_entity_type(self, entity):
        return serializer._infer_entity_type(self, entity)

    def _draw(self, surface):
        return renderer.draw(self, surface)

    def _draw_map_select(self, surface, mouse_virtual):
        return renderer.draw_map_select(self, surface, mouse_virtual)

    def _draw_button(self, surface, rect, label, is_hovered=False):
        return renderer.draw_button(self, surface, rect, label, is_hovered)

    def _draw_grid(self, surface):
        return renderer.draw_grid(self, surface)

    def _draw_selection(self, surface):
        return renderer.draw_selection(self, surface)

    def _draw_sidebar(self, surface):
        return renderer.draw_sidebar(self, surface)

    def _draw_tool_button(self, surface, tool, x, y):
        return renderer.draw_tool_button(self, surface, tool, x, y)

    def _draw_inspector(self, surface, panel_x):
        return renderer.draw_inspector(self, surface, panel_x)

    def _draw_help(self, surface, panel_x):
        return renderer.draw_help(self, surface, panel_x)

    def _draw_status(self, surface):
        return renderer.draw_status(self, surface)

    def _text(self, surface, text, x, y, font, color=(238, 242, 245)):
        return renderer.text(self, surface, text, x, y, font, color)

    def _window_to_virtual(self, pos):
        return input_handler.window_to_virtual(self, pos)

    def _screen_to_world(self, pos):
        return input_handler.screen_to_world(self, pos)

    def _snap(self, value):
        return input_handler.snap(self, value)

    def _app_state(self, name):
        if name == "MENU":
            return "MAIN_MENU"
        if name == "QUIT":
            return None
        return name

    def scan_map_files(self):
        return map_selector.scan_map_files(self)
