package com.desertcore.session;

import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class GameSessionManager {
    private final JavaPlugin plugin;
    // 월드 이름을 Key로 하여 세션을 저장 (교통 제어 지도)
    private final Map<String, GameSession> sessionByWorld = new HashMap<>();
    // 플레이어 UUID를 Key로 하여 세션을 매핑 (빠른 유저 추적용)
    private final Map<UUID, GameSession> sessionByPlayer = new HashMap<>();

    public GameSessionManager(JavaPlugin plugin) {
        this.plugin = plugin;
    }

    /**
     * 새로운 사막 게임 세션을 생성하고 장부에 등록합니다.
     */
    public GameSession createSession(String worldName, Player host) {
        GameSession session = new GameSession(worldName, host.getUniqueId());
        
        sessionByWorld.put(worldName, session);
        sessionByPlayer.put(host.getUniqueId(), session);
        
        plugin.getLogger().info("[DesertCore] 새 세션 생성됨 - 월드: " + worldName + " (호스트: " + host.getName() + ")");
        return session;
    }

    /**
     * 플레이어가 속해 있는 세션을 즉시 추적합니다. (지방 도로에서 이 메소드를 호출함)
     */
    public GameSession getSessionByPlayer(Player player) {
        return sessionByPlayer.get(player.getUniqueId());
    }

    /**
     * 월드 이름을 기준으로 세션을 조회합니다.
     */
    public GameSession getSessionByWorld(String worldName) {
        return sessionByWorld.get(worldName);
    }

    /**
     * 게임이 끝나거나 플레이어가 사망/퇴장하여 세션을 종료할 때 장부에서 완전히 제거합니다.
     */
    public void terminateSession(String worldName) {
        GameSession session = sessionByWorld.remove(worldName);
        if (session != null) {
            // 세션에 바인딩된 백그라운드 타이머 전면 강제 종료 (메모리 누수 원천 차단)
            session.clearActiveTimer();
            
            // 플레이어 매핑 장부에서도 제거
            for (UUID uuid : session.getPlayers()) {
                sessionByPlayer.remove(uuid);
            }
            plugin.getLogger().info("[DesertCore] 세션 폐쇄 및 장부 제거 완료 - 월드: " + worldName);
        }
    }
}