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
        
    # 🎯 최소한의 안전한 단축키만 가볍게 복구하고 싶을 때 추가하는 영역
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return editor._app_state("MENU") # ESC 누르면 안전하게 메뉴로 퇴장
        elif event.key == pygame.K_1:
            editor.tool = "place"
        elif event.key == pygame.K_2:
            editor.tool = "select"
        elif event.key == pygame.K_3:
            editor.tool = "erase"
            
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


# map_editor_tool/input_handler.py:62-79 범위 수정
# map_editor_tool/input_handler.py:147-172 범위 수정 (사이드바 마우스 감지 추가)
def handle_sidebar_click(editor, click_pos):
    """
    사이드바 영역 클릭 시 세부 처리부.
    인스펙터 UI 내부의 버튼 충돌을 계산하여 즉시 속성 및 리사이징을 수행합니다.
    """
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    if click_pos.x < panel_x:
        return False

    # 1. 저장 버튼 클릭 처리
    if editor.SAVE_BUTTON_RECT.collidepoint(click_pos):
        from map_editor_tool import serializer
        serializer.save_map(editor)
        return True

    # 2. 툴 버튼 클릭 처리
    for tool_name, rect_x in [("place", panel_x + 24), ("select", panel_x + 116), ("erase", panel_x + 208)]:
        tool_rect = pygame.Rect(rect_x, 246, 82, 42)
        if tool_rect.collidepoint(click_pos):
            editor.tool = tool_name
            return True

    # 3. 팔레트 오브젝트 선택 처리
    for idx, definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, 348 + idx * 54, editor.SIDEBAR_W - 48, 42)
        if rect.collidepoint(click_pos):
            editor.palette_index = idx
            return True

    # 4. 플랫폼 인스펙터 버튼 인터랙션 처리 (플랫폼이 선택되어 있을 때만 동작)
    if editor.selected_platform:
        vars_obj = editor.selected_platform.vars

        # ── 가로 길이(Width) 수정 버튼 ──
        if hasattr(editor, "BTN_W_DEC") and editor.BTN_W_DEC.collidepoint(click_pos):
            vars_obj.width = max(editor.GRID_SIZE, vars_obj.width - editor.GRID_SIZE)
            editor.selected_platform.load_image() # 실시간 텍스처 리사이징
            return True
        elif hasattr(editor, "BTN_W_INC") and editor.BTN_W_INC.collidepoint(click_pos):
            vars_obj.width += editor.GRID_SIZE
            editor.selected_platform.load_image()
            return True

        # ── 세로 길이(Height) 수정 버튼 ──
        elif hasattr(editor, "BTN_H_DEC") and editor.BTN_H_DEC.collidepoint(click_pos):
            vars_obj.height = max(10, vars_obj.height - 10)
            editor.selected_platform.load_image()
            return True
        elif hasattr(editor, "BTN_H_INC") and editor.BTN_H_INC.collidepoint(click_pos):
            vars_obj.height += 10
            editor.selected_platform.load_image()
            return True

        # ── 충돌 타입 3종 변경 버튼 ──
        elif hasattr(editor, "BTN_SOLID") and editor.BTN_SOLID.collidepoint(click_pos):
            vars_obj.platform_type = "SOLID"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = False
            return True
        elif hasattr(editor, "BTN_ONE_WAY") and editor.BTN_ONE_WAY.collidepoint(click_pos):
            vars_obj.platform_type = "ONE_WAY"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = True
            return True
        elif hasattr(editor, "BTN_GHOST") and editor.BTN_GHOST.collidepoint(click_pos):
            vars_obj.platform_type = "GHOST"
            vars_obj.is_solid = False
            vars_obj.passable_from_bottom = True
            return True

    return False


