import pygame

import settings

from map_editor_tool import selection


def calculate_placement_pos(editor, mouse_world_x, mouse_world_y, current_definition):
    """설치 Y값 자유화: 카테고리가 enemy일 경우 타일 스냅을 풀고 마우스 좌표를 그대로 반환"""
    if current_definition.category == "enemy":
        return mouse_world_x, mouse_world_y

    # 일반 플랫폼은 기존 격자(스냅) 시스템 유지
    snap_x = (mouse_world_x // editor.GRID_SIZE) * editor.GRID_SIZE
    snap_y = (mouse_world_y // editor.GRID_SIZE) * editor.GRID_SIZE
    return snap_x, snap_y


def handle_event(editor, event, mouse_virtual):
    if event.type == pygame.QUIT:
        return editor._app_state("QUIT")
    if editor.mode == "select":
        from map_editor_tool import map_selector
        return map_selector.handle_select_event(editor, event, mouse_virtual)
    if event.type == pygame.KEYDOWN:
        return handle_keydown(editor, event)
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_down(editor, event, mouse_virtual)
    if event.type == pygame.MOUSEMOTION and editor.dragging and editor.selected_platform:
        world = screen_to_world(editor, mouse_virtual)
        vars_obj = editor.selected_platform.vars
        vars_obj.x = snap(editor, world.x - editor.drag_offset.x)
        vars_obj.y = snap(editor, world.y - editor.drag_offset.y)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        editor.dragging = False
    return None


def handle_keydown(editor, event):
    if event.key == pygame.K_ESCAPE:
        return editor._app_state("MENU")
    if event.key == pygame.K_1:
        editor.tool = "place"
    elif event.key == pygame.K_2:
        editor.tool = "select"
    elif event.key == pygame.K_3:
        editor.tool = "erase"
    elif event.key == pygame.K_TAB and editor.palette:
        editor.palette_index = (editor.palette_index + 1) % len(editor.palette)
    elif event.key == pygame.K_s:
        if editor.save_map():
            return editor._app_state("MENU")
    elif event.key == pygame.K_l:
        editor.load_saved_or_source()
    elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
        selection.delete_selected(editor)
    elif editor.selected_platform:
        handle_selected_shortcuts(editor, event)
    return None


def handle_selected_shortcuts(editor, event):
    vars_obj = editor.selected_platform.vars
    if event.key == pygame.K_LEFTBRACKET:
        vars_obj.width = max(40, vars_obj.width - editor.GRID_SIZE)
        editor.selected_platform.load_image()
    elif event.key == pygame.K_RIGHTBRACKET:
        vars_obj.width += editor.GRID_SIZE
        editor.selected_platform.load_image()
    elif event.key == pygame.K_SEMICOLON:
        vars_obj.height = max(20, vars_obj.height - 10)
        editor.selected_platform.load_image()
    elif event.key == pygame.K_QUOTE:
        vars_obj.height += 10
        editor.selected_platform.load_image()
    elif event.key == pygame.K_v:
        vars_obj.is_visible = not vars_obj.is_visible
    elif event.key == pygame.K_p:
        vars_obj.passable_from_bottom = not getattr(vars_obj, "passable_from_bottom", False)


def handle_mouse_down(editor, event, mouse_virtual):
    if event.button == 1:
        if mouse_virtual[0] >= settings.VIRTUAL_WIDTH - editor.SIDEBAR_W:
            return handle_sidebar_click(editor, mouse_virtual)

        world = screen_to_world(editor, mouse_virtual)
        if editor.tool == "place":
            selection.place_selected(editor, world)
        elif editor.tool == "erase":
            # 🎯 마우스 위치의 플랫폼/엔티티 통합 탐색 객체 획득
            target_obj = selection.find_platform_at(editor, world)
            if target_obj:
                # 1. 플랫폼 리스트에 존재하는 경우 안전 삭제
                if target_obj in editor.map_manager.platforms:
                    editor.map_manager.platforms.remove(target_obj)
                    if hasattr(editor.map_manager, "structures") and target_obj in editor.map_manager.structures:
                        editor.map_manager.structures.remove(target_obj)
                # 2. 엔티티(몹 등) 리스트에 존재하는 경우 안전 삭제
                elif target_obj in editor.map_manager.entities:
                    editor.map_manager.entities.remove(target_obj)

                if editor.selected_platform is target_obj:
                    editor.selected_platform = None
        else:
            editor.selected_platform = selection.find_platform_at(editor, world)
            if editor.selected_platform:
                vars_obj = editor.selected_platform.vars
                editor.dragging = True
                editor.drag_offset = pygame.Vector2(world.x - vars_obj.x, world.y - vars_obj.y)
    elif event.button == 3:
        editor.tool = "select"
        editor.selected_platform = selection.find_platform_at(editor, screen_to_world(editor, mouse_virtual))
    elif event.button == 4:
        editor.camera.y = max(0, editor.camera.y - editor.GRID_SIZE)
    elif event.button == 5:
        editor.camera.y += editor.GRID_SIZE
    return None


def handle_sidebar_click(editor, mouse_virtual):
    x, y = mouse_virtual
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    if editor.SAVE_BUTTON_RECT.collidepoint(x, y):
        if editor.save_map():
            return editor._app_state("MENU")
        return None

    tool_buttons = [
        ("place", pygame.Rect(panel_x + 24, 246, 82, 42)),
        ("select", pygame.Rect(panel_x + 116, 246, 82, 42)),
        ("erase", pygame.Rect(panel_x + 208, 246, 82, 42)),
    ]
    for tool, rect in tool_buttons:
        if rect.collidepoint(x, y):
            editor.tool = tool
            return None

    item_y = 348
    for idx, _definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, item_y + idx * 54, editor.SIDEBAR_W - 48, 42)
        if rect.collidepoint(x, y):
            editor.palette_index = idx
            editor.tool = "place"
            return None
    return None


def update_camera(editor, dt):
    keys = pygame.key.get_pressed()
    speed = 720 * dt
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        editor.camera.x = max(0, editor.camera.x - speed)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        max_x = max(0, editor.map_manager.width - (settings.VIRTUAL_WIDTH - editor.SIDEBAR_W))
        editor.camera.x = min(max_x, editor.camera.x + speed)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        editor.camera.y = max(0, editor.camera.y - speed)
    if keys[pygame.K_s] and not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
        max_y = max(0, editor.map_manager.height - settings.VIRTUAL_HEIGHT)
        editor.camera.y = min(max_y, editor.camera.y + speed)
    if keys[pygame.K_DOWN]:
        max_y = max(0, editor.map_manager.height - settings.VIRTUAL_HEIGHT)
        editor.camera.y = min(max_y, editor.camera.y + speed)


def window_to_virtual(editor, pos):
    x, y = pos
    return int(x * settings.VIRTUAL_WIDTH / settings.SCREEN_WIDTH), int(y * settings.VIRTUAL_HEIGHT / settings.SCREEN_HEIGHT)


def screen_to_world(editor, pos):
    x, y = pos
    return pygame.Vector2(x + editor.camera.x, y + editor.camera.y)


def snap(editor, value):
    return int(round(float(value) / editor.GRID_SIZE) * editor.GRID_SIZE)
