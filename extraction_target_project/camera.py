import math


class ElasticCamera:
    """
    Dynamic Camera Smoothing / Elastic Camera

    - 기본 원리: Camera_Pos += (Target_Pos - Camera_Pos) * lerp_factor
    - dt(초) 기반으로 보정해 FPS가 달라져도 체감이 비슷하게 유지되도록 처리합니다.
    """

    def __init__(
        self,
        viewport_w: int,
        viewport_h: int,
        *,
        smoothing: float = 0.01,
        deadzone_w: int = 30,
        deadzone_h: int = 20,
        max_speed_px_per_sec: float | None = None,
    ):
        # 카메라가 "바라보려는 중심점" (월드 좌표, float 유지)
        self.x = 0.0
        self.y = 0.0

        self.viewport_w = viewport_w
        self.viewport_h = viewport_h

        self.smoothing = float(smoothing)

        self.deadzone_w = int(deadzone_w)
        self.deadzone_h = int(deadzone_h)

        self.max_speed_px_per_sec = max_speed_px_per_sec

    def set_center(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    @staticmethod
    def _frame_lerp(lerp_60fps: float, dt: float) -> float:
        lerp_60fps = max(0.0, min(1.0, float(lerp_60fps)))
        if dt <= 0:
            return 0.0
        return 1.0 - math.pow(1.0 - lerp_60fps, dt * 60.0)

    def update(
        self,
        target_x: float,
        target_y: float,
        dt: float,
        *,
        clamp_y_max: float | None = None,
    ):
        # 1) 순수한 플레이어 중심점을 기반으로 기본 목표점 설정
        desired_x = float(target_x)
        desired_y = float(target_y)

        # 2) 보정되지 않은 원래 목표점과의 차이(거리)를 기반으로 데드존 계산
        dx = desired_x - self.x
        dy = desired_y - self.y

        half_w = self.deadzone_w / 2.0
        half_h = self.deadzone_h / 2.0

        adj_dx = 0.0
        adj_dy = 0.0

        if dx > half_w:
            adj_dx = dx - half_w
        elif dx < -half_w:
            adj_dx = dx + half_w

        if dy > half_h:
            adj_dy = dy - half_h
        elif dy < -half_h:
            adj_dy = dy + half_h

        # [🌟 수정 핵심 1] 상시 보정 조건 검사
        # 현재 카메라 위치가 main에서 준 제한치보다 아래에 도달해 있다면 데드존 내부여도 강제로 움직이게 처리
        is_outside_clamp = (clamp_y_max is not None) and (self.y > float(clamp_y_max))

        if adj_dx == 0.0 and adj_dy == 0.0 and not is_outside_clamp:
            return

        final_target_x = self.x + adj_dx
        final_target_y = self.y + adj_dy

        # [🌟 수정 핵심 2] 데드존을 적용한 최종 목적지 단계에서 clamp_y_max를 걸어줍니다.
        # 이렇게 해야 main.py에서 의도한 땅의 노출 크기(마진)가 화면 하단에 그대로 유지됩니다.
        if clamp_y_max is not None:
            final_target_y = min(final_target_y, float(clamp_y_max))

        # 3) 거리 비례 Lerp 적용 (dt 보정 포함)
        a = self._frame_lerp(self.smoothing, dt)
        new_x = self.x + (final_target_x - self.x) * a
        new_y = self.y + (final_target_y - self.y) * a

        # 4) 속도 상한
        if self.max_speed_px_per_sec is not None and dt > 0:
            max_delta = float(self.max_speed_px_per_sec) * dt
            delta_x = new_x - self.x
            delta_y = new_y - self.y
            dist = math.hypot(delta_x, delta_y)
            if dist > max_delta and dist > 0:
                scale = max_delta / dist
                new_x = self.x + delta_x * scale
                new_y = self.y + delta_y * scale

        # 5) 최종 위치 안전망 클램핑 (시작 지점이 이미 제한선 밖인 경우의 급격한 Snapping 방지)
        if clamp_y_max is not None and self.y <= clamp_y_max:
            new_y = min(new_y, float(clamp_y_max))

        self.x = new_x
        self.y = new_y

    def get_offset(self) -> tuple[float, float]:
        return (self.x - self.viewport_w / 2.0, self.y - self.viewport_h / 2.0)