package com.desertcore;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.Listener;
import com.desertcore.session.GameSessionManager;
import com.desertcore.legacy.LobbyCommand;

import java.io.File;
import java.net.URL;

public final class DesertCore extends JavaPlugin {
    private GameSessionManager gameSessionManager;

    @Override
    public void onEnable() {
        // 1. 중앙 교통 통제국 가동
        this.gameSessionManager = new GameSessionManager(this);

        // 2. ⚡ [자동화] com.desertcore.legacy 폴더 내부 리스너 자동 등록 가동
        registerAllListenersInPackage("com.desertcore.legacy");

        // 3. 🛡️ 명령어 실행기 예외처리 수동 등록
        if (getCommand("로비") != null) {
            getCommand("로비").setExecutor(new LobbyCommand());
        }

        if (Switch.DEBUG_MODE) {
            getLogger().info("[DEBUG] 패키지 자동 스캔 및 리스너 일괄 등록 프로세스 완료.");
        }
    }

    @Override
    public void onDisable() {
        getLogger().info("DesertCore가 비활성화되었습니다.");
    }

    public GameSessionManager getGameSessionManager() {
        return gameSessionManager;
    }

    private void registerAllListenersInPackage(String packageName) {
        try {
            String path = packageName.replace('.', '/');
            ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
            URL resource = classLoader.getResource(path);
            
            if (resource == null) return;

            File directory = new File(resource.toURI());
            if (!directory.exists()) return;

            File[] files = directory.listFiles();
            if (files == null) return;

            for (File file : files) {
                if (file.getName().endsWith(".class")) {
                    String className = packageName + '.' + file.getName().substring(0, file.getName().length() - 6);
                    Class<?> clazz = Class.forName(className);

                    if (Listener.class.isAssignableFrom(clazz) && !clazz.isInterface()) {
                        try {
                            // 리플렉션을 통해 대문자/소문자 상관없이 규격에 맞으면 인스턴스를 동적 바인딩합니다.
                            Listener listener = (Listener) clazz.getConstructor(DesertCore.class).newInstance(this);
                            getServer().getPluginManager().registerEvents(listener, this);
                            
                            if (Switch.DEBUG_MODE) {
                                getLogger().info("[DEBUG] 자동 로드 성공: " + className);
                            }
                        } catch (Exception e) {
                            getLogger().warning("클래스 동적 생성 실패 (생성자 규격 확인 필요): " + className);
                        }
                    }
                }
            }
        } catch (Exception e) {
            getLogger().severe("패키지 스캔 중 치명적 오류 발생: " + e.getMessage());
        }
    }
}