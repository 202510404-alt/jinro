plugins {
    id("java-library")
    id("xyz.jpenilla.run-paper") version "3.0.2"
}

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
}

dependencies {
   
    compileOnly("io.papermc.paper:paper-api:1.21.11-R0.1-SNAPSHOT")
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
        // ⭕ 내 컴퓨터 자바 25를 완전히 무시하고, 
        // 빌드 전용 순정 Java 21을 백그라운드에서 격리 다운로드하여 컴파일하도록 강제 지정
        vendor.set(JvmVendorSpec.ORACLE)
    }
}

tasks {
    runServer {
        // ⭕ 여기도 1.21.1로 수정
        minecraftVersion("1.21.11")
        jvmArgs("-Xms2G", "-Xmx2G")
    }

    processResources {
        val props = mapOf("version" to version)
        filesMatching("plugin.yml") {
            expand(props)
        }
    }
}