# map_system/variables.py
import math
from map_system.map_settings import *
import settings

class MapVariables:
    def __init__(self, map_id=1, width=None, height=None):
        """
        맵 전체 크기에 맞춰 배경과 바닥 이미지를 
        몇 개나 이어 붙여야 하는지 계산하고 저장하는 설계도
        """
        if isinstance(map_id, dict):
            settings_dict = map_id
            self.map_id = settings_dict.get("map_id", 1)
            self.width = settings_dict.get("width") or settings_dict.get("map_width") or DEFAULT_MAP_WIDTH
            self.height = settings_dict.get("height") or settings_dict.get("map_height") or DEFAULT_MAP_HEIGHT
            self.background_type = settings_dict.get("background_type") or DEFAULT_BACKGROUND_TYPE
            self.ground_type = settings_dict.get("ground_type") or DEFAULT_GROUND_TYPE
            self.ground_y = settings_dict.get("ground_y") or DEFAULT_GROUND_Y
        else:
            self.map_id = map_id
            self.width = width if width is not None else DEFAULT_MAP_WIDTH
            self.height = height if height is not None else DEFAULT_MAP_HEIGHT
            self.background_type = DEFAULT_BACKGROUND_TYPE
            self.ground_type = DEFAULT_GROUND_TYPE
            self.ground_y = DEFAULT_GROUND_Y

        # 1. 🖼️ 배경 데이터 및 이어 붙일 개수 계산
        self.bg_width = DEFAULT_BG_WIDTH
        self.bg_height = DEFAULT_BG_HEIGHT
        # 맵 전체를 채우기 위해 가로로 몇 장을 이어 붙여야 하는지 계산 (올림 처리)
        self.bg_repeat_count = math.ceil(self.width / self.bg_width) # 1600 / 800 = 2장
        
        # 2. 🪵 바닥 데이터 및 이어 붙일 개수 계산
        self.ground_tile_width = DEFAULT_GROUND_TILE_WIDTH
        self.ground_tile_height = DEFAULT_GROUND_TILE_HEIGHT

        # ============================================================
        # 🗺️ 카메라 잘림 방지를 위한 좌우 패딩값(월드 좌표 기준)
        # - 카메라가 맵 끝으로 이동할 때 화면의 양쪽이 비지 않도록
        #   바닥 타일을 더 넓게 그립니다.
        # - 값은 settings.py에서 관리합니다(하드코딩 금지).
        self.ground_draw_padding_x = float(getattr(settings, "MAP_PADDING_X", 0.0))
        # 맵 끝까지 바닥 타일을 몇 개나 도장 찍어야 하는지 계산
        self.ground_repeat_count = math.ceil(self.width / self.ground_tile_width) # 1600 / 64 = 25개
        
        # 3. 🧱 구조물 리스트 (기존 유지)
        self.platform_data_list = []
        self.trap_data_list = []