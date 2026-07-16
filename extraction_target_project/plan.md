마인크래프트 FPS 타워디펜스 플러그인 — 기술 설계 문서 (Technical Design Document)

버전: v0.1 (Draft)
작성 기준 환경: IntelliJ IDEA / Gradle / Java 21 / Paper 1.21.1
문서 성격: 실제 구현에 착수 가능한 수준의 아키텍처 설계 문서 (코드 제외, 구조·클래스·인터페이스·이벤트·데이터 흐름 중심)


0. 문서 개요 및 설계 철학

0.1 이 문서의 목적

이 문서는 기획 회의에서 확정된 게임 콘텐츠(코어 방어, 광산 클리커, NPC 육성, 9직업 27전문화, 장벽/포탑, 웨이브 로그라이크 성장)를 실제 Paper 플러그인 코드베이스로 옮기기 위한 아키텍처 청사진이다. 코드는 작성하지 않지만, 패키지·클래스·인터페이스·메서드 시그니처 수준까지 명시하여 어떤 개발자가 이 문서만 보고도 스켈레톤 코드를 곧바로 만들 수 있도록 하는 것을 목표로 한다.

0.2 핵심 설계 원칙과 적용 방식

원칙이 프로젝트에서의 구체적 적용SOLID모든 "직업", "총기", "적", "포탑"은 인터페이스(계약)로 추상화하고, 구체 구현은 별도 클래스+데이터 정의
│   │       │   │   ├── classes.yml
│   │       │   │   └── specializations.yml
│   │       │   ├── npc/(Config/Registry)로 분리한다. 새 총기 하나를 추가할 때 기존 코드를 수정하지 않고 새 클래스+등록 한 줄만 추가되도록 한다 (OCP).이벤트 기반 구조Bukkit/Paper의 Event/Listener 체계를 게임 자체 로직에도 그대로 확장한다. 코어 피격, NPC 사망, 웨이브 종료, 광물 채굴 등 모든 상태 변화는 커스텀 이벤트를 발행(fire)하고, 각 시스템은 그 이벤트를 구독(subscribe)하는 방식으로만 상호작용한다. 시스템 간 직접 참조(강결합)를 최소화한다.데이터/로직 분리총기 스탯, 몬스터 스탯, 웨이브 구성, 직업 트리 수치 등은 전부 YAML Config 또는 JSON 데이터 파일로 외부화하고, 로직 클래스는 그 데이터를 "해석"만 한다. 밸런스 수정 시 재컴파일이 필요 없도록 한다.Registry 패턴총기, 직업, 전문화, 포탑, NPC 종류, 웨이브 등 "종류가 계속 늘어나는" 모든 요소는 중앙 Registry에 등록하고 ID로 조회한다.Factory 패턴몬스터, 총알(Projectile), NPC, 포탑 등 반복 생성되는 객체는 Factory를 통해 생성하여 생성 로직을 한 곳에 모은다.Strategy 패턴총기 발사 방식(단발/연발/저격), 힐 방식(지속/범위/집중), AI 행동(공격/도주/채굴) 등 "같은 부모 아래 동작 방식이 갈리는" 요소에 적용한다.State 패턴웨이브 상태(대기/진행/보상/휴식), 코어 상태(정상/위험/파괴), NPC 상태(대기/작업/전투/사망) 등 명확한 상태 전이가 있는 도메인에 적용한다.확장 전제 설계모든 Enum 대신 가능하면 문자열 ID + Registry 조회 방식을 사용하여, 서버 재시작 없이 데이터팩/애드온 형태로 콘텐츠를 추가할 수 있는 여지를 남긴다.

0.3 기술 스택 확정


Java 21 (LTS, Record/Sealed Class/Pattern Matching 적극 활용)
Paper API 1.21.1 (NMS 접근 최소화, 가능한 한 공식 API로 구현)
Gradle (Shadow 플러그인으로 의존성 셰이딩)
영속성: 1차는 YAML/JSON 기반 파일 저장, 2차 확장으로 SQLite→MySQL/MariaDB (JDBC 추상화 계층을 처음부터 둠)
비동기 처리: Paper의 BukkitScheduler/Folia 호환 스레드 정책 고려 (리전 스레딩 대비)
커맨드/GUI: Paper Adventure API 기반 텍스트, Inventory GUI 프레임워크 자체 제작 (경량 커스텀 GUI 매니저)



1. 게임 전체 콘셉트

1.1 한 줄 콘셉트

"내 코어를 지켜라" — 플레이어(들)는 사방에서 몰려오는 몬스터 웨이브로부터 **코어(Core)**를 방어하며, 광산 클리커로 자원을 캐고, NPC를 육성해 병력을 늘리고, 장벽과 포탑으로 기지를 확장하고, 9개 직업 27개 전문화 중 하나로 성장하는 FPS 로그라이크 협동 타워디펜스.

1.2 게임 루프의 3층 구조


매크로 루프 (메타 성장, 런 간): 한 판(런)이 끝나면 점수 기반 재화를 얻어 영구 업그레이드(스킬포인트, 시작 장비, 해금 콘텐츠)에 투자. 다음 런은 더 유리하게 시작.
미들 루프 (한 판 내, 웨이브 단위): 웨이브 진행 → 웨이브 종료 → 보상/모집/건설 페이즈 → 다음 웨이브. 코어 레벨업으로 새 시스템(광산, 스킬트리, NPC 슬롯 등)이 순차 해금.
마이크로 루프 (실시간 전투): FPS 슈팅, 조준/재장전/스킬 사용, 실시간 NPC 지휘, 포탑 배치·업그레이드.


1.3 왜 이 구조가 좋은가 (설계 근거)


로그라이크 특유의 "한 판은 짧고 굵게, 실패해도 다음 판에 도움이 된다"는 동기부여 구조를 코어 레벨 시스템(런 내 성장)과 영구 성장(런 간 성장)으로 이중화하여 확보.
FPS 전투 + 클리커(광산) + 육성(NPC)이라는 이질적 장르를 "코어 에너지"라는 단일 자원 허브로 연결해 시스템 간 결합을 데이터 레벨(자원)로만 유지하고 로직 레벨에서는 분리.
협동 플레이 시 역할 분업(누구는 전투, 누구는 채광, 누구는 건설)이 자연스럽게 생기도록 직업 3병과 구조를 설계.


1.4 확장 방향


시즌제 콘텐츠(계절별 몬스터/보스/스킨) 추가가 쉬운 구조 (웨이브 데이터 및 몬스터 Registry가 외부화되어 있으므로).
코어 테마 변형(용암 코어, 얼음 코어 등 별도 맵 프리셋)으로 재플레이성 확장.
PvE뿐 아니라 후속 PvP 모드(코어 vs 코어) 확장을 염두에 두고 팀 개념을 처음부터 GameTeam 단위로 추상화.



2. 핵심 플레이 루프 (상세)

2.1 런 시작


플레이어(파티)가 맵 로드 → GameSession 생성 → CoreEntity 스폰 (레벨 1)
영구 성장 데이터(PlayerProgressionData)를 불러와 시작 스탯/장비/해금 여부 적용
초기 시스템: 총기 전투, 코어 체력만 노출. 광산/스킬트리/NPC 모집 등은 잠김 상태


2.2 웨이브 루프 (State 패턴 기반 WaveState)

WAITING(대기) → SPAWNING(적 생성) → IN_PROGRESS(전투 진행)
    → CLEARED(웨이브 클리어) → REWARD(보상/모집/건설 페이즈) → WAITING(다음 웨이브)


WAITING: 플레이어가 건설/배치/모집을 하는 준비 시간 (제한시간 있음, 스킵 가능)
SPAWNING: WaveDefinition에 정의된 몬스터들이 스폰 포인트에서 생성, WaveSpawnEvent 발행
IN_PROGRESS: 코어 방어 실시간 전투. 코어 HP, NPC 생사, 포탑 가동이 전부 이 구간에서 발생
CLEARED: 모든 적 처치 또는 생존 조건 달성 시 WaveClearedEvent 발행 → 보상 계산
REWARD: 코어 경험치/레벨업 판정, NPC 모집소 갱신, 스킬포인트 지급


2.3 코어 레벨업에 따른 시스템 순차 해금 (회의 내용 반영)

코어 레벨해금 시스템1기본 전투(총기), 장벽 1종2광산(클리커) 시스템3포탑 1종, NPC 모집소4스킬트리(직업 선택) 개방5전문화 트리 선택6+강화 모듈, 상위 포탑/장벽 재질, 오버클럭 등 순차 해금

이 표는 CoreUnlockConfig(YAML)로 관리되어 기획자가 코드를 건드리지 않고 레벨-해금 매핑을 조정 가능.

2.4 런 종료 및 메타 성장 반영


코어 파괴(패배) 또는 목표 웨이브 달성(승리) 시 GameSession 종료
최종 점수 계산 (ScoreCalculator): 생존 웨이브 수, 처치 수, 코어 레벨, 남은 NPC 수 등 가중합
점수를 영구 재화(MetaCurrency)로 환산하여 PlayerProgressionData에 저장 → 영구 성장 트리에 투자 가능



3. 전체 시스템 구조 (아키텍처 다이어그램 설명)

3.1 레이어 구조

┌─────────────────────────────────────────────────────────┐
│  Paper API Layer (Bukkit Event, Entity, World, Scheduler) │
└───────────────────────┬─────────────────────────────────┘
                         │ (Adapter / Listener)
