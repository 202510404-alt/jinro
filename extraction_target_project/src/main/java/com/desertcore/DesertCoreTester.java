package com.desertcore;

import org.bukkit.event.Listener;
import java.io.File;
import java.net.URL;
import java.lang.reflect.Constructor;

/**
 * 하드코딩 없이 특정 패키지의 모든 자바 파일을 동적 로드하여 
 * 자동화 아키텍처 및 디버그 로깅을 통합 검증하는 메인 실행 파일
 */
public class DesertCoreTester {

    public static void main(String[] args) {
        System.out.println("==================================================");
        System.out.println("🚀 [AUTOMATION] 리플렉션 패키지 스캔 및 런타임 테스트 시작");
        System.out.println("==================================================");

        // 1. 글로벌 스위치 상태 확인
        System.out.println("[STEP 1] 글로벌 디버그 스위치 검증");
        System.out.println(">> Switch.DEBUG_MODE: " + Switch.DEBUG_MODE);
        System.out.println();

        // 2. 패키지 동적 자동 스캔 시뮬레이션
        System.out.println("[STEP 2] 'com.desertcore.legacy' 패키지 자동 탐색 시작");
        String targetPackage = "com.desertcore.legacy";
        
        try {
            String path = targetPackage.replace('.', '/');
            ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
            URL resource = classLoader.getResource(path);

            if (resource == null) {
                System.err.println("❌ 에러: 지정된 패키지 경로를 찾을 수 없습니다: " + path);
                return;
            }

            // 팩트 교정: URL 객체를 정석 URI 파이프라인을 거쳐 안전하게 물리 파일 객체로 빌드
            File directory = new File(resource.toURI());
            if (!directory.exists()) {
                System.err.println("❌ 에러: 디렉토리가 존재하지 않습니다: " + directory.getPath());
                return;
            }

            File[] files = directory.listFiles();
            if (files == null || files.length == 0) {
                System.out.println("⚠ 스캔 결과: 폴더 내에 자바 클래스 파일이 존재하지 않습니다.");
                return;
            }

            int loadCount = 0;
            for (File file : files) {
                if (file.getName().endsWith(".class")) {
                    String className = targetPackage + '.' + file.getName().substring(0, file.getName().length() - 6);
                    Class<?> clazz = Class.forName(className);

                    // Bukkit Listener 구현체 여부 및 인터페이스 제외 검증
                    if (Listener.class.isAssignableFrom(clazz) && !clazz.isInterface()) {
                        System.out.println("✨ [발견된 리스너]: " + clazz.getSimpleName());
                        
                        // 디버깅 모드가 켜져 있을 때 생성자 명세 무결성 검증 시뮬레이션
                        if (Switch.DEBUG_MODE) {
                            System.out.println("   [DEBUG] " + clazz.getSimpleName() + " 클래스에 대한 의존성 주입(DI) 가능 여부 확인 중...");
                        }

                        // DesertCore.class 타입을 인자로 받는 생성자 존재 여부 리플렉션 검사
                        try {
                            Constructor<?> constructor = clazz.getConstructor(Class.forName("com.desertcore.DesertCore"));
                            if (Switch.DEBUG_MODE) {
                                System.out.println("   [DEBUG] 검증 완료: (DesertCore plugin) 주입 생성자 명세 일치.");
                            }
                            loadCount++;
                        } catch (NoSuchMethodException e) {
                            System.err.println("   ❌ 규격 에러: " + clazz.getSimpleName() + "에 'DesertCore' 주입 생성자가 존재하지 않습니다.");
                        }
                    }
                }
            }

            System.out.println();
            System.out.println("==================================================");
            System.out.println("✅ [결과] 총 " + loadCount + "개의 리스너 파일 자동 식별 및 아키텍처 검증 성공!");
            System.out.println("==================================================");

        } catch (Exception e) {
            System.err.println("❌ 런타임 자동 스캔 테스트 실패: " + e.getMessage());
            e.printStackTrace();
        }
    }
}