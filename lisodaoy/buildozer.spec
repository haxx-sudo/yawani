# Build Android APK on Linux or WSL:
#   pip install buildozer
#   buildozer android debug
#
# Install the APK from bin/*.apk on your phone (enable unknown sources).

[app]
title = Tech Support Cafe
package.name = techsupportcafe
package.domain = org.techsupport
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1

android.api = 33
android.minapi = 24
android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a
android.entrypoint = org.kivy.android.PythonActivity
p4a.bootstrap = sdl2
# master branch no longer exists — use develop
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
