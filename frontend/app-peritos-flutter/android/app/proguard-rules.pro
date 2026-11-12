# AegisCore App & Activity
-keep class com.aegiscore.aegiscore_peritos.** { *; }
-keep class com.aegiscore.aegiscore_peritos.MainActivity { *; }

# Flutter Local Notifications
-keep class com.dexterous.flutterlocalnotifications.** { *; }

# Desugaring
-keepattributes *Annotation*
-keepclassmembers class * {
    native <methods>;
}

# Flutter Wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# SQL & Plugins
-keep class com.tekartik.sqflite.** { *; }
-keep class dev.fluttercommunity.plus.** { *; }

# Play Core suppression for deferred components
-dontwarn com.google.android.play.core.**

