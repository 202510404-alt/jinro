# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
<<<<<<< HEAD
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/src/main/java/com/desertcore/lobbycmd.java (1-49라인)
# ----------------------------------------------------------
```python
package com.desertcore;

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

public class lobbycmd implements CommandExecutor {

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, @NotNull String[] args) {

        // 1. 명령어를 친 대상이 플레이어인지 확인 (콘솔창 입력 방지)
        if (!(sender instanceof Player)) {
            sender.sendMessage(Component.text("이 명령어는 인게임 플레이어만 사용할 수 있습니다.").color(NamedTextColor.RED));
            return true;
        }

        Player player = (Player) sender;

        // 2. [핵심] 오퍼레이터(OP) 권한이 있는지 체크
        if (!player.isOp()) {
            player.sendMessage(Component.text("❌ 이 명령어를 사용할 권한이 없습니다. (OP 전용)").color(NamedTextColor.RED));
            return true;
        }

        // 3. 로비 월드("world") 정보 가져오기
        World lobbyWorld = Bukkit.getWorld("world");
        if (lobbyWorld != null) {
            // 서바이벌 모드로 안전하게 변경 후 지정된 로비 좌표로 텔레포트
            player.setGameMode(GameMode.SURVIVAL);
            Location lobbyLocation = new Location(lobbyWorld, 0.0, -44.0, 17.0, 180f, 0f);
            player.teleport(lobbyLocation);

            player.sendMessage(Component.text("[!] 관리자 권한으로 로비에 강제 복귀했습니다.").color(NamedTextColor.GREEN));
        } else {
            player.sendMessage(Component.text("❌ 'world' 월드를 찾을 수 없습니다. 월드 이름을 확인해 주세요.").color(NamedTextColor.RED));
        }

        return true;
    }
}
```

# 📄 [요청 2] TARGET: extraction_target_project/src/main/java/com/desertcore/legacy/samakportal.java (1-60라인)
# ----------------------------------------------------------
```python
package com.desertcore.legacy;

import com.desertcore.DesertCore;
import com.desertcore.Switch;
import com.desertcore.session.GameSession;
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

public class samakportal implements Listener {

    private final DesertCore plugin;

    public samakportal(DesertCore plugin) {
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
                if (Switch.DEBUG_MODE) {
                    plugin.getLogger().warning("[DEBUG] " + player.getName() + " 진입 거부: 이미 세션 존재함 또는 전장 월드에 있음.");
                }
                return;
            }

            player.sendMessage(Component.text("⏳ 새로운 전장(사본)을 생성하고 있습니다. 잠시만 기다려주세요...").color(NamedTextColor.YELLOW));

            String templateName = "desert_template";
            String instanceName = "desert_" + player.getUniqueId().toString().substring(0, 8);

            File serverDir = Bukkit.getWorldContainer();
```