┌───────────────────────▼─────────────────────────────────┐
│  Core Engine Layer (자체 이벤트 버스, GameSession, Config) │
├───────────────────────────────────────────────────────────┤
│  Domain Systems Layer                                      │
│  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌───────┐│
│  │ Combat   ││ Core     ││ Wave     ││ NPC      ││ Mining ││
│  │ (총기)   ││ (코어)   ││ (웨이브) ││ (NPC)    ││ (광산) ││
│  └──────────┘└──────────┘└──────────┘└──────────┘└───────┘│
│  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐         │
│  │ Structure││ Class    ││ Progres- ││ Persis-  │         │
│  │ (장벽/포탑)│(직업)   ││ sion(성장)││ tence(저장)│        │
│  └──────────┘└──────────┘└──────────┘└──────────┘         │
├───────────────────────────────────────────────────────────┤
│  Data/Config Layer (YAML/JSON, Registry, Repository)        │
└───────────────────────┬─────────────────────────────────┘
                         │
┌───────────────────────▼─────────────────────────────────┐
│  Storage Layer (Flat-file → SQLite/MySQL, 추상화된 Repo)  │
└─────────────────────────────────────────────────────────┘

3.2 시스템 간 통신 원칙


직접 호출 금지 원칙: Domain Systems Layer의 각 시스템은 서로를 직접 import하여 메서드를 호출하지 않는다. 대신 자체 이벤트 버스(GameEventBus)를 통해서만 통신한다.

예: 광산 시스템이 "광물 채굴 완료"를 알리면(OreMinedEvent), 코어 시스템이 이를 구독해 코어 에너지를 증가시킨다. 광산 시스템은 코어 시스템의 존재 자체를 몰라도 된다.



예외: 순수 조회(read-only) 성격의 공용 서비스(예: PlayerProgressionService, ConfigService)는 인터페이스를 통해 직접 주입받아 호출 가능. 단 상태 변경(write)은 반드시 이벤트를 통해야 한다.
이 원칙 덕분에 시스템 하나를 통째로 교체(예: 광산 시스템을 다른 미니게임으로 교체)해도 다른 시스템은 이벤트 스펙만 유지하면 영향받지 않는다.


3.3 GameEventBus 설계


Bukkit의 PluginManager#callEvent를 그대로 활용하되, 우리 도메인 이벤트는 전부 AbstractGameEvent를 상속한 커스텀 이벤트로 정의하여 Paper의 이벤트 시스템에 자연스럽게 편입시킨다 (별도 이벤트 버스를 새로 구현하지 않아 유지보수 부담을 줄임).
AbstractGameEvent는 GameSession 참조, 발생 시각, 취소 가능 여부(Cancellable)를 공통으로 가진다.
모든 도메인 리스너는 GameListener 마커 인터페이스를 구현하고, 플러그인 부트스트랩 시 ListenerRegistrar가 리플렉션 없이 명시적 리스트로 등록한다 (스타트업 시간 예측 가능성 확보, 리플렉션 스캔은 지양).



4. 프로젝트 디렉터리 구조 (Gradle 프로젝트 루트 기준)

core-defense-plugin/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── gradle/wrapper/
├── README.md
├── docs/
│   └── design/                     ← 본 설계 문서 및 하위 상세 문서
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/yourstudio/coredefense/   (5장 패키지 구조 참고)
│   │   └── resources/
│   │       ├── plugin.yml
│   │       ├── config/
│   │       │   ├── core.yml
│   │       │   ├── waves/
│   │       │   │   ├── wave_definitions.yml
│   │       │   │   └── boss_waves.yml
│   │       │   ├── weapons/
│   │       │   │   ├── guns.yml
│   │       │   │   └── melee.yml
│   │       │   ├── classes/
│   │       │   │   ├── npc_traits.yml
│   │       │   │   └── npc_recruit_pool.yml
│   │       │   ├── mining/
│   │       │   │   └── ores.yml
│   │       │   ├── structures/
│   │       │   │   ├── walls.yml
│   │       │   │   └── turrets.yml
│   │       │   └── progression/
│   │       │       └── meta_upgrades.yml
│   │       ├── lang/
│   │       │   ├── en_US.yml
│   │       │   └── ko_KR.yml
│   │       └── schematics/           ← 코어/포탑/장벽 구조물 스키매틱(WorldEdit .schem 등)
│   └── test/
│       └── java/                     ← 단위 테스트 (JUnit5 + MockBukkit)
└── libs/                             ← 외부 비공개 의존성(있을 경우)

4.1 설계 근거


resources/config 하위를 도메인별 폴더로 나누어, 밸런스 담당자가 코드 지식 없이도 YAML만 수정할 수 있게 한다.
docs/design에 본 문서와 이후 파생 문서(예: weapon-balance.md, wave-table.md)를 함께 버전관리하여 기획-개발 싱크를 유지한다.
schematics 폴더를 별도로 두어, 코어/포탑/장벽의 월드 구조물을 코드가 아닌 데이터(스키매틱 파일)로 배치할 수 있게 한다 → 레벨 디자이너가 코드 재컴파일 없이 구조물 모양을 수정 가능.
test에 MockBukkit 기반 유닛 테스트를 처음부터 편성하여, 총기 데미지 계산·웨이브 스폰 로직·코어 레벨업 계산 등 순수 로직을 서버 구동 없이 검증 가능하게 한다.



5. Java 패키지 구조

루트 패키지: com.yourstudio.coredefense

com.yourstudio.coredefense
├── CoreDefensePlugin.java          (JavaPlugin 진입점, 부트스트랩만 담당)
├── bootstrap/
│   ├── ModuleInitializer.java      (각 도메인 모듈 초기화 순서 관리)
│   ├── ListenerRegistrar.java
│   └── CommandRegistrar.java
├── api/                            (다른 플러그인/애드온이 참조할 공개 API, 향후 확장 대비)
│   ├── event/                      (외부 공개용 이벤트 인터페이스)
│   └── service/                    (외부 공개용 서비스 인터페이스)
├── common/
│   ├── event/
│   │   ├── AbstractGameEvent.java
│   │   └── GameListener.java
│   ├── registry/
│   │   ├── Registry.java                  (제네릭 Registry<K,V> 인터페이스)
│   │   ├── AbstractRegistry.java
│   │   └── RegistryKey.java
│   ├── config/
│   │   ├── ConfigService.java
│   │   ├── ConfigLoader.java
│   │   └── ReloadableConfig.java
│   ├── util/
│   │   ├── MathUtils.java
│   │   ├── ParticleUtils.java
│   │   └── CooldownTracker.java
│   └── result/
│       └── ActionResult.java              (성공/실패/사유를 담는 공용 결과 타입)
│
├── session/
│   ├── GameSession.java
│   ├── GameSessionManager.java
│   ├── GameTeam.java
│   └── SessionState.java                  (State 패턴: LOBBY/RUNNING/ENDED)
│
├── core/                                   (코어 시스템)
│   ├── CoreEntity.java
│   ├── CoreLevel.java
│   ├── CoreEnergyManager.java
│   ├── CoreUnlockManager.java
│   ├── CoreState.java                      (NORMAL/DAMAGED/CRITICAL/DESTROYED)
│   └── event/
│       ├── CoreDamagedEvent.java
│       ├── CoreLeveledUpEvent.java
│       ├── CoreDestroyedEvent.java
│       └── CoreSystemUnlockedEvent.java
│
├── wave/                                   (웨이브 시스템)
│   ├── WaveManager.java
│   ├── WaveState.java
│   ├── WaveDefinition.java
│   ├── WaveSpawnScheduler.java
│   ├── boss/
│   │   └── BossWaveHandler.java
│   └── event/
│       ├── WaveStartedEvent.java
│       ├── WaveSpawnEvent.java
│       └── WaveClearedEvent.java
│
├── combat/                                  (FPS 전투 / 총기 시스템)
│   ├── weapon/
│   │   ├── Weapon.java                     (인터페이스)
│   │   ├── AbstractFirearm.java
│   │   ├── FireMode.java                   (SINGLE/BURST/AUTO/CHARGE 등 Strategy)
│   │   ├── strategy/
│   │   │   ├── FireModeStrategy.java
│   │   │   ├── SingleShotStrategy.java
│   │   │   ├── BurstFireStrategy.java
│   │   │   └── SniperShotStrategy.java
│   │   ├── projectile/
│   │   │   ├── ProjectileType.java
│   │   │   ├── BulletProjectile.java
│   │   │   └── ProjectileFactory.java
│   │   ├── ammo/
│   │   │   ├── AmmoType.java
│   │   │   └── AmmoInventory.java
│   │   ├── WeaponRegistry.java
│   │   └── WeaponFactory.java
│   ├── melee/
│   │   ├── MeleeWeapon.java
│   │   └── MeleeAttackHandler.java
│   ├── damage/
│   │   ├── DamageCalculator.java
│   │   ├── DamageSource.java
│   │   └── DamageModifier.java
│   └── event/
│       ├── WeaponFiredEvent.java
│       └── EntityDamagedByGameEvent.java
│
├── mob/                                     (적 몬스터)
│   ├── MonsterDefinition.java
│   ├── MonsterFactory.java
│   ├── MonsterAI.java                       (Strategy: 목표 지정/이동/공격 패턴)
│   ├── ai/
│   │   ├── TargetSelector.java
│   │   └── PathingStrategy.java
│   ├── MonsterRegistry.java
│   └── event/
│       └── MonsterKilledEvent.java
│
├── npc/                                     (NPC 시스템)
│   ├── GameNpc.java
│   ├── NpcRole.java                         (PRODUCTION/COMBAT)
│   ├── NpcState.java                        (IDLE/WORKING/FIGHTING/DEAD)
│   ├── NpcStatSheet.java
│   ├── trait/
│   │   ├── NpcTrait.java
│   │   ├── TraitRegistry.java
│   │   └── ResonanceCalculator.java         (특성 공명 계산)
│   ├── job/
│   │   ├── NpcJob.java                      (Miner/Medic/Researcher 등과 매핑)
│   │   └── JobSkillTree.java
│   ├── recruit/
│   │   ├── RecruitPool.java
│   │   ├── RecruitOffer.java
│   │   └── RecruitmentService.java
│   ├── death/
│   │   ├── NpcDeathHandler.java
│   │   ├── ReviveService.java               (빈사 구조)
│   │   └── LegacyTransferService.java       (묘지/유산 이전)
│   └── event/
│       ├── NpcRecruitedEvent.java
│       ├── NpcLeveledUpEvent.java
│       └── NpcDiedEvent.java
│
├── mining/                                  (광산 클리커 시스템)
│   ├── MiningSession.java
│   ├── OreType.java
│   ├── OreRegistry.java
│   ├── ClickMiningHandler.java
│   ├── AutoMiningTicker.java                (NPC 자동 채굴 틱 처리)
│   └── event/
│       └── OreMinedEvent.java
│
├── structure/                               (장벽/포탑)
│   ├── wall/
│   │   ├── WallDefinition.java
│   │   ├── WallMaterialTier.java
│   │   ├── WallInstance.java
│   │   └── WallModule.java                  (가시/전기/폭발 강화 모듈)
│   ├── turret/
│   │   ├── Turret.java
│   │   ├── TurretDefinition.java
│   │   ├── TurretFactory.java
│   │   ├── TurretTargeting.java
│   │   └── TurretAmmoSupply.java
│   ├── StructureRegistry.java
│   ├── StructurePlacementService.java
│   └── event/
│       ├── StructurePlacedEvent.java
│       └── StructureDestroyedEvent.java
│
├── job/                                     (플레이어 직업/전문화 — NPC job과는 별개 네임스페이스)
│   ├── PlayerClass.java                     (Gunner/Swordsman/Archer/Miner/Medic/Researcher/Mechanic/Builder/Fighter)
│   ├── ClassDefinition.java
│   ├── Specialization.java                  (27개 전문화)
│   ├── SkillTree.java
│   ├── skill/
│   │   ├── Skill.java
│   │   ├── ActiveSkill.java
│   │   ├── PassiveSkill.java
│   │   └── UltimateSkill.java
│   ├── ClassRegistry.java
│   └── event/
│       ├── ClassSelectedEvent.java
│       └── SkillUsedEvent.java
│
├── progression/                              (영구 성장 / 메타 성장)
│   ├── MetaCurrency.java
│   ├── PlayerProgressionData.java
│   ├── MetaUpgrade.java
│   ├── MetaUpgradeTree.java
│   ├── ScoreCalculator.java
│   └── ProgressionService.java
│
├── persistence/                              (저장 시스템)
│   ├── Repository.java                       (제네릭 인터페이스)
│   ├── file/
│   │   ├── YamlPlayerRepository.java
│   │   └── JsonSessionSnapshotRepository.java
│   ├── sql/
│   │   ├── SqlPlayerRepository.java          (SQLite/MySQL 공용, JDBC 기반)
│   │   └── SqlSchemaMigrator.java
│   ├── DataStoreType.java                    (FLAT_FILE/SQLITE/MYSQL)
│   └── PersistenceService.java
│
├── gui/                                       (인벤토리 기반 UI)
│   ├── GameMenu.java
│   ├── MenuFactory.java
│   └── menus/
│       ├── RecruitMenu.java
│       ├── SkillTreeMenu.java
│       └── MetaUpgradeMenu.java
│
└── command/
    ├── CoreDefenseCommand.java
    └── sub/
        ├── StartGameSubcommand.java
        └── AdminReloadSubcommand.java

