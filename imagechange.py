import os
import cv2
import numpy as np

def convert_strict_outer_white_to_transparent(folder_path):
    if not os.path.exists(folder_path):
        print(f"폴더를 찾을 수 없습니다: {folder_path}")
        return

    # .jpg와 .jpeg 파일만 대상
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]
    
    if not files:
        print(f"변환할 JPG 파일이 없습니다: {folder_path}")
        return

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        # 이미지 읽기
        img = cv2.imread(file_path)
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        # 알파 채널(투명도) 추가 (기본 불투명 255)
        rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        
        # FloodFill용 마스크 생성
        mask = np.zeros((h + 2, w + 2), np.uint8)
        
        # 오차 범위를 (0, 0, 0)으로 설정 -> 오직 시작점과 '완벽히 똑같은 색'만 타고 들어감
        lo_diff = (5, 5, 5)
        up_diff = (5, 5, 5)
        
        # 네 모퉁이에서 시작
        seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        
        for seed in seeds:
            # 시작점의 색상 확인
            b, g, r = img[seed[1], seed[0]]
            
            # 시작점 자체가 완벽한 흰색(255, 255, 255)인 경우에만 탐색 시작
            if r == 255 and g == 255 and b == 255:
                cv2.floodFill(img, mask, seed, (0, 0, 0), lo_diff, up_diff, flags=4 | cv2.FLOODFILL_MASK_ONLY)
        
        # 마스크 슬라이싱 (원래 이미지 크기로)
        actual_mask = mask[1:h+1, 1:w+1]
        
        # 외곽 완벽한 흰색 부분만 투명화
        rgba[actual_mask == 1, 3] = 0

        # 새 확장자 설정 (.png)
        new_filename = os.path.splitext(filename)[0] + ".png"
        save_path = os.path.join(folder_path, new_filename)
        
        # 이미지 저장
        cv2.imwrite(save_path, rgba)
        print(f"엄격한 외곽 투명화 완료: {filename} -> {new_filename}")

# 대상 폴더 리스트
target_folders = [
    "extraction_target_project/assets/images/player/attack_effect",
    "extraction_target_project/assets/images/player/player_move"
]

# 작업 실행
for folder in target_folders:
    print(f"\n--- {folder} 엄격한 외곽 투명화 작업 시작 ---")
    convert_strict_outer_white_to_transparent(folder)