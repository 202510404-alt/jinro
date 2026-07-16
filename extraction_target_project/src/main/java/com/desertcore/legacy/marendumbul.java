package com.desertcore.legacy;

import com.desertcore.DesertCore;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import java.util.Random;

public class Marendumbul implements Listener {

    private final DesertCore plugin;
    private final Random random = new Random();
    private final double BUSH_CHANCE = 0.005;

    public Marendumbul(DesertCore plugin) {
        this.plugin = plugin;
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        World world = player.getWorld();

        // 💡 유저가 들어오고 3초(60틱) 뒤에 실행
        Bukkit.getScheduler().runTaskLater(this.plugin, () -> {
            if (!player.isOnline()) return;

            Bukkit.getLogger().info("[DesertCore] 3초 대기 완료! (0, -43, 0) 기준 이중 범위(정리 300, 재생성 100) 연산을 시작합니다.");

            // (0, 0) 기준으로 X축, Z축을 -300부터 +300까지 탐색합니다.
            for (int x = -300; x <= 300; x++) {
                for (int z = -300; z <= 300; z++) {

                    // (0, 0) 좌표로부터의 현재 블록의 거리를 체스판/정사각형 거리(Chebyshev distance) 기준으로 계산
                    int distance = Math.max(Math.abs(x), Math.abs(z));

                    Block targetBlock = world.getBlockAt(x, -43, z);
                    Block underBlock = world.getBlockAt(x, -44, z);

                    // 1. [100 이하 범위] -> 완전 소멸 후 0.5% 확률로 재생성
                    if (distance <= 100) {
                        if (targetBlock.getType() == Material.DEAD_BUSH) {
                            targetBlock.setType(Material.AIR, false);
                        }

                        if (underBlock.getType() == Material.SAND && targetBlock.getType() == Material.AIR) {
                            if (random.nextDouble() < BUSH_CHANCE) {
                                targetBlock.setType(Material.DEAD_BUSH, false);
                            }
                        }
                    }
                    // 2. [101 ~ 300 외곽 범위] -> 오직 기존 덤불 삭제만 진행
                    else {
                        if (targetBlock.getType() == Material.DEAD_BUSH) {
                            targetBlock.setType(Material.AIR, false);
                        }
                    }
                }
            }
            Bukkit.getLogger().info("[DesertCore] 이중 범위 덤불 재배치 및 외곽 청소 완료!");
        }, 60L);
    }
}