$env:JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
$env:Path="$env:JAVA_HOME\bin;$env:Path"
cd C:\DATA\PETS\TEST\T6A2-POLLEN\sprout\code\pollen
.\gradlew assembleDemoDebug
Copy-Item "app\build\outputs\apk\demo\debug\pollen-demo.apk" -Destination "..\..\demo\pollen-demo.apk" -Force
.\gradlew assembleDeviceDebug
Copy-Item "app\build\outputs\apk\device\debug\pollen-device.apk" -Destination "..\..\demo\pollen-device.apk" -Force
adb install -r "..\..\demo\pollen-demo.apk"
adb install -r "..\..\demo\pollen-device.apk"