5.1 패키지 설계 근거


도메인별 패키지 분리(core/wave/combat/mob/npc/mining/structure/job/progression/persistence): 하나의 도메인 변경이 다른 도메인의 컴파일에 영향을 주지 않도록 패키지 경계를 곧 모듈 경계로 취급한다. 추후 Gradle 멀티모듈로 쪼개기도 쉬움.
event 하위 패키지를 각 도메인 안에 둠: 이벤트가 해당 도메인의 "공개 계약(public contract)"이라는 것을 명확히 하기 위함. 다른 도메인은 이 이벤트 클래스만 알면 되고 내부 구현 클래스는 몰라도 됨(캡슐화).
api 패키지 별도 분리: 추후 다른 플러그인이나 애드온이 이 플러그인을 확장할 수 있도록 공개 인터페이스만 노출하는 계층을 처음부터 분리해둠 (하위 호환성 관리 용이).



6. 시스템별 클래스 구조 & 7. 주요 인터페이스/추상 클래스 & 8. 각 클래스의 역할

이 세 항목은 시스템 단위로 함께 서술하는 것이 실제 개발 시 참조하기 쉬우므로 통합하여 시스템별로 기술한다.

6.1 코어(Core) 시스템

핵심 클래스


CoreEntity : 실제 월드에 존재하는 코어 개체(내부적으로 커스텀 엔티티 또는 Armor Stand + 커스텀 홀로그램 조합으로 구현 가능). 체력(HP), 현재 레벨, 현재 경험치를 보유.

주요 메서드: damage(double amount, DamageSource source), heal(double amount), addExperience(int exp), getLevel(), getState()



CoreLevel (Record) : 레벨별 최대 HP, 필요 경험치, 해금 시스템 목록을 담는 불변 데이터 객체. CoreLevelRegistry에서 레벨→데이터 매핑을 관리.
CoreEnergyManager : 코어 에너지(전력) 총량, 소비처(포탑/장벽 모듈/오버클럭)에 대한 할당을 관리. 인터페이스 EnergyConsumer를 구현하는 모든 구조물이 에너지를 요청(requestEnergy(int amount))하면 우선순위 큐 기반으로 분배.
CoreUnlockManager : 코어 레벨업 시 CoreUnlockConfig를 조회하여 어떤 시스템을 활성화할지 판단하고 CoreSystemUnlockedEvent를 발행.
CoreState (Enum + State 패턴의 상태 마커) : NORMAL / DAMAGED / CRITICAL / DESTROYED. 상태 전이 로직은 CoreStateMachine이 전담(체력 임계값 도달 시 전이, 전이 시 파티클/사운드 연출 트리거).


핵심 인터페이스


EnergyConsumer : int getEnergyDemand(); void onEnergyAllocated(int amount); — 포탑, 강화 모듈, 오버클럭 빌더 스킬 등이 구현.
CoreLevelListener (마커) : 코어 레벨업에 반응해야 하는 시스템(광산, NPC 슬롯, 스킬트리 등)이 구현하여 ListenerRegistrar에 등록.


역할 요약: 코어 시스템은 "게임 전체의 심장이자 자원 허브"로서, 직접 로직을 수행하기보다 이벤트를 발행하여 다른 시스템의 트리거 역할을 하는 데 집중한다. 이렇게 설계하면 코어 자체 로직은 매우 단순하게 유지되고, 실제 복잡도는 각 도메인(광산, NPC, 구조물)에 위임된다.

6.2 웨이브(Wave) 시스템

핵심 클래스


WaveManager : GameSession당 하나. 현재 웨이브 번호, WaveState, 타이머를 보유. tick()이 매 서버 틱 또는 1초 간격으로 호출되어 상태 전이를 판단.
WaveDefinition (Record, YAML 역직렬화 대상) : 웨이브 번호, 스폰될 몬스터 목록(List<MonsterSpawnEntry>), 스폰 간격, 보상 테이블 참조 ID.
WaveSpawnScheduler : WaveDefinition을 읽어 실제 스폰 타이밍을 계산하고 MonsterFactory에 생성을 위임.
BossWaveHandler : 일정 웨이브(예: 5,10,15...)마다 별도의 보스 스폰 로직과 특수 승리조건을 처리 (일반 WaveDefinition과 다른 서브클래스 BossWaveDefinition 사용).


핵심 인터페이스


WaveClearCondition : boolean isCleared(GameSession session); — 기본은 "모든 몬스터 사망"이지만, 보스전은 "보스 HP 0" 등으로 다르게 구현 가능(Strategy).


역할 요약: 웨이브 시스템은 State 패턴의 대표 사례로, WaveState enum과 각 상태의 진입/퇴장 처리를 WaveManager 내부에서 switch-case가 아닌 WaveStateHandler 인터페이스 구현체(WaitingStateHandler, SpawningStateHandler, ...) 리스트로 관리하여, 새로운 상태(예: INTERMISSION_EVENT)를 추가할 때 기존 상태 처리 코드를 건드리지 않도록 한다(OCP).

6.3 전투(Combat) — FPS 총기 시스템 (회의 외 추가 요구사항 반영)

핵심 인터페이스/추상클래스


Weapon (인터페이스) : void use(Player player); ItemStack toItemStack(); WeaponDefinition getDefinition();
AbstractFirearm implements Weapon : 총기 공통 로직(탄창, 재장전, 반동, 조준선) 구현. 하위 클래스는 총사 전문화별로 분화.

SingleShotFirearm, BurstFireFirearm, SniperRifle 이 AbstractFirearm을 상속하며, 발사 방식은 내부적으로 FireModeStrategy에 위임(상속+전략 혼합 — 총기 "종류"는 상속, 발사 "패턴"은 전략으로 분리하여 총사 전문화(단발/연발/저격)와 실제 무기 아이템(권총/돌격소총/저격총 등 세부 아이템)을 독립적으로 조합 가능하게 함).



FireModeStrategy (인터페이스) : void fire(Player shooter, Weapon weapon);

SingleShotStrategy, BurstFireStrategy, SniperShotStrategy 구현체.



ProjectileFactory : 총알 종류(일반탄/관통탄/폭발탄 등, 검사/궁사 무기의 투사체 포함)를 생성. MonsterAI나 TurretTargeting과도 공유되는 공용 컴포넌트.
DamageCalculator : 무기 기본 데미지 × 거리 감쇠 × 전문화 보너스 × 특성/공명 보너스 × 대상 방어력을 계산하는 순수 함수형 클래스(부작용 없음, 단위테스트 용이).


