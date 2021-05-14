script.service.hyperion
=======================

Kodi add-on to capture video data and send it to Hyperion. Note that this plugin will not work for Kodi running on the Raspberry Pi, because the video capture interface is not (yet?) supported on this device.

Information about Hyperion can be found here: https://wiki.hyperion-project.org

The add-on can be installed by downlading the zip and extracting it to the add-on directory (probably ~/.xbmc/add-ons on Linux and C:\Users\user\AppData\Roaming\XBMC\addons on Windows)


Changes in this fork:
=======================

* Made it compatible with python3 and kodi 19.1
* Added fix for random screen flashing (not sure where I found this, I googled it last year and it was still adapted in my local hyperion version)
* Converted script.module.protobuf to python3 for kodi 19.1 (I just ran 2to3 on my folder and adjusted the addon.xml - I wasn't sure howto adjust the github repo with the build script..)

Howto Install:
=======================
1. Checkout/Download repo into ~/.kodi/addons/hyperion.kodi
2. Extract script.module.protobuf.tar.gz to ~/.kodi/addons/script.module.protobuf
3. Verify that both locations have addon.xml in their root
4. Install python3 protobuf by running: pip3 install protobuf

Notes:
=======================

* I read somewhere that there is a problem with autodiscovery - I use a fixed IP so I haven't checked that
