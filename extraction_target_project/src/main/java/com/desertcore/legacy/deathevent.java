package com.desertcore.legacy;

import com.desertcore.DesertCore;
import com.desertcore.Switch;
import com.desertcore.session.GameSession;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerRespawnEvent;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.scheduler.BukkitTask;

import java.io.File;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.HashSet;
import java.util.UUID;

public class DeathEvent implements Listener {

    private final DesertCore plugin;
    private final HashSet<UUID> promptActive = new HashSet<>();

    public DeathEvent(DesertCore plugin) {
        this.plugin = plugin;
    }

    @EventHandler
    public void onPlayerDeath(PlayerDeathEvent event) {
        Player player = event.getEntity();
        String currentWorld = player.getWorld().getName();

        if (currentWorld.startsWith("desert_")) {
            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + " 전장 내 사망 감지. 인벤토리 보존 활성화.");
            event.setKeepInventory(true);
            event.getDrops().clear();

            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + " 강제 즉시 리스폰 패킷 전송.");
                player.spigot().respawn();
            }, 1L);
        }
    }

    @EventHandler
    public void onPlayerRespawn(PlayerRespawnEvent event) {
        Player player = event.getPlayer();
        String currentWorld = player.getWorld().getName();

        if (currentWorld.startsWith("desert_")) {
            event.setRespawnLocation(player.getLocation());
            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + " 리스폰 위치 고정.");

            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                player.setGameMode(GameMode.SPECTATOR);
                promptActive.remove(player.getUniqueId());
                
                GameSession session = plugin.getGameSessionManager().getSessionByPlayer(player);
                if (session != null) {
                    if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 세션 장부 확인됨. 기존 활성 타이머 초기화 클리어 시도.");
                    session.clearActiveTimer();
                }

                player.sendMessage(Component.text("\n☠️ 전장에서 전사하셨습니다. 관전자 모드로 전환됩니다.").color(NamedTextColor.RED));
                player.sendMessage(Component.text("💡 [Shift](웅크리기) 키를 3초간 꾹 누르면 로비로 돌아갈 수 있습니다.\n").color(NamedTextColor.GRAY));
            }, 1L);
        }
    }

    @EventHandler
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        UUID uuid = player.getUniqueId();
        String currentWorld = player.getWorld().getName();

        if (player.getGameMode() == GameMode.SPECTATOR && currentWorld.startsWith("desert_")) {
            GameSession session = plugin.getGameSessionManager().getSessionByPlayer(player);
            if (session == null) return;

            if (player.isSneaking()) {
                if (promptActive.contains(uuid) || session.isTerminating()) return;

                // 타이머가 돌고 있지 않을 때만 타스크 새로 할당
                // 무한 스폰 방지를 위해 세션 내부의 실제 타이머 참조 상태를 직접 식별 검증해야 함
                // (기존 스토리지 구조가 이관되었으므로 호출 컨텍스트 직접 추적)
                // 현재 세션 타스크가 물리적으로 바인딩되어 작동하는지 런타임 추적 로깅 추가
                if (Switch.DEBUG_MODE) {
                    plugin.getLogger().info("[DEBUG] " + player.getName() + " 관전자 웅크리기 진입. 스케줄러 스폰 루프 검증 요구.");
                }

                BukkitRunnable runnableTimer = new BukkitRunnable() {
                    int timeLeft = 3;

                    @Override
                    public void run() {
                        if (!player.isOnline() || player.getGameMode() != GameMode.SPECTATOR) {
                            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 스케줄러 중단: 온라인 아님 또는 스펙테이터 해제됨.");
                            session.clearActiveTimer();
                            return;
                        }
                        if (!player.isSneaking()) {
                            player.sendMessage(Component.text("❌ Shift 키를 떼어 로비 복귀가 취소되었습니다.").color(NamedTextColor.RED));
                            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + "가 Shift 키를 떼어 세션 타이머 청소.");
                            session.clearActiveTimer();
                            return;
                        }

                        if (timeLeft > 0) {
                            player.sendMessage(Component.text("⏳ 로비 복귀 준비 중... " + timeLeft + "초").color(NamedTextColor.YELLOW));
                            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 카운트다운 진행 중: " + timeLeft + "초");
                            timeLeft--;
                        } else {
                            if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 카운트다운 완료. UI 버튼 프롬프트 표출.");
                            session.clearActiveTimer();
                            promptActive.add(uuid);

                            player.sendMessage(Component.text("\n[ 시스템 ] 로비로 돌아가시겠습니까?").color(NamedTextColor.GOLD));
                            Component yesButton = Component.text("[ 예 ]").color(NamedTextColor.GREEN).decorate(TextDecoration.BOLD).clickEvent(ClickEvent.runCommand("/lobby_confirm"));
                            Component noButton = Component.text("[ 아니오 ]").color(NamedTextColor.RED).decorate(TextDecoration.BOLD).clickEvent(ClickEvent.runCommand("/lobby_cancel"));
                            player.sendMessage(Component.text("👉 ").append(yesButton).append(Component.text("  |  ")).append(noButton).append(Component.text("\n")));
                        }
                    }
                };

                BukkitTask registeredTask = runnableTimer.runTaskTimer(plugin, 0L, 20L);
                session.setActiveTimer(registeredTask);

            } else {
                // 움직였으나 언스니킹인 경우 잔여 타이머 일괄 파쇄
                session.clearActiveTimer();
            }
        }
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        World lobbyWorld = Bukkit.getWorld("world");
        String previousWorldName = player.getWorld().getName();

        if (lobbyWorld != null) {
            GameSession session = plugin.getGameSessionManager().getSessionByPlayer(player);
            if (session != null) {
                if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + " 재접속 감지. 기존 세션 타이머 파쇄.");
                session.clearActiveTimer();
            }
            
            player.setGameMode(GameMode.SURVIVAL);
            Location lobbyLocation = new Location(lobbyWorld, 0.0, -43.0, 0.0, 0f, 0f);
            player.teleport(lobbyLocation);

            if (previousWorldName.startsWith("desert_")) {
                if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + player.getName() + " 전장 이탈 재접속 확인. 해당 사본 인스턴스 정리 유도.");
                unloadAndDeleteInstance(previousWorldName);
            }
        }
    }

    private void unloadAndDeleteInstance(String instanceName) {
        GameSession session = plugin.getGameSessionManager().getSessionByWorld(instanceName);
        if (session != null) {
            session.setTerminating(true);
            session.clearActiveTimer();
        }

        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            World instanceWorld = Bukkit.getWorld(instanceName);
            if (instanceWorld != null) {
                if (instanceWorld.getPlayers().isEmpty()) {
                    if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] " + instanceName + " 내 인원 전원 전멸 확인. 월드 Unload 진입.");
                    Bukkit.unloadWorld(instanceWorld, false);

                    plugin.getGameSessionManager().terminateSession(instanceName);

                    Bukkit.getScheduler().runTaskAsynchronously(plugin, () -> {
                        File instanceDir = new File(Bukkit.getWorldContainer(), instanceName);
                        if (instanceDir.exists()) {
                            try {
                                if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 비동기 하드디스크 사본 잔재 폴더 파쇄 트리 시작.");
                                deleteDirectoryNative(instanceDir.toPath());
                                if (Switch.DEBUG_MODE) plugin.getLogger().info("[DEBUG] 비동기 폴더 파쇄 완전히 끝남.");
                            } catch (IOException e) {
                                plugin.getLogger().warning(instanceName + " 사본 월드 폴더 삭제 중 예외 발생");
                            }
                        }
                    });
                }
            }
        }, 20L);
    }

    private void deleteDirectoryNative(Path path) throws IOException {
        Files.walkFileTree(path, new SimpleFileVisitor<>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                Files.delete(file);
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                Files.delete(dir);
                return FileVisitResult.CONTINUE;
            }
        });
    }
}