FPS 특유 고려사항


조준(에이밍) 시 Player의 시야 벡터(getLocation().getDirection())를 기반으로 레이캐스트(RayTraceResult)를 수행하여 히트 판정. Paper의 World#rayTraceEntities를 활용.
반동/탄퍼짐은 클라이언트 시야에 실제로 영향을 주기 어려우므로(서버 사이드 한계), 탄착점에 랜덤 오프셋을 부여하는 방식으로 시뮬레이션.
재장전 딜레이, 연사 속도는 CooldownTracker(공용 유틸)로 통일 관리하여 모든 무기/스킬의 쿨다운을 동일한 방식으로 다룸.


역할 요약: 총기 시스템은 "아이템(외형/장착) — 발사방식(전략) — 투사체(공용 팩토리) — 데미지 계산(공용 순수함수)"의 4계층으로 분리되어 있어, 새 총기 하나 추가 시 WeaponDefinition YAML 항목 하나와 필요시 신규 FireModeStrategy 하나만 추가하면 되고, 기존 코드는 전혀 수정하지 않는다.

6.4 몬스터(Mob) 시스템


MonsterDefinition (Record) : 종족, 기본 스탯, AI 프로필 ID, 드랍 테이블 ID.
MonsterFactory : Location과 MonsterDefinition을 받아 실제 Bukkit 엔티티(Vanilla 몹 베이스 + NBT 태깅 또는 커스텀 엔티티)를 생성하고 MonsterAI를 부착.
MonsterAI (인터페이스) : void tick(Mob entity); — TargetSelector(공격 대상 우선순위: 코어 vs NPC vs 플레이어)와 PathingStrategy(직진/우회/공성)를 조합.
MonsterRegistry : ID → MonsterDefinition 조회.


6.5 NPC 시스템


GameNpc : 공통 상위 클래스. NpcRole(PRODUCTION/COMBAT), NpcState(IDLE/WORKING/FIGHTING/DEAD), NpcStatSheet(공격/체력/속도), 부여된 NpcTrait 1개, NpcJob(직업/전직 정보), JobSkillTree 진행도를 보유.
NpcStatSheet : 기본 스탯 + 트레이트 보너스 + 공명 보너스를 합산한 최종 스탯을 계산하는 책임(ResonanceCalculator와 협업).
NpcTrait (인터페이스) + TraitRegistry : "광부의 재능", "전투 본능", "강인함" 등 특성을 데이터 기반으로 정의. 특성은 스탯 보정치와 소속 직업 친화도(공명 계산용 태그)를 가짐.
ResonanceCalculator : 동일 특성을 보유한 NPC 수를 세어 공명 보너스(예: 겹칠 때마다 7% 상승, 상한 캡 적용, 특성-직업 일치 시 100% 발휘)를 계산하는 순수 함수 클래스.
RecruitPool / RecruitOffer / RecruitmentService : 웨이브 종료 후 후보 3명을 생성(랜덤 특성 + 랜덤 잠재 직업 성향), 리롤(자원 소모), 선택/방출 처리.
NpcDeathHandler : NPC 사망 시 ReviveService(빈사 상태 시 구조 가능 여부 판정) → 실패 시 LegacyTransferService(경험치 일부를 코어 또는 동료에게 이전, "묘지" 개념) 순서로 처리.
JobSkillTree : NPC 직업(광부/전투 등)별 성장 트리. 플레이어 직업 트리(job 패키지)와 구조는 유사하지만 완전히 별도 데이터셋으로 관리(혼동 방지를 위해 패키지도 분리됨: npc.job vs job).


6.6 광산(Mining) 시스템


MiningSession : 플레이어별 또는 파티 공용 채광 상태(누적 채광 포인트, 현재 해금된 OreType 티어).
ClickMiningHandler : 우클릭/좌클릭 이벤트를 구독하여 MiningSession에 포인트를 누적하고, 확률 테이블(OreType별 드랍률)에 따라 광물 지급.
AutoMiningTicker : NPC 중 NpcRole.PRODUCTION && NpcJob == MINER인 개체를 주기적으로 순회하며 자동 채광 포인트를 누적. 광부 스탯이 임계치를 넘으면 사람 클릭보다 효율이 높아지는 규칙을 MiningEfficiencyPolicy로 캡슐화.
OreType (Record) + OreRegistry : 광물 등급, 해금 조건(누적 포인트), 코어 에너지 환산 비율.


6.7 구조물(Structure) — 장벽/포탑 시스템


WallDefinition / WallMaterialTier : 참나무→가문비→돌담→철격자→강화방벽의 티어별 체력/방어 데이터.
WallInstance : 실제 배치된 장벽 개체(위치, 현재 체력, 장착된 WallModule 목록).
WallModule (인터페이스) : 가시(반사 데미지), 전기(기절), 폭발(광역 피해) 등 슬롯형 강화 모듈. EnergyConsumer 인터페이스도 함께 구현하여 코어 에너지를 소비.
Turret (추상 클래스) : 사거리, 공격속도, 탄약 소모량 등 공통 필드. TurretTargeting(전략: 최근접/최고체력/최다피해 등 타겟 우선순위)을 조합.

하위 구현: ArrowSentryTurret, SlingshotTurret, FlamethrowerTurret, MinigunTurret, BuffTowerTurret, LightGunTurret, AutoCannonTurret, MissileTurret, NukeMissileTurret (회의에서 정의된 나무~네더의 별 티어 매핑).



TurretAmmoSupply : 포탑별 전용 탄약 재고 관리, NPC(메카닉/빌더) 보급 연계 지점 제공.
TurretFactory / StructureRegistry : 신규 포탑/장벽 추가 시 정의 등록 지점.


6.8 직업(Job/Class) 시스템 — 9직업 27전문화


PlayerClass (Enum 또는 Registry 기반 값 객체) : 돌격군(총사/검사/궁사), 지원군(광부/메딕/연구원), 방어군(메카닉/빌더/파이터).
ClassDefinition : 직업별 기본 스탯 보정, 사용 가능 무기군, 전문화 3종 참조.
Specialization : 27개 전문화 각각의 고유 패시브 + 액티브 스킬 + 궁극기 슬롯 정의.
SkillTree : 전문화 선택 이후 세부 스킬 포인트 분배 트리. SkillNode(선행 조건, 포인트 비용, 효과)를 그래프 구조로 표현.
Skill (추상) → ActiveSkill / PassiveSkill / UltimateSkill : 궁극기는 별도 쿨다운 풀과 UI 슬롯을 가짐.
ClassRegistry : 직업/전문화 ID 조회, 신규 직업 확장 지점.


직업별 설계 메모(회의 반영)


파이터: 극딜/CC/방어 3분화. UltimateSkill 예: 극딜(순간 광역 폭딜), CC(도발+기절), 방어(무적 강化).
메카닉: 자폭봇/견제봇/지원봇. 로봇은 GameNpc와 별개의 CombatDrone 엔티티로 구현하되 EnergyConsumer를 구현하여 코어 에너지 소모. 최대 운용 수는 DroneCapacityPolicy로 제한.
빌더: 유지보수/강화/오버클럭. 오버클럭은 EnergyConsumer 초과 요청 + 과열 패널티(OverclockPenaltyHandler)로 구현, 코어 에너지 시스템과 강하게 연동.
메딕: 지속/범위/집중 힐. HealStrategy 인터페이스로 힐 방식 분리, NPC/코어 시설도 회복 대상이 될 수 있도록 Healable 인터페이스를 코어/NPC/구조물이 공통 구현.


6.9 영구 성장(Progression) 시스템


PlayerProgressionData : 플레이어별 영구 저장 데이터(메타 재화, 해금 콘텐츠, 영구 업그레이드 레벨).
MetaUpgrade / MetaUpgradeTree : 시작 스탯, 시작 장비, 해금형 콘텐츠(신규 직업/포탑/광물 등) 트리.
ScoreCalculator : 런 종료 시 점수를 계산하는 순수 함수 클래스(입력: 세션 통계 → 출력: 점수, 단위테스트 용이).
ProgressionService : 점수를 MetaCurrency로 환산하고 PersistenceService를 통해 저장을 위임하는 파사드(Facade) 역할.


6.10 저장(Persistence) 시스템


Repository<ID, T> (제네릭 인터페이스) : T findById(ID id); void save(T entity); void delete(ID id);
YamlPlayerRepository, JsonSessionSnapshotRepository : 1차 구현체(파일 기반).
SqlPlayerRepository : JDBC 기반 2차 구현체. DataStoreType Config 값에 따라 PersistenceService가 어떤 Repository 구현체를 주입할지 결정(Factory + DI 조합).
SqlSchemaMigrator : 버전별 스키마 마이그레이션 스크립트 관리(Flyway 또는 자체 경량 마이그레이터).



9. 주요 메서드와 호출 관계 (대표 시나리오별 시퀀스)

9.1 시나리오: 플레이어가 총을 발사하여 몬스터를 처치

1. PlayerInteractListener.onLeftClick(PlayerInteractEvent e)
     → WeaponInputHandler.handleFire(Player player)
2. WeaponInputHandler.handleFire()
     → AbstractFirearm.use(player)
3. AbstractFirearm.use()
     → CooldownTracker.isReady(player, weaponId) 확인
     → FireModeStrategy.fire(player, weapon) 위임 (예: SingleShotStrategy)
4. SingleShotStrategy.fire()
     → RayTraceUtil.traceEntity(player) 로 히트 대상 산출
     → ProjectileFactory.spawnTracer(...)  (시각 이펙트용, 판정은 즉시)
     → DamageCalculator.calculate(weapon, distance, shooterBonuses, target)
5. DamageCalculator.calculate() 결과값 반환
     → CombatDamageService.applyDamage(target, amount, DamageSource.WEAPON)
