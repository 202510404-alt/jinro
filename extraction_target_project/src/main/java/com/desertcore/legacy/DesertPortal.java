package com.desertcore.legacy;

import com.desertcore.DesertCore;
import com.desertcore.Switch;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.WorldCreator;
import org.bukkit.entity.Player;
import org.bukkit.entity.Villager;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerInteractEntityEvent;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.logging.Level;

public class DesertPortal implements Listener {

    private final DesertCore plugin;

    // 대소문자 및 파일명 불일치 결함 정밀 수술 완료
    public DesertPortal(DesertCore plugin) {
        this.plugin = plugin;
    }

    @EventHandler
    public void onVillagerClick(PlayerInteractEntityEvent event) {
        if (!(event.getRightClicked() instanceof Villager villager)) {
            return;
        }

        if (villager.getScoreboardTags().contains("desert_npc")) {
            event.setCancelled(true);
            Player player = event.getPlayer();

            if (Switch.DEBUG_MODE) {
                plugin.getLogger().info("[DEBUG] " + player.getName() + "이(가) desert_npc 상호작용 감지됨.");
            }

            if (plugin.getGameSessionManager().getSessionByPlayer(player) != null || player.getWorld().getName().startsWith("desert_")) {
                player.sendMessage(Component.text("[!] 이미 전장 월드에 진입했거나 세션이 할당된 상태입니다.").color(NamedTextColor.RED));
                return;
            }

            player.sendMessage(Component.text("⏳ 새로운 전장(사본)을 생성하고 있습니다. 잠시만 기다려주세요...").color(NamedTextColor.YELLOW));

            String templateName = "desert_template";
            String instanceName = "desert_" + player.getUniqueId().toString().substring(0, 8);

            File serverDir = Bukkit.getWorldContainer();
            File templateDir = new File(serverDir, templateName);
            File instanceDir = new File(serverDir, instanceName);

            if (!templateDir.exists()) {
                player.sendMessage(Component.text("❌ 서버에 '" + templateName + "' 원본 폴더가 없습니다! 관리자에게 문의하세요.").color(NamedTextColor.RED));
                return;
            }

            Bukkit.getScheduler().runTaskAsynchronously(plugin, () -> {
                try {
                    if (instanceDir.exists()) {
                        deleteDirectoryNative(instanceDir.toPath());
                    }

                    copyDirectoryNative(templateDir.toPath(), instanceDir.toPath());

                    File uidFile = new File(instanceDir, "uid.dat");
                    if (uidFile.exists()) {
                        uidFile.delete();
                    }

                    Bukkit.getScheduler().runTask(plugin, () -> {
                        World copiedWorld = Bukkit.createWorld(new WorldCreator(instanceName));
                        if (copiedWorld != null) {
                            plugin.getGameSessionManager().createSession(instanceName, player);

                            Location desertLocation = new Location(copiedWorld, 0.0, -43.0, 0.0, 180f, 0f);
                            player.teleport(desertLocation);
                            player.setGameMode(GameMode.SURVIVAL);
                            player.sendMessage(Component.text("[!] 전장(사막 맵)으로 이동했습니다!").color(NamedTextColor.YELLOW));
                        } else {
                            player.sendMessage(Component.text("❌ 월드 로딩 중 오류가 발생했습니다.").color(NamedTextColor.RED));
                        }
                    });

                } catch (IOException e) {
                    player.sendMessage(Component.text("❌ 전장 맵 데이터 복사 중 오류가 발생했습니다.").color(NamedTextColor.RED));
                    plugin.getLogger().log(Level.SEVERE, "전장 복사 중 예외 발생: ", e);
                }
            });
        }
    }

    private void copyDirectoryNative(Path source, Path target) throws IOException {
        Files.walkFileTree(source, new SimpleFileVisitor<>() {
            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
                Path targetDir = target.resolve(source.relativize(dir));
                if (!Files.exists(targetDir)) {
                    Files.createDirectories(targetDir);
                }
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                Files.copy(file, target.resolve(source.relativize(file)), StandardCopyOption.REPLACE_EXISTING);
                return FileVisitResult.CONTINUE;
            }
        });
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