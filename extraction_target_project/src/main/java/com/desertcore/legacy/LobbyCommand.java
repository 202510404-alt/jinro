package com.desertcore.legacy; // ⭕ 올바른 패키지 경로 매핑

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;

public class LobbyCommand implements CommandExecutor { // ⭕ 표준 대문자 네이밍

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, @NotNull String[] args) {

        if (!(sender instanceof Player)) {
            sender.sendMessage(Component.text("This command can only be used by in-game players.").color(NamedTextColor.RED));
            return true;
        }

        Player player = (Player) sender;

        if (!player.isOp()) {
            sender.sendMessage(Component.text("❌ You do not have permission to use this command. (OP Only)").color(NamedTextColor.RED));
            return true;
        }

        World lobbyWorld = Bukkit.getWorld("world");
        if (lobbyWorld != null) {
            player.setGameMode(GameMode.SURVIVAL);
            // 시스템 좌표 보존
            Location lobbyLocation = new Location(lobbyWorld, 0.0, -44.0, 17.0, 180f, 0f);
            player.teleport(lobbyLocation);

            player.sendMessage(Component.text("[!] Returned to the lobby via administrator authority.").color(NamedTextColor.GREEN));
        } else {
            player.sendMessage(Component.text("❌ 'world' cannot be found. Please check the world configuration.").color(NamedTextColor.RED));
        }

        return true;
    }
}