6. CombatDamageService.applyDamage()
     → target이 Monster인 경우: Mob 엔티티 HP 감소 → HP<=0 이면
         MonsterKilledEvent 발행 (몬스터, 처치자, 사용 무기 포함)
7. (구독자) WaveManager.onMonsterKilled(MonsterKilledEvent)
     → 남은 몬스터 수 갱신 → 0이면 WaveClearedEvent 발행
8. (구독자) ProgressionStatsCollector.onMonsterKilled(...)
     → 세션 통계(처치 수) 누적 (추후 ScoreCalculator 입력으로 사용)
9. (구독자) SkillTree.onMonsterKilled(...)  (필요 시 스킬 포인트/경험치 지급)

설계 포인트: 5~9 사이는 전부 이벤트 구독으로 이어지며, CombatDamageService는 WaveManager나 ProgressionStatsCollector의 존재를 전혀 모른다. 새로운 시스템(예: "몬스터 처치 시 도감 등록")을 추가해도 MonsterKilledEvent에 리스너 하나만 추가하면 된다.

9.2 시나리오: 코어가 레벨업하여 광산 시스템이 해금됨

1. CoreEntity.addExperience(int exp)
     → 누적 경험치가 다음 레벨 임계치 도달 확인
     → CoreLevelUpService.tryLevelUp(coreEntity)
2. CoreLevelUpService.tryLevelUp()
     → CoreEntity.setLevel(newLevel)
     → CoreLeveledUpEvent(session, oldLevel, newLevel) 발행
3. (구독자) CoreUnlockManager.onCoreLeveledUp(event)
     → CoreUnlockConfig.getUnlocksForLevel(newLevel) 조회
     → 해금 대상 시스템 각각에 대해 CoreSystemUnlockedEvent(systemId) 발행
4. (구독자) MiningSessionManager.onSystemUnlocked(event)
     → event.systemId() == "MINING" 이면 해당 세션의 MiningSession 활성화 플래그 on
     → GUI 알림(BossBar/ActionBar)으로 플레이어에게 안내
5. (구독자) NpcRecruitmentService.onSystemUnlocked(event)
     → event.systemId() == "NPC_RECRUIT" 이면 모집소 GUI 접근 가능 처리

설계 포인트: CoreUnlockManager는 "무엇이 해금되는지"만 알고 "해금되면 각 시스템이 구체적으로 뭘 하는지"는 전혀 모른다. 이는 OCP의 핵심 사례로, 향후 레벨 6 이후 새로운 해금 콘텐츠(예: "특수 상점")를 추가해도 CoreUnlockManager는 수정할 필요가 없다(Config 데이터만 추가하고, 새 시스템이 CoreSystemUnlockedEvent를 구독하기만 하면 됨).

9.3 시나리오: NPC 모집 및 배치

1. GameMenu(RecruitMenu).open(player)
     → RecruitmentService.getCurrentOffers(session) 로 후보 3명 조회/생성
2. player가 후보 선택 클릭
     → RecruitMenu.onOfferSelected(offer)
     → RecruitmentService.recruit(session, offer)
3. RecruitmentService.recruit()
     → NpcCapacityPolicy.canAdd(session) 확인 (코어 레벨별 최대치)
     → GameNpcFactory.create(offer.trait(), offer.jobHint())
     → NpcRecruitedEvent 발행
4. (구독자) ResonanceCalculator.recalculate(session)
     → 신규 NPC의 트레이트를 포함하여 전체 공명 보너스 재계산
     → 각 NpcStatSheet에 보너스 반영

9.4 시나리오: 오버클럭 스킬 사용 (빌더 전문화, 코어 에너지 연동)

1. SkillInputHandler.onSkillKey(player, skillSlot)
     → ActiveSkill(OverclockSkill).activate(player)
2. OverclockSkill.activate()
     → CoreEnergyManager.requestBurstEnergy(amount) 호출 (EnergyConsumer 구현)
3. CoreEnergyManager.requestBurstEnergy()
     → 가용 에너지 확인 → 부족 시 ActionResult.failure("에너지 부족")
     → 충분 시 에너지 차감 + OverclockActivatedEvent 발행
4. (구독자) OverclockPenaltyHandler.onActivated(event)
     → 일정 시간 후 과열 패널티 스케줄링 (BukkitScheduler.runTaskLater)
5. 시간 경과 후 OverheatTriggeredEvent 발행 → 대상 구조물/스킬 일시 비활성화


10. 이벤트 흐름 (전체 이벤트 카탈로그 및 발행-구독 매핑)

10.1 이벤트 명명 규칙


과거형 동사로 명명 (~Event가 발생한 "결과"를 나타냄): MonsterKilledEvent, WaveClearedEvent
취소 가능해야 하는 이벤트(사전 검증 필요)는 Cancellable 구현: 예) NpcRecruitedEvent는 정원 초과 시 사전 단계에서 걸러지지만, CoreDamagedEvent는 무적 판정 등을 위해 Cancellable로 설계.


10.2 이벤트 카탈로그 (발행자 → 주요 구독자)

이벤트발행 시스템주요 구독 시스템WeaponFiredEventCombatProgression(통계), Skill(트리거형 스킬)MonsterKilledEventCombat/MobWave, Progression, NPC(경험치 분배), Job(스킬 트리거)WaveStartedEventWaveStructure(포탑 자동 활성화), NPC(전투 배치 알림)WaveClearedEventWaveCore(경험치 지급), NPC(모집소 갱신), ProgressionCoreDamagedEventCoreUI(BossBar 갱신), Progression(피격 통계)CoreLeveledUpEventCoreCoreUnlockManagerCoreSystemUnlockedEventCoreMining, NPC, Job, StructureCoreDestroyedEventCoreSessionManager(패배 처리), Progression(점수 확정)OreMinedEventMiningCore(에너지 증가), Progression(자원 통계)NpcRecruitedEventNPCJob(스킬트리 배정), UINpcLeveledUpEventNPCTrait/ResonanceNpcDiedEventNPCLegacy(유산 이전), UI(알림), Wave(전투력 재평가)StructurePlacedEventStructureCore(에너지 소비 등록)StructureDestroyedEventStructureWave(방어선 재계산), UISkillUsedEventJobProgression(통계), Core(에너지 연동 스킬의 경우)GameSessionEndedEventSessionProgression(최종 점수/저장), Persistence

10.3 이벤트 흐름 다이어그램 (텍스트 표현)

[Combat] --MonsterKilledEvent--> [Wave] --(0체 시)--> WaveClearedEvent
                                                          │
                        ┌─────────────────────────────────┼───────────────┐
                        ▼                                  ▼               ▼
                   [Core.addExp]                    [NPC.refreshPool]  [Progression.collectStats]
                        │
                CoreLeveledUpEvent
                        │
                 [CoreUnlockManager]
                        │
        ┌───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼
   [Mining 활성화]  [NPC모집 활성화]  [SkillTree 활성화] [Structure 신규해금]


11. 데이터 흐름 (Config → Runtime → Persistence)

11.1 정적 데이터(Config) 로드 흐름

서버 시작
  → CoreDefensePlugin.onEnable()
  → ModuleInitializer.initialize()
      1) ConfigService.loadAll()  (resources/config 하위 전체 YAML 파싱)
      2) 각 Registry.populate(ConfigService)
           - WeaponRegistry ← guns.yml
           - MonsterRegistry ← (wave 폴더 내 몬스터 참조 데이터)
           - ClassRegistry ← classes.yml, specializations.yml
           - TraitRegistry ← npc_traits.yml
           - OreRegistry ← ores.yml
           - StructureRegistry ← walls.yml, turrets.yml
           - MetaUpgradeTree ← meta_upgrades.yml
      3) ListenerRegistrar.registerAll()
      4) CommandRegistrar.registerAll()

11.2 런타임 데이터 흐름 (한 판 진행 중)

GameSession (메모리 상주, 세션 종료 시 소멸)
  ├─ CoreEntity (HP/레벨/에너지) — 인메모리, 매 틱 갱신
  ├─ WaveManager 상태 — 인메모리
  ├─ List<GameNpc> — 인메모리 (사망 시 소멸 or LegacyTransfer로 일부 값만 이전)
  ├─ List<WallInstance>/List<Turret> — 인메모리
  └─ SessionStatsCollector — 인메모리 누적(처치 수, 채광량, 생존 시간 등)

세션 종료 시:
  GameSessionEndedEvent
    → ScoreCalculator.calculate(SessionStatsCollector 스냅샷)
    → ProgressionService.applyScore(player, score)
    → PersistenceService.save(PlayerProgressionData)  ← 영속화 지점

11.3 영속 데이터 흐름 (플레이어별 영구 성장)

플레이어 접속
  → PersistenceService.load(playerId) → PlayerProgressionData 메모리 캐시
  → (게임 중에는 캐시만 참조, 실시간 DB 접근 없음 — 성능 고려)
플레이어 퇴장 or 런 종료
  → PersistenceService.save(playerId, data) (비동기 스레드에서 처리)

11.4 설계 근거


정적 데이터(Config)와 동적 데이터(Runtime State)와 영속 데이터(Player Progression)를 명확히 3분류하여, "이 값은 코드 재시작해야 바뀌는지 / 게임 한 판 안에서만 유효한지 / 영구히 저장되어야 하는지"를 클래스 설계 단계에서부터 명확히 한다.
런타임 중에는 DB/파일 I/O를 최소화(입장/퇴장/런 종료 시점에만 발생)하여 틱 성능에 영향을 주지 않도록 한다.



12. 직업 및 전문화 시스템 (상세)

12.1 데이터 구조 예시 (classes.yml 설계, 실제 값이 아닌 구조 예시)

