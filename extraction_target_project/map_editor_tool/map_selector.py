import os

import pygame

import settings


def scan_map_files(editor):
    return sorted(
        file_name
        for file_name in os.listdir(editor.maps_dir)
        if file_name.lower().endswith(".json") and os.path.isfile(os.path.join(editor.maps_dir, file_name))
    )


def build_map_selection_buttons(editor):
    editor.map_select_buttons = []
    button_w = 560
    button_h = 54
    start_x = (settings.VIRTUAL_WIDTH - button_w) // 2
    start_y = 310

    # 1. 기존 존재하는 맵 파일 리스트 버튼 생성
    for idx, file_name in enumerate(editor.map_files):
        rect = pygame.Rect(start_x, start_y + idx * 68, button_w, button_h)
        editor.map_select_buttons.append((file_name, rect))

    # 2. 리스트 아래에 유연하게 이어 붙을 Y축 시작점 계산
    new_y = start_y + max(len(editor.map_files), 1) * 68 + 10

    # 🎯 [오류 원인 해결] 누락되었던 새 맵 생성 버튼과 메인메뉴 복귀 버튼 할당
    editor.new_map_button = pygame.Rect(start_x, new_y, button_w, button_h)
    editor.back_button = pygame.Rect(start_x, new_y + 68, button_w, button_h)


def handle_select_event(editor, event, mouse_virtual):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return editor._app_state("MENU")
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return None

    for file_name, rect in editor.map_select_buttons:
        if rect.collidepoint(mouse_virtual):
            editor.load_map(file_to_map_name(file_name), file_name)
            return None

    if editor.new_map_button.collidepoint(mouse_virtual):
        file_name = next_new_map_file(editor)
        editor.load_map(file_to_map_name(file_name), file_name)
        return None

    if editor.back_button.collidepoint(mouse_virtual):
        return editor._app_state("MENU")
    return None


def file_to_map_name(file_name):
    stem = os.path.splitext(file_name)[0]
    if stem.startswith("map_"):
        return stem[4:]
    if stem.startswith("map") and stem[3:].isdigit():
        return stem[3:]
    return stem


def map_name_to_file(map_name):
    if map_name is None:
        return None
    name = str(map_name)
    if name.startswith("map") and name.endswith(".json"):
        return name
    if name.isdigit():
        return f"map{name}.json"
    return f"map_{name}.json"


def next_new_map_file(editor):
    base = "map_new.json"
    if base not in editor.map_files and not os.path.exists(os.path.join(editor.maps_dir, base)):
        return base
    idx = 1
    while True:
        file_name = f"map_new_{idx}.json"
        if file_name not in editor.map_files and not os.path.exists(os.path.join(editor.maps_dir, file_name)):
            return file_name
        idx += 1