# 📄 [요청 3] TARGET: extraction_target_project/src/main/java/com/desertcore/legacy/deathevent.java (35-80라인)
# ----------------------------------------------------------
```python
public class deathevent implements Listener {

    private final DesertCore plugin;
    private final HashSet<UUID> promptActive = new HashSet<>();

    public deathevent(DesertCore plugin) {
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
=======
# [주의] 코드를 리팩토링/분석/작성할 때 아래 핵심 최적화 규칙을 엄격히 준수하십시오.
#
# 1. 라벨 무시: 코드 행 앞의 '[001]' 등 숫자 마커는 절대 줄번호 사격 좌표입니다.
#              새 코드를 출력할 때는 이 숫자 태그를 완전히 제외하고 순수 코드만 출력하십시오.
# 2. 로그 중심: 설명 주석 작성을 기피하고, 대신 On/Off 가변 스위치가 달린 촘촘한 디버깅 로그를
#              도배 수준으로 짜십시오. 메인 실행 파일 없이 로그 흐름만으로 작동 상태를 유추하게 만듭니다.
# 3. 구조 유지: 프로젝트 내 기존 클래스/함수명 명세 및 self.vars 데이터 프로토콜은 엄격히 준수하십시오.
# 4. 환각 방지: 존재하지 않는 가짜 함수 창조 절대 금지! 절대값 연산은 순정 내장 함수 abs()를 쓰십시오.
# 5. 개발 자유: 위 최소 조건 내에서 알고리즘, 물리 수식, 이동 로직은 자유롭고 창의적으로 짜십시오.
# ==========================================================================
# 📄 [요청 1] TARGET: tools/universal_indexer/indexer.py (115-145라인)
# ----------------------------------------------------------
```python
                    total_ignored_count += 1

        log(f"🏁 스캔 타임라인 종료 -> 분석 통계 [처리 완료: {total_scanned_count}개 | 미지원/패스: {total_ignored_count}개]")

        # 🗂️ 수집 완료 후 디스크 정밀 장부 보관소로 직행 쓰기
        self.save_index_data()

    def index_file(self, file_path: Path, ext: str):
        """개별 파일을 파서를 통해 쪼개어 마스터 장부에 바느질합니다."""
        try:
            rel_path_str = file_path.relative_to(self.project_root).as_posix()
        except ValueError:
            rel_path_str = file_path.resolve().relative_to(self.project_root.resolve()).as_posix()

        log(f"🧵 [장부 바느질 개시] 상대 경로 키: '{rel_path_str}'")
        parser_func = self.parsers[ext]
        
        try:
            log(f"   📡 플러그인 함수 {parser_func.__name__} 원격 연산 제어권 이양 중...")
            res = parser_func(file_path, self.project_root)
            
            if not res or len(res) < 5:
                log(f"   ⚠️ [규격 위반] '{rel_path_str}' 파서의 반환 데이터가 5대 규격을 충족하지 못해 드롭합니다.")
                return

            f_symbols, f_context, f_def_map, f_protocols, f_registry = res

            # 데이터 적재 현황 세부 체크 로그
            log(f"   📥 수집 결과 피드백 받음 -> 심볼: {len(f_symbols)}개, 정의 매핑: {len(f_def_map)}개, 프로토콜: {len(f_protocols)}개, 레지스트리: {len(f_registry)}개")

            # 1. 글로벌 심볼 리스트 누적
```

# 📄 [요청 2] TARGET: tools/universal_indexer/create_ai_map.py (101-135라인)
# ----------------------------------------------------------
```python
def collect_target_files():
    """[수정] .py 제한을 해제하고, 제외 키워드가 없는 프로젝트 내의 '모든 파일'을 수집합니다."""
    if SCAN_MODE == "ROOT":
        scan_target = PROJECT_ROOT
        print("🎯 [create_ai_map] Mode: ROOT (프로젝트 전체 경로를 직접 스캔합니다)")
    else:
        scan_target = PROJECT_ROOT / "src"
        print("🎯 [create_ai_map] Mode: SRC (src/ 폴더 내부만 정밀 스캔합니다)")

    if not scan_target.exists():
        print(f"❌ [오류] 스캔 대상 경로가 존재하지 않습니다: {scan_target}")
        return []

    target_files = []
    for root, dirs, files in os.walk(scan_target, followlinks=True):
        normalized_root = root.replace("\\", "/")

        if "src/project_root/src" in normalized_root:
            continue
        if any(kw in normalized_root for kw in EXCLUDE_KEYWORDS):
            continue

        for file in files:
            if file == "start.py" and SCAN_MODE == "SRC":
                continue
            
            # 💡 [교정] 특정 확장자 차단 해제 -> 모든 파일을 수집 대상으로 포함
            target_files.append(Path(root) / file)

    return sorted(target_files)


def load_registry():
    """
    🔑 [Universal Registry Loader]
```

# 📄 [요청 3] TARGET: tools/universal_indexer/indexer.py (200-202라인)
# ----------------------------------------------------------
```python
if __name__ == "__main__":
    indexer = AdvancedIndexerV2(PROJECT_ROOT)
    indexer.scan_project()
```

# 📄 [요청 4] TARGET: tools/universal_indexer/create_ai_map.py (110-135라인)
# ----------------------------------------------------------
```python
    if not scan_target.exists():
        print(f"❌ [오류] 스캔 대상 경로가 존재하지 않습니다: {scan_target}")
        return []

    target_files = []
    for root, dirs, files in os.walk(scan_target, followlinks=True):
        normalized_root = root.replace("\\", "/")

        if "src/project_root/src" in normalized_root:
            continue
        if any(kw in normalized_root for kw in EXCLUDE_KEYWORDS):
            continue

        for file in files:
            if file == "start.py" and SCAN_MODE == "SRC":
                continue
            
            # 💡 [교정] 특정 확장자 차단 해제 -> 모든 파일을 수집 대상으로 포함
            target_files.append(Path(root) / file)

    return sorted(target_files)


def load_registry():
    """
    🔑 [Universal Registry Loader]
>>>>>>> 79e67b921324292ffe056387f30e76530bd562d9
```