yamlclasses:
  GUNNER:
    role: ASSAULT
    base_weapon_group: FIREARM
    base_stats: { attack: 8, defense: 3, mobility: 6 }
    specializations: [SINGLE_SHOT, BURST, SNIPER]
  MEDIC:
    role: SUPPORT
    base_weapon_group: SIDEARM
    base_stats: { attack: 3, defense: 4, mobility: 5 }
    specializations: [HOT_HEAL, AOE_HEAL, FOCUS_HEAL]
  # ... 9개 직업 전체 동일 패턴

Specialization은 별도 specializations.yml에서 skill_tree_id, ultimate_skill_id, passive_bonus를 정의하며 ClassDefinition과는 참조(ID)로만 연결되어 서로 독립적으로 수정 가능하다.

12.2 27개 전문화 전체 목록 (설계 기준 확정본)

병과직업전문화 A전문화 B전문화 C돌격군총사단발연발저격돌격군검사쌍검단검장검돌격군궁사곡궁쇠뇌슬링샷지원군광부성급함행운효율지원군메딕지속 힐범위 힐집중 힐지원군연구원농사경험치버프방어군메카닉자폭봇견제봇지원봇방어군빌더유지보수강화오버클럭방어군파이터극딜CC방어

12.3 전문화 선택 및 성장 흐름


코어 레벨 4 도달 → ClassSelectionMenu 오픈 → 병과/직업 선택 (ClassSelectedEvent)
코어 레벨 5 도달 → SpecializationMenu 오픈 → 3종 중 1종 선택 (SpecializationSelectedEvent)
이후 스킬 포인트(웨이브 클리어/처치 수 기반 지급)를 SkillTree에 투자 → 패시브/액티브/궁극기 순차 해금
전문화는 한 런 내 1회 확정을 기본 원칙으로 하되, 영구 성장 트리에서 "전문화 재선택권"을 해금 아이템으로 판매하여 자유도와 진행형 성장의 균형을 맞춘다.


12.4 밸런스 설계 원칙


3분화는 항상 "물량형 vs 순간화력형 vs 유틸/방어형"의 삼각 구도를 지키도록 설계(가위바위보 관계는 아니지만 상황별 우위가 갈리도록).
궁극기는 공용 쿨다운 풀(UltimateCooldownPool)을 두어, 협동 플레이 시 여러 명이 동시에 궁극기를 난사해 밸런스가 붕괴하지 않도록 파티 단위 궁극기 게이지 공유 옵션을 Config로 토글 가능하게 한다(shared_ultimate_gauge: true/false).


12.5 확장 방향


신규 직업 추가 시 classes.yml에 항목 추가 + ClassRegistry에 자동 반영(리로드 커맨드로 핫스왑 가능하도록 ReloadableConfig 인터페이스 구현).
전문화 4번째 슬롯(하이브리드/각성 전문화)을 후반 확장 콘텐츠로 추가할 수 있도록 Specialization 목록을 고정 3개가 아닌 List<Specialization>으로 설계.



13. FPS 총기 시스템 (상세)

13.1 총기 아이템 계층


WeaponDefinition (Record): id, displayName, damage, fireRate, magazineSize, reloadTimeTicks, projectileSpeed, falloffCurve, requiredClass(optional), rarity
실제 아이템은 커스텀 모델 데이터(리소스팩 연동, CustomModelData 또는 1.21의 아이템 컴포넌트 item_model)를 사용하여 시각적으로 총기별 외형을 구분.


13.2 발사 판정 파이프라인


입력 감지: 좌클릭(PlayerInteractEvent, 인터랙트 쿨다운 문제 우회를 위해 필요 시 패킷 레벨 감지 병행 고려) 또는 우클릭(조준).
탄퍼짐/반동 계산: SpreadPolicy(정지/이동/조준 상태별 탄퍼짐 각도 계산).
레이캐스트: World#rayTraceEntities + World#rayTraceBlocks를 함께 호출하여 지형에 가려지면 무효 판정.
판정 결과 → DamageCalculator → CombatDamageService.applyDamage.
시각 효과: 트레이서 파티클(ParticleUtils), 총구 화염, 임팩트 파티클/사운드는 판정과 완전히 분리된 순수 연출 레이어(WeaponVfxService)에서 처리 — 즉 서버 판정 로직과 클라이언트 체감 연출을 분리하여, 연출 코드 수정이 밸런스에 영향을 주지 않도록 한다.


13.3 총사 전문화별 발사 방식 매핑

전문화FireModeStrategy 구현체특징단발SingleShotStrategy클릭당 1발, 높은 정확도, 헤드샷 배율 최대연발BurstFireStrategy클릭당 3점사 또는 자동연사, DPS 우위, 탄퍼짐 큼저격SniperShotStrategy조준(줌) 필수, 관통 판정 지원, 재장전 김

13.4 검사/궁사 무기 계열


근접(검사)은 MeleeWeapon/MeleeAttackHandler로 별도 처리하되, 데미지 계산은 동일한 DamageCalculator를 공유(무기 카테고리만 다르고 계산 로직은 통일 — 유지보수성 확보).
궁사는 투사체형 근접도 원거리도 아닌 중간 형태로, ProjectileFactory를 Firearm과 공유하되 궤적에 중력 보정을 추가하는 ArcProjectile 서브타입을 사용.


13.5 확장 방향


총기 부착물(스코프/소음기/확장탄창) 시스템을 WeaponAttachment 인터페이스로 추후 추가 가능하도록 AbstractFirearm에 List<WeaponAttachment> attachments 필드를 예비로 설계.
총기 획득 방식(런 내 드랍/상점/영구 해금)을 WeaponAcquisitionPolicy로 분리하여 이후 시즌 콘텐츠(한정 스킨/특수 총기)를 쉽게 얹을 수 있게 한다.



14. NPC 시스템 (상세)

14.1 NPC 생애주기 (State 다이어그램)

RECRUITED → IDLE ⇄ WORKING (생산직)
                 ⇄ FIGHTING (전투직 또는 전투 배치된 생산직)
                 → DOWNED (빈사, 구조 가능 창) → REVIVED(→IDLE) or DEAD
                 → DEAD → LegacyTransferService 처리 → 세션에서 제거


NpcState 전이는 NpcStateMachine이 전담하며, 각 상태 진입 시 애니메이션/AI 스크립트를 교체하는 방식으로 구현(State 패턴).
DOWNED 상태는 회의에서 논의된 "구조 시스템"의 구현체로, 일정 시간 내 근처 아군(플레이어 또는 메딕류 NPC)이 상호작용하면 ReviveService.revive(npc) 호출, 시간 초과 시 자동으로 DEAD 전이.


14.2 배치 전략 (생산 NPC vs 전투 NPC)


NpcRole.PRODUCTION : 기지 내부 안전지대(SafeZone 폴리곤/영역)에서만 활동. SafeZoneService가 좌표 기반으로 안전 여부 판정.
NpcRole.COMBAT : 전선(코어 주변 방어선) 배치, 사망 위험 높음, 대신 경험치 성장 속도 배율(combatExpMultiplier)이 생산직보다 높게 설계되어 "하이리스크 하이리턴" 선택지가 되도록 함.
몬스터가 안전지대 내부까지 침투(장벽 붕괴 등)하면 생산 NPC도 위험에 노출되는 구조로, 이는 SafeZoneBreachedEvent를 통해 처리(장벽 파괴 이벤트와 연동).


14.3 특성(Trait)과 공명(Resonance) 시스템 상세


NPC 1인당 특성은 정확히 1개(회의 확정 사항). TraitRegistry에 정의된 특성 목록에서 모집 시 랜덤 부여, 리롤권으로 재추첨 가능(기본 3회, 영구 성장으로 확장 가능).
ResonanceCalculator.calculate(session):

세션 내 전체 NPC의 특성을 집계(Map<TraitId, Integer> traitCounts)
각 특성별로 count - 1을 겹침 수로 보고 bonus = min(cap, count_overlap * 0.07)로 1차 계산(회의에서 제안된 7% 기준치, cap은 Config화하여 후반 폭주 방지)
NPC의 실제 NpcJob이 특성의 친화 직업과 일치하면 bonus *= affinityMultiplier(기본 1.0, 불일치 시 0.3 등으로 감쇠) — 이는 "실질적 광질 보너스는 광부만 의미 있게"라는 회의 요구사항의 구현.
계산된 최종 보너스를 각 NpcStatSheet.applyResonanceBonus(bonus)에 반영.



공명 레벨(공명 보너스 총합의 구간)에 따라 NpcCollaborationUnlockService가 "상위 광물 자동 합성" 등 협업 효과를 단계적으로 해금(회의 제안 반영), 해금 기준은 resonance_thresholds.yml로 관리.


14.4 전직(전문화) 시스템


NPC도 플레이어와 유사하게 일정 레벨(npc_job_promotion_level Config) 도달 시 JobSkillTree의 상위 분기(전직) 선택 UI가 뜨도록 하여, 광부라면 "채굴 전문가"류 상위 전직으로 분화.
전직 데이터는 npc_traits.yml과 분리된 npc_job_promotions.yml에서 관리하여, NPC 콘텐츠 확장 시 플레이어 직업 밸런스에 영향이 가지 않도록 격리.


14.5 모집소(Recruitment) 시스템


RecruitPool.generateOffers(session) : 코어 레벨별 RecruitPoolWeightTable을 참조해 후보 3인 생성(특성/직업 성향 랜덤).
RecruitmentService.rerollOffers(session) : 자원(코어 에너지 또는 별도 재화) 소모하여 재생성.
NpcCapacityPolicy.getMaxCapacity(coreLevel) : 코어 레벨별 최대 보유 인원 테이블 조회. 초과 시 기존 NPC 교체/방출 UI(NpcReplaceMenu) 노출.


14.6 확장 방향