def handle_mouse_down(editor, event, mouse_virtual):
    # 어떤 타입의 좌표가 들어와도 pygame.Vector2로 강제 통합하여 무결성 유지
    pos_vector = pygame.Vector2(mouse_virtual[0], mouse_virtual[1])

    if event.button == 1:
        # 사이드바 충돌 판정 (Vector2 속성인 .x 활용)
        if pos_vector.x >= settings.VIRTUAL_WIDTH - editor.SIDEBAR_W:
            return handle_sidebar_click(editor, pos_vector)

        world = screen_to_world(editor, pos_vector)
        if editor.tool == "place":
            selection.place_selected(editor, world)
        elif editor.tool == "erase":
            target_obj = selection.find_platform_at(editor, world)
            if target_obj:
                if target_obj in editor.map_manager.platforms:
                    editor.map_manager.platforms.remove(target_obj)
                    if hasattr(editor.map_manager, "structures") and target_obj in editor.map_manager.structures:
                        editor.map_manager.structures.remove(target_obj)
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
        editor.selected_platform = selection.find_platform_at(editor, screen_to_world(editor, pos_vector))
        
    elif event.button == 4:
        editor.camera.y = max(0, editor.camera.y - editor.GRID_SIZE)
    elif event.button == 5:
        editor.camera.y += editor.GRID_SIZE
        
    return None


def handle_sidebar_click(editor, mouse_virtual):
    # 어떤 형태의 마우스 좌표가 넘어오든 안전하게 언패킹
    x, y = mouse_virtual[0], mouse_virtual[1]
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W

    # 1. 원래의 [저장] 버튼 처리 (기존 구조 완벽 유지)
    if editor.SAVE_BUTTON_RECT.collidepoint(x, y):
        if editor.save_map():
            return editor._app_state("MENU")
        return None

    # 2. 원래의 [툴 선택] 버튼 처리 (기존 구조 완벽 유지)
    tool_buttons = [
        ("place", pygame.Rect(panel_x + 24, 246, 82, 42)),
        ("select", pygame.Rect(panel_x + 116, 246, 82, 42)),
        ("erase", pygame.Rect(panel_x + 208, 246, 82, 42)),
    ]
    for tool, rect in tool_buttons:
        if rect.collidepoint(x, y):
            editor.tool = tool
            return None

    # 3. 원래의 [팔레트 아이템 선택] 처리 (기존 구조 완벽 유지)
    item_y = 348
    for idx, _definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, item_y + idx * 54, editor.SIDEBAR_W - 48, 42)
        if rect.collidepoint(x, y):
            editor.palette_index = idx
            editor.tool = "place"
            return None

    # 4. 🎯 추가된 [인스펙터 플랫폼 수정] 처리 (선택된 플랫폼이 있을 때만 안전하게 검사)
    # map_editor_tool/input_handler.py의 handle_sidebar_click 내 인스펙터 수정부
    if editor.selected_platform:
        vars_obj = editor.selected_platform.vars

        # ── 가로 길이(W) 수정 ──
        if hasattr(editor, "BTN_W_DEC") and editor.BTN_W_DEC.collidepoint(x, y):
            vars_obj.width = max(editor.GRID_SIZE, vars_obj.width - editor.GRID_SIZE)
            editor.selected_platform.load_image()
            return None
        elif hasattr(editor, "BTN_W_INC") and editor.BTN_W_INC.collidepoint(x, y):
            vars_obj.width += editor.GRID_SIZE
            editor.selected_platform.load_image()
            return None

        # ── 세로 길이(H) 수정 ──
        elif hasattr(editor, "BTN_H_DEC") and editor.BTN_H_DEC.collidepoint(x, y):
            vars_obj.height = max(10, vars_obj.height - 10)
            editor.selected_platform.load_image()
            return None
        elif hasattr(editor, "BTN_H_INC") and editor.BTN_H_INC.collidepoint(x, y):
            vars_obj.height += 10
            editor.selected_platform.load_image()
            return None

        # ── 충돌 타입 3종 변경 및 내부 물리 플래그 강제 정렬 ──
        elif hasattr(editor, "BTN_SOLID") and editor.BTN_SOLID.collidepoint(x, y):
            vars_obj.platform_type = "SOLID"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = False
            return None
        elif hasattr(editor, "BTN_ONE_WAY") and editor.BTN_ONE_WAY.collidepoint(x, y):
            vars_obj.platform_type = "ONE_WAY"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = True
            return None
        elif hasattr(editor, "BTN_GHOST") and editor.BTN_GHOST.collidepoint(x, y):
            vars_obj.platform_type = "GHOST"
            vars_obj.is_solid = False
            vars_obj.passable_from_bottom = True
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
