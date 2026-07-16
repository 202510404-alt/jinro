# map_system/map_settings.py

# 🗺️ 맵 전체 크기 설정
DEFAULT_MAP_WIDTH = 1600   # 맵 전체 가로 길이
DEFAULT_MAP_HEIGHT = 600   # 맵 전체 세로 길이

# 🖼️ 배경(Background) 관련 설정
# 나중에 배경 이미지 한 장의 크기가 가로 800, 세로 600이라고 가정합니다.
DEFAULT_BG_WIDTH = 800     
DEFAULT_BG_HEIGHT = 600    
DEFAULT_BACKGROUND_TYPE = "bg_sky" # assets에 들어갈 이미지 파일명 매칭용

# 🪵 바닥(Ground) 관련 설정
# 바닥 타일 도트 한 장이 가로 64, 세로 64 픽셀짜리 블록이라고 가정합니다.
DEFAULT_GROUND_TILE_WIDTH = 64
DEFAULT_GROUND_TILE_HEIGHT = 64
DEFAULT_GROUND_Y = 536     # 타일 높이(64)를 고려해 플레이어가 딛을 Y축 위치 설정
DEFAULT_GROUND_TYPE = "ground_dirt" # assets에 들어갈 이미지 파일명 매칭용