NPC 외형 커스터마이징(스킨/장비 착용) 추가 시 GameNpc에 EquipmentSlotSet 필드만 추가하면 되도록 사전 설계.
다중 파티(대규모 협동) 환경에서 NPC 소유권을 팀 단위로 공유할지 개인 단위로 할지 NpcOwnershipPolicy로 토글 가능하게 설계.



15. 웨이브 시스템 (상세)

15.1 웨이브 데이터 구조 예시 (wave_definitions.yml)

yamlwaves:
  - id: 1
    spawn_interval_ticks: 40
    monsters:
      - { type: ZOMBIE_GRUNT, count: 8, spawn_point_group: OUTER_RING }
    reward_table: WAVE_REWARD_TIER_1
  - id: 5
    is_boss_wave: true
    boss: { type: STONE_GOLEM_BOSS, count: 1 }
    monsters:
      - { type: SKELETON_ARCHER, count: 10, spawn_point_group: OUTER_RING }
    reward_table: WAVE_REWARD_TIER_BOSS_1


웨이브 난이도 곡선은 WaveScalingPolicy(순수 함수)로 별도 분리하여, 몬스터 수/스탯을 코어 레벨·파티 인원수에 비례해 동적으로 스케일링(협동 인원이 많을수록 난이도 상승 — 멀티플레이 밸런스 핵심 로직).


15.2 스폰 포인트 그룹 전략


맵 디자인 시 SpawnPointGroup(예: OUTER_RING, NORTH_BREACH 등)을 스키매틱과 함께 사전 정의하고, WaveSpawnScheduler가 그룹 ID로만 참조 → 맵을 교체해도 웨이브 데이터는 그대로 재사용 가능(맵-웨이브 데이터 분리).


15.3 승리/패배 조건의 확장성


WaveClearCondition 전략 인터페이스로 일반 웨이브(전멸)와 보스 웨이브(보스 처치) 조건을 분리했듯, 향후 "생존 시간 클리어", "특정 오브젝트 보호" 등 신규 조건도 동일 인터페이스 구현체 추가만으로 대응 가능.


15.4 인터미션(REWARD) 페이즈 설계


타이머 기반 자동 진행 + 플레이어 전원 "준비 완료" 투표(ReadyVoteService) 시 즉시 다음 웨이브로 스킵 가능하게 하여 협동 템포를 플레이어가 조절할 수 있게 한다.



16. 코어 시스템 (상세)

16.1 코어 스탯/레벨 곡선


CoreLevelRegistry가 레벨 1~N까지 최대 HP, 필요 경험치, 에너지 총량 상한을 데이터로 관리(core.yml). 레벨업 경험치 요구량은 지수형 곡선(exp(n) = base * growth^n)을 기본으로 하되 Config 상수로 튜닝.


16.2 코어 에너지(전력) 시스템 상세


CoreEnergyManager는 매 틱마다 총 발전량 - 총 소비량을 계산하는 것이 아니라, 요청 기반(pull) 배분 모델을 사용: EnergyConsumer 구현체들이 필요할 때 requestEnergy()를 호출하고 CoreEnergyManager가 우선순위(EnergyPriority: CORE_DEFENSE > STRUCTURE > UTILITY)에 따라 배분.
에너지가 부족하면 낮은 우선순위 소비처(예: 버프타워)부터 자동 다운그레이드(onEnergyStarved() 콜백) — 이는 "전력 공유를 통한 전략적 선택"이라는 회의 요구사항의 핵심 구현.


16.3 코어 상태(State) 및 연출


CoreState 전이 임계값(예: HP 50% 이하 DAMAGED, 20% 이하 CRITICAL)은 Config화. 상태 전이 시 파티클/사운드/BossBar 색상 변경 등은 CoreVisualFeedbackService가 전담(로직과 연출 분리 원칙 재적용).


16.4 코어 외형 변화 (회의 제안 반영)


레벨 구간별로 코어 주변에 스키매틱을 단계적으로 페이스트(SchematicPasteService)하여 기지가 시각적으로 성장하는 느낌을 구현. 스키매틱 파일과 레벨의 매핑은 core_visual_stages.yml로 관리하여 아티스트가 코드 없이 교체 가능.



17. 광산 시스템 (상세)

17.1 클릭 채광 처리


ClickMiningHandler는 특정 광맥 블록(커스텀 블록 또는 PersistentDataContainer 태깅된 바닐라 블록) 좌클릭 시 MiningSession.addPoints(clickValue) 호출.
클릭 가치(clickValue)는 플레이어 장비/영구 업그레이드 보너스를 반영한 계산식으로, MiningEfficiencyPolicy.calculatePlayerClickValue(player)가 담당.


17.2 광물 티어 해금


OreType은 requiredCumulativePoints 필드를 가지며, 누적 포인트가 임계치를 넘으면 OreUnlockedEvent 발행 → 채광 확률 테이블(OreDropTable)에 신규 티어 추가.


17.3 NPC 자동 채광과의 상호작용


AutoMiningTicker는 광부 NPC 각각에 대해 MiningEfficiencyPolicy.calculateNpcClickEquivalent(npc)를 계산하여 실제 사람 클릭과 동일한 파이프라인(MiningSession.addPoints)에 합류시킨다 — 즉 "사람 클릭"과 "NPC 자동 클릭"이 동일한 자료구조를 공유하여 로직 중복을 없앤다.
광부 스탯이 특정 임계치를 넘으면 사람보다 효율이 높아지는 회의 요구사항은 MiningEfficiencyPolicy 내부의 스탯-효율 변환 곡선으로 구현(선형이 아닌 체감형 곡선을 권장 — 무한 성장으로 인한 밸런스 붕괴 방지).


17.4 광물 → 코어 에너지 환산


채광된 광물은 즉시 소모되는 것이 아니라 PlayerInventory 또는 SharedResourcePool(협동 공유 자원)에 축적되고, 코어/구조물 건설·업그레이드 시 소모된다. 광물의 코어 에너지 환산 비율은 OreType.energyConversionRate 필드로 관리.


17.5 확장 방향


광산 던전(별도 인스턴스 공간에서 진행하는 채광 미니게임)으로 확장할 수 있도록 MiningSession을 코어와 완전히 분리된 독립 모듈로 설계.



18. 장벽 및 포탑 시스템 (상세)

18.1 장벽 재질 티어 테이블

티어재질상대 체력(예시 배율)1참나무 울타리1.0x2가문비 울타리1.5x3돌담2.5x4철격자4.0x5강화방벽6.5x


실제 수치는 walls.yml에서 관리하며 위 표는 설계 의도 예시.


18.2 장벽 강화 모듈 슬롯


WallInstance는 List<WallModule> moduleSlots(기본 1~2슬롯, 업그레이드로 확장)를 가지며, 가시(반사 데미지)/전기(기절)/폭발(광역) 모듈은 각각 WallModule 인터페이스 구현체. 모듈 장착/해제는 빌더 직업의 "강화" 전문화와 연계.


18.3 포탑 티어 및 재화 매핑 (회의 확정)

포탑필요 재화(탄약 소모원)활포탑나무슬링샷돌화염방사기석탄미니건구리버프타워레드스톤/청금석/에메랄드경량탄총금기관포철미사일다이아/네더라이트핵미사일네더의 별


TurretDefinition은 ammoOreType(위 표의 재화를 OreType ID로 참조)을 가져 광산 시스템과 자연스럽게 연동된다.


18.4 포탑 타겟팅 전략


TurretTargeting 인터페이스 구현체: NearestTargetStrategy, LowestHpTargetStrategy, HighestThreatTargetStrategy(위협도 = 코어까지 남은 거리 등 가중치). 포탑별 기본 전략은 Config로 지정하되, 메카닉 직업의 "견제봇" 전문화 스킬로 런타임에 전략을 스왑할 수 있게 Turret.setTargetingStrategy()를 공개 API로 둔다.


18.5 배치 및 건설 시스템


StructurePlacementService.tryPlace(player, structureId, location) : 자원 소모 검증 → 배치 가능 영역 검증(BuildableZoneService) → 성공 시 StructurePlacedEvent 발행.
건설/철거 권한은 팀 단위로 관리(GameTeam.canBuild(player)), 추후 "역할별 건설 권한 제한" 확장을 고려해 boolean이 아닌 BuildPermissionPolicy 인터페이스로 설계.



19. 영구 성장 시스템 (상세)

19.1 메타 재화 및 점수 계산


ScoreCalculator.calculate(SessionStats stats) 예시 가중치 구조:

생존 웨이브 수 × W1
몬스터 처치 수 × W2
도달 코어 레벨 × W3
런 종료 시점 생존 NPC 수 × W4
(패배 시) 페널티 없음 — 로그라이크 특성상 "실패해도 보상"이 동기부여 핵심이므로 최소 보장 점수(baseScoreFloor) 지급.



가중치(W1~W4)는 score_weights.yml로 관리하여 시즌별 메타 변화에 대응.


19.2 영구 업그레이드 트리 구조


MetaUpgradeTree는 그래프 구조(MetaUpgradeNode가 선행 노드 리스트를 가짐)로, 예: "시작 무기 업그레이드 라인", "시작 코어 체력 라인", "특성 리롤권 시작 지급 라인", "신규 직업 해금 라인" 등 다중 트리를 병렬로 운용.
노드 타입(UpgradeEffectType): STAT_BONUS(수치 보정), UNLOCK(콘텐츠 해금), STARTING_ITEM(시작 장비 지급) — Strategy 패턴으로 효과 적용 로직 분리.


19.3 재화-트리 연동 흐름

GameSessionEndedEvent → ScoreCalculator → MetaCurrency 지급
    → PlayerProgressionData.addCurrency(amount)
플레이어가 로비 GUI(MetaUpgradeMenu)에서 노드 구매
    → MetaUpgradeTree.purchase(playerData, nodeId)
    → 검증(재화 충분?/선행조건 충족?) → 성공 시 UpgradeEffectType 적용 + 저장

19.4 확장 방향


시즌 초기화(프레스티지) 시스템을 고려하여 PlayerProgressionData에 seasonId 필드를 예비 설계, 시즌 종료 시 일부 트리만 초기화하고 코스메틱/기록은 유지하는 정책을 이후 손쉽게 추가 가능.



20. 저장 시스템 (상세)

20.1 저장 대상 데이터 분류

데이터저장 시점저장소 후보PlayerProgressionData (영구 성장)접속 시 로드, 변경 시 비동기 저장, 퇴장 시 강제 flushYAML → SQLite/MySQLGameSession 스냅샷 (재시작 복구용, 선택적)서버 크래시/종료 시JSON 파일통계/랭킹 데이터 (확장 기능)런 종료 시SQL 전용 (집계 쿼리 필요하므로)

20.2 Repository 추상화 설계


Repository<ID, T> 인터페이스를 두고, PersistenceService가 DataStoreType(Config: FLAT_FILE / SQLITE / MYSQL)에 따라 알맞은 구현체를 조립(Factory + 의존성 주입)한다.
모든 저장/조회는 반드시 비동기(CompletableFuture 또는 Paper의 비동기 스케줄러) 로 수행하여 메인 스레드 블로킹을 방지. 단, 플레이어 로그인 직후 데이터가 필요한 시점 등 동기 대기가 불가피한 구간은 최소화하고 타임아웃/로딩 UX를 함께 설계.


20.3 SQL 스키마 설계 방향 (개념 수준)


players(uuid PK, meta_currency, created_at, updated_at)
player_upgrades(player_uuid FK, upgrade_node_id, purchased_at)
player_stats(player_uuid FK, total_runs, best_wave, total_kills, ...)
SqlSchemaMigrator가 버전 넘버 기반으로 순차 마이그레이션 스크립트를 실행하여, 이후 컬럼 추가/변경 시 기존 데이터 손실 없이 확장 가능.


20.4 데이터 무결성/동시성 고려


동일 플레이어의 동시 저장 요청은 PlayerDataLock(플레이어 UUID 기준 뮤텍스 또는 큐)으로 직렬화하여 레이스 컨디션 방지.
저장 실패 시 재시도 큐(FailedSaveRetryQueue)를 두어 일시적 DB 장애에도 데이터 유실을 최소화.



21. Config 구조 (전체 정리)

21.1 Config 설계 원칙


모든 Config는 ReloadableConfig 인터페이스(void reload(); void validate();)를 구현하여, 관리자 커맨드(/coredefense admin reload)로 서버 재시작 없이 핫리로드 가능하게 한다.
validate()는 로드 직후 필수 필드 누락/참조 무결성(예: TurretDefinition.ammoOreType이 실제 존재하는 OreType ID인지)을 검증하여, 잘못된 YAML로 인한 런타임 NPE를 사전 차단한다.


21.2 최상위 Config 파일 목록 및 책임

파일책임core.yml코어 레벨 곡선, 에너지 총량, 상태 임계값, 해금 매핑waves/wave_definitions.yml일반 웨이브 구성waves/boss_waves.yml보스 웨이브 구성weapons/guns.yml총기 스탯/발사방식 매핑weapons/melee.yml근접무기 스탯classes/classes.yml9직업 정의classes/specializations.yml27전문화 정의 및 스킬트리 참조npc/npc_traits.ymlNPC 특성 목록 및 보너스npc/npc_recruit_pool.yml모집 후보 가중치 테이블mining/ores.yml광물 티어, 해금 조건, 에너지 환산율structures/walls.yml장벽 재질 티어structures/turrets.yml포탑 종류/탄약원/타겟팅 기본 전략progression/meta_upgrades.yml영구 업그레이드 트리progression/score_weights.yml점수 계산 가중치resonance_thresholds.ymlNPC 공명 레벨별 협업 해금 기준core_visual_stages.yml코어 레벨별 외형 스키매틱 매핑

21.3 ConfigService 접근 패턴


모든 도메인 클래스는 원시 FileConfiguration을 직접 다루지 않고, 타입 안전한 ConfigModel 레코드(예: CoreConfigModel, WaveConfigModel)로 역직렬화된 객체만 참조한다. 이를 통해 YAML 키 오타로 인한 버그를 컴파일 타임 가까이 앞당긴다 (역직렬화 시점에 검증).
ConfigLoader는 SnakeYAML 또는 Paper 내장 YAML 파서를 기반으로 하되, 필요 시 Jackson-YAML로 교체 가능하도록 ConfigParser 인터페이스로 파서 자체도 추상화한다.



22. 멀티플레이 및 동기화 고려사항

22.1 세션/파티 모델


GameSession은 1개 이상의 GameTeam을 가질 수 있고(협동 인원 다수), 자원(코어 에너지, 채광 포인트, 메타 업그레이드 이외의 세션 내 재화)은 기본적으로 팀 공유(Shared Resource Pool) 로 설계하여 협동의 재미를 살린다. 단, 개인 스탯/영구 성장은 철저히 개인 소유로 분리.


22.2 동시 접근 데이터의 동기화 전략


코어 에너지 요청, 광산 채광 포인트 누적처럼 여러 플레이어/NPC가 동시에 접근하는 자료구조는 원자적 연산(AtomicInteger/AtomicLong) 또는 메인 스레드 틱 큐잉(ActionQueue)을 통해 처리하여 레이스 컨디션을 방지한다. Paper/Bukkit은 기본적으로 단일 메인 스레드 이벤트 처리 모델이므로, 대부분의 게임 로직은 메인 스레드에서 순차 처리되어 별도 락 없이도 안전하지만, 비동기 저장/로드 작업과의 경계에서는 명시적 스레드 안전성 검토가 필요하다.


22.3 Folia(리전 기반 멀티스레딩) 호환성 고려


Paper 생태계의 최신 흐름인 Folia(엔티티/청크별 리전 스레드 분산)를 염두에 두어, 전역 상태(GameSession, CoreEntity)에 대한 접근은 항상 해당 리전의 스레드에서만 이루어지도록 RegionizedScheduler 래퍼(GameScheduler 인터페이스로 추상화)를 통해 스케줄링한다. 이렇게 하면 순정 Paper와 Folia 양쪽에서 동일 코드베이스로 동작 가능.
코어와 그 주변 방어 지역은 하나의 "월드 리전"에 고정 배치되도록 맵을 설계하여, 리전 간 엔티티 이동으로 인한 동기화 복잡도를 최소화한다.


22.4 클라이언트 체감 동기화 (FPS 특성상 중요)


히트 판정은 서버 권위(Server Authoritative) 원칙을 지키되, 판정 지연 체감을 줄이기 위해 근거리 판정은 즉시 처리 + 원거리/고TPS부하 상황에서는 판정 유예 프레임을 최소화하는 방향으로 RayTraceUtil 호출 빈도를 최적화한다.
다인원 협동 시 파티클/사운드 연출이 과도하게 중첩되지 않도록 VfxThrottleService로 동일 틱 내 이펙트 발생량을 상한 제어(성능+가독성 동시 확보).


22.5 확장 방향


향후 서버 간 세션 이전(크로스 서버 로비→게임 서버 전환, Velocity/BungeeCord 연동)을 고려하여 PlayerProgressionData 로드/저장을 플러그인 시작 시점이 아닌 명시적 서비스 호출 지점으로만 한정해, 프록시 환경에서도 재사용 가능하도록 설계.



23. 성능 최적화 전략

23.1 틱 부하 관리


웨이브 중 다수의 몬스터 AI(MonsterAI.tick())는 매 틱이 아닌 분산 틱(Staggered Tick) 방식으로 처리(예: 몬스터를 4개 그룹으로 나누어 그룹별로 4틱에 1번씩 순환 처리)하여 순간 부하를 평준화한다.
포탑 타겟팅 탐색(TurretTargeting)은 매 틱 전체 엔티티 스캔 대신, 청크 기반 공간 분할(SpatialIndex, 예: Grid 기반 broad-phase)을 활용해 탐색 범위를 좁힌다.


23.2 이벤트 폭주 방지


MonsterKilledEvent처럼 짧은 시간에 대량 발생 가능한 이벤트는 구독자 측에서 즉시 처리하지 않고 배치 집계(Batch Aggregation) 방식(예: 1틱 동안의 처치 이벤트를 모았다가 틱 종료 시 일괄 정산)을 적용해 리스너 호출 오버헤드를 줄인다.


23.3 파티클/사운드 최적화


플레이어와의 거리 기반으로 파티클 디테일을 낮추는 LOD(Level of Detail) 정책(VfxLodPolicy)을 적용하고, Player#spawnParticle의 대상 플레이어 한정 전송(전체 브로드캐스트 대신 근거리 플레이어에게만 전송)을 기본으로 한다.


23.4 저장 I/O 최적화


플레이어 데이터 저장은 변경분이 있을 때만(Dirty Flag 패턴) 비동기로 flush하며, 짧은 시간 내 중복 저장 요청은 디바운스(Debounce, 예: 5초 내 중복 요청 병합)한다.


23.5 메모리 관리


런 종료 후 GameSession 및 그에 딸린 모든 인메모리 객체(NPC, 구조물, 몬스터 참조)는 명시적으로 dispose()하여 GC 대상이 되도록 하고, 이벤트 리스너 등록 해제(unregister)를 세션 종료 훅에서 반드시 수행해 메모리 누수를 방지한다.


23.6 프로파일링 및 모니터링 지점


주요 시스템(웨이브 스폰, 포탑 타겟팅, 데미지 계산, 저장 I/O)에 PerformanceMonitor(간단한 타이머 유틸)를 삽입 지점으로 예비하여, 운영 중 병목 구간을 계측 가능하게 한다.


