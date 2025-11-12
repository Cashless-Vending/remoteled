plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.remoteled"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.remoteled"
        minSdk = 26  // Lowered for broader compatibility
        targetSdk = 34
        versionCode = 2
        versionName = "2.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        
        // API Base URL
        buildConfigField("String", "API_BASE_URL", "\"http://10.41.121.73:9999\"")
        // Demo flag: when true, skip network and drive mock flow
        buildConfigField("boolean", "DEMO_MODE", "false")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

dependencies {

    // AndroidX Core
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.constraintlayout)
    implementation(libs.navigation.fragment)
    implementation(libs.navigation.ui)
    implementation(libs.activity)
    implementation(libs.cardview)
    implementation(libs.recyclerview)
    
    // QR Code Scanner
    implementation(libs.zxing.android.embedded)
    implementation(libs.core)
    
    // Networking - Retrofit + OkHttp
    implementation(libs.retrofit)
    implementation(libs.retrofit.gson)
    implementation(libs.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)
    
    // Image Loading - Glide
    implementation(libs.glide)
    
    // Testing
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}