# src/platform_system/platform_main.py
import pygame
import sys
import os
from platform_system.variables import PlatformVariables

class Platform:
    def __init__(self, x, y, width=200, height=30, **kwargs):
        self.vars = PlatformVariables(x, y, width, height, **kwargs)
        self.load_image()

    def load_image(self):
        # 🌟 현재 파일(src/platform_system/platform_main.py) 위치 기준 상위 src/ 폴더 추적
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_dir = os.path.join(src_dir, "assets", "images", "platform")
        
        try:
            self.image = pygame.image.load(os.path.join(img_dir, "platform_brick.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.vars.width, self.vars.height))
        except pygame.error as e:
            print(f"\n❌ 에러: 플랫폼 이미지를 로드할 수 없습니다. ({e})")
            print(f"참조 실패한 디렉터리: {img_dir}")
            pygame.quit()
            sys.exit()

    def update(self):
        pass

    def draw(self, screen, camera_offset=(0, 0)):
        """🌟 플랫폼이 보임 처리되어 있다면 화면에 그립니다."""
        if self.vars.is_visible:
            ox, oy = camera_offset
            screen.blit(self.image, (self.vars.x - ox, self.vars.y - oy))