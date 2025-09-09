allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

// Use default Gradle build directories. Custom traversal can break Flutter paths.
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
