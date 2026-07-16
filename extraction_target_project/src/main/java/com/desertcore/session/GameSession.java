package com.desertcore.session;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.scheduler.BukkitTask;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class GameSession {
    private final UUID sessionId;
    private final String worldName;
    private final List<UUID> players;
    
    private int currentWave = 0;
    private BukkitTask activeTimer = null;
    private boolean isTerminating = false;

    // 생성자: 사막 월드가 생성될 때 호출됨
    public GameSession(String worldName, UUID hostPlayerUuid) {
        this.sessionId = UUID.randomUUID();
        this.worldName = worldName;
        this.players = new ArrayList<>();
        this.players.add(hostPlayerUuid);
    }

    // --- Getters & Setters ---
    public UUID getSessionId() { return sessionId; }
    public String getWorldName() { return worldName; }
    
    // 외부에서 플레이어 목록을 함부로 수정하지 못하도록 읽기 전용으로 제공
    public List<UUID> getPlayers() { return Collections.unmodifiableList(players); }
    
    public int getCurrentWave() { return currentWave; }
    public void incrementWave() { this.currentWave++; }

    public boolean isTerminating() { return isTerminating; }
    public void setTerminating(boolean terminating) { this.isTerminating = terminating; }

    // --- 타이머 제어 인프라 ---
    /**
     * 현재 세션에서 실행 중인 스케줄러(사망 카운트다운, 웨이브 타이머 등)를 안전하게 교체합니다.
     * 기존에 돌고 있던 타이머가 있다면 자동으로 중단(cancel)시켜 메모리 누수를 방지합니다.
     */
    public void setActiveTimer(BukkitTask newTimer) {
        clearActiveTimer();
        this.activeTimer = newTimer;
    }

    /**
     * 현재 작동 중인 타이머를 강제로 중지시키고 비웁니다.
     */
    public void clearActiveTimer() {
        if (this.activeTimer != null) {
            try {
                this.activeTimer.cancel();
            } catch (IllegalStateException e) {
                // 이미 종료된 타이머일 경우 예외 발생 방지
            }
            this.activeTimer = null;
        }
    }

    /**
     * 버킷(Bukkit)의 실제 월드 객체를 가져옵니다.
     */
    public World getBukkitWorld() {
        return Bukkit.getWorld(this.worldName);
    }
}