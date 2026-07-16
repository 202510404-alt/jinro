import pygame

import settings


def draw(editor, surface):
    surface.fill((10, 15, 20))
    editor.map_manager.draw(surface, camera_offset=(editor.camera.x, editor.camera.y))
    draw_grid(editor, surface)
    draw_selection(editor, surface)
    draw_sidebar(editor, surface)
    draw_status(editor, surface)


def draw_map_select(editor, surface, mouse_virtual):
    surface.fill((18, 24, 30))
    title = editor.header_font.render("Select Map", True, (238, 242, 245))
    surface.blit(title, title.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 150)))

    subtitle_text = f"{len(editor.map_files)} map file(s) in src/map_system/maps"
    subtitle = editor.small_font.render(subtitle_text, True, (180, 198, 214))
    surface.blit(subtitle, subtitle.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 202)))

    if not editor.map_select_buttons:
        empty = editor.font.render("No existing maps found.", True, (220, 229, 237))
        surface.blit(empty, empty.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 310)))

    for file_name, rect in editor.map_select_buttons:
        draw_button(editor, surface, rect, file_name, rect.collidepoint(mouse_virtual))

    draw_button(editor, surface, editor.new_map_button, "Create New Map", editor.new_map_button.collidepoint(mouse_virtual))
    draw_button(editor, surface, editor.back_button, "Back to Main Menu", editor.back_button.collidepoint(mouse_virtual))

    help_text = editor.small_font.render("Click a file to open it. Esc returns to the main menu.", True, (150, 170, 188))
    surface.blit(help_text, help_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 120)))


def draw_button(editor, surface, rect, label, is_hovered=False):
    fill = (58, 78, 96) if is_hovered else (38, 49, 59)
    border = (152, 177, 199) if is_hovered else (74, 91, 106)
    pygame.draw.rect(surface, fill, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, 2, border_radius=6)
    label_surface = editor.font.render(label, True, (238, 242, 245))
    surface.blit(label_surface, label_surface.get_rect(center=rect.center))


def draw_grid(editor, surface):
    world_left = int(editor.camera.x)
    world_top = int(editor.camera.y)
    view_w = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    view_h = settings.VIRTUAL_HEIGHT
    color = (255, 255, 255, 34)

    grid_overlay = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
    start_x = -(world_left % editor.GRID_SIZE)
    start_y = -(world_top % editor.GRID_SIZE)
    for x in range(start_x, view_w, editor.GRID_SIZE):
        pygame.draw.line(grid_overlay, color, (x, 0), (x, view_h))
    for y in range(start_y, view_h, editor.GRID_SIZE):
        pygame.draw.line(grid_overlay, color, (0, y), (view_w, y))
    surface.blit(grid_overlay, (0, 0))


def draw_selection(editor, surface):
    if not editor.selected_platform:
        return
    vars_obj = editor.selected_platform.vars
    rect = pygame.Rect(
        vars_obj.x - editor.camera.x,
        vars_obj.y - editor.camera.y,
        vars_obj.width,
        vars_obj.height,
    )
    pygame.draw.rect(surface, (255, 229, 122), rect, 4)


def draw_sidebar(editor, surface):
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    pygame.draw.rect(surface, (26, 34, 42), (panel_x, 0, editor.SIDEBAR_W, settings.VIRTUAL_HEIGHT))
    pygame.draw.line(surface, (88, 106, 124), (panel_x, 0), (panel_x, settings.VIRTUAL_HEIGHT), 3)

    text(editor, surface, "Map Editor", panel_x + 24, 34, editor.header_font)
    text(editor, surface, f"Editing: {editor.selected_map_file}", panel_x + 24, 78, editor.small_font, (180, 198, 214))
    text(editor, surface, "Save writes this file and exits.", panel_x + 24, 104, editor.small_font, (180, 198, 214))

    from map_editor_tool import input_handler
    hovered = editor.SAVE_BUTTON_RECT.collidepoint(input_handler.window_to_virtual(editor, pygame.mouse.get_pos()))
    draw_button(editor, surface, editor.SAVE_BUTTON_RECT, "Save", hovered)

    text(editor, surface, "Tools", panel_x + 24, 214, editor.font)
    draw_tool_button(editor, surface, "place", panel_x + 24, 246)
    draw_tool_button(editor, surface, "select", panel_x + 116, 246)
    draw_tool_button(editor, surface, "erase", panel_x + 208, 246)

    text(editor, surface, "Palette", panel_x + 24, 310, editor.font)
    for idx, definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, 348 + idx * 54, editor.SIDEBAR_W - 48, 42)
        active = idx == editor.palette_index
        pygame.draw.rect(surface, (67, 92, 111) if active else (38, 49, 59), rect, border_radius=5)
        pygame.draw.rect(surface, (145, 170, 190) if active else (74, 91, 106), rect, 1, border_radius=5)
        text(editor, surface, definition.label, rect.x + 12, rect.y + 10, editor.small_font)

    draw_inspector(editor, surface, panel_x)
    draw_help(editor, surface, panel_x)


def draw_tool_button(editor, surface, tool, x, y):
    rect = pygame.Rect(x, y, 82, 42)
    active = editor.tool == tool
    pygame.draw.rect(surface, (72, 101, 82) if active else (38, 49, 59), rect, border_radius=5)
    pygame.draw.rect(surface, (142, 188, 155) if active else (74, 91, 106), rect, 1, border_radius=5)
    text(editor, surface, tool, x + 10, y + 11, editor.small_font)


def draw_inspector(editor, surface, panel_x):
    y = 520
    text(editor, surface, "Inspector", panel_x + 24, y, editor.font)
    if not editor.selected_platform:
        text(editor, surface, "No selection", panel_x + 24, y + 40, editor.small_font, (180, 198, 214))
        return
    vars_obj = editor.selected_platform.vars
    lines = [
        f"x {int(vars_obj.x)}  y {int(vars_obj.y)}",
        f"w {int(vars_obj.width)}  h {int(vars_obj.height)}",
        f"visible {getattr(vars_obj, 'is_visible', True)}",
        f"type {getattr(vars_obj, 'platform_type', 'SOLID')}", # 1. 3종 관통 판정 상태 표시 (기존 pass-through 대체 및 확장)
        f"A/D: W-Scale  W/S: H-Scale",                         # 2. 가로/세로 조작을 위한 단축키 안내 라인 추가
        f"T: Change Platform Type",                             # 3. 판정 변경을 위한 단축키 안내 라인 추가
    ]
    for idx, line in enumerate(lines):
        # 안내 문구는 다른 색상으로 가독성 처리
        color = (140, 160, 180) if idx >= 4 else (213, 225, 235)
        text(editor, surface, line, panel_x + 24, y + 40 + idx * 28, editor.small_font, color)


def draw_help(editor, surface, panel_x):
    y = settings.VIRTUAL_HEIGHT - 210
    lines = [
        "1 place  2 select  3 erase",
        "WASD/arrows pan camera",
        "S save  L reload  Esc menu",
        "[ ] width  ; ' height",
        "V visibility  P pass-through",
    ]
    for idx, line in enumerate(lines):
        text(editor, surface, line, panel_x + 24, y + idx * 30, editor.small_font, (180, 198, 214))


def draw_status(editor, surface):
    pygame.draw.rect(surface, (18, 24, 30), (0, settings.VIRTUAL_HEIGHT - 36, settings.VIRTUAL_WIDTH - editor.SIDEBAR_W, 36))
    text(editor, surface, editor.status_message, 18, settings.VIRTUAL_HEIGHT - 28, editor.small_font, (220, 229, 237))


def text(editor, surface, text_str, x, y, font, color=(238, 242, 245)):
    surface.blit(font.render(str(text_str), True, color), (x, y))
