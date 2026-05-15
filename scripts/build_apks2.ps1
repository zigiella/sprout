$env:JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
$env:Path="$env:JAVA_HOME\bin;$env:Path"
cd C:\DATA\PETS\TEST\T6A2-POLLEN\sprout\code\pollen
.\gradlew assembleDemoRelease
Copy-Item "app\build\outputs\apk\demo\release\app-demo-release-unsigned.apk" -Destination "..\..\demo\pollen-demo.apk" -Force
.\gradlew assembleDeviceRelease
Copy-Item "app\build\outputs\apk\device\release\app-device-release-unsigned.apk" -Destination "..\..\demo\pollen-venation-ui.apk" -Force
