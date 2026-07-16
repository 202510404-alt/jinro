# player/physics_processor.py
import pygame
from settings import SCREEN_WIDTH, GROUND_Y

class PlayerPhysicsProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, platforms, game_map=None, dt=1.0/60.0):
        # 1. Y축 좌표를 업데이트하기 전에 '이전 발끝 위치'를 먼저 기록
        old_bottom = vars_obj.y + vars_obj.height

        # 가변 프레임 환경(dt)에 맞춘 가속 스케일러 연산
        fps_scale = dt * 60.0

        # 중력 적용 및 Y축 좌표 실제 이동
        vars_obj.vertical_velocity += vars_obj.gravity * fps_scale
        vars_obj.y += vars_obj.vertical_velocity * fps_scale

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 정밀 검사
        for platform in platforms:
            # [GHOST 분기] 통과형 플랫폼은 연산에서 제외
            if not platform.vars.is_solid:
                continue
                
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            
            if player_rect.colliderect(plat_rect):
                # ─── A. 하강/낙하 중일 때 (착지 처리: SOLID & ONE_WAY 공통) ───
                if vars_obj.vertical_velocity > 0:
                    # [하드코딩 제거] 매직 넘버 12 대신 낙하 속도와 프레임 보정치를 연동한 동적 착지 임계값 산출
                    dynamic_threshold = max(12.0, vars_obj.vertical_velocity * fps_scale + 2.0)
                    
                    if old_bottom <= platform.vars.y + dynamic_threshold:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        
                        # 💡 [차후 기능 확장 가드] 플랫폼 객체에 특수 밟기 기믹(무너짐 등) 기능이 있다면 동적 호출
                        if hasattr(platform, "on_stepped"):
                            platform.on_stepped(vars_obj, dt)
                        break
                
                # ─── B. 점프 상승 중일 때 (천장 충돌 처리: ONLY SOLID) ───
                elif vars_obj.vertical_velocity < 0:
                    # 아래에서 위로 통과할 수 없는 플랫폼 유형인 경우에만 정수리를 막음
                    if not platform.vars.passable_from_bottom:
                        # 이전 프레임의 머리 꼭대기 위치를 가변 dt 스케일에 맞춰 정확하게 역산
                        old_top = vars_obj.y - (vars_obj.vertical_velocity * fps_scale)
                        if old_top >= platform.vars.y + platform.vars.height:
                            vars_obj.y = platform.vars.y + platform.vars.height
                            vars_obj.vertical_velocity = 0 
                            
                            # 💡 [차후 기능 확장 가드] 천장 충돌 시 플랫폼 특수 기믹(스위치 작동 등) 확장 인터페이스
                            if hasattr(platform, "on_head_bump"):
                                platform.on_head_bump(vars_obj, dt)

        # 맵 시스템의 메인 바닥 착지 처리
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # 좌측 화면 경계 밖 이탈 제어
        if vars_obj.x < 0:
            vars_obj.x = 0

        # 우측 화면/월드 경계 밖 이탈 제어 (유동적 가변 맵 대응 너비 반영)
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width