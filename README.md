# gphoto2 MultiCam Tethering Utility
This is a Multi-Camera Tethering Utility for Linux. It was designed for a multi-angle (multi-camera) product photo shoot. It uses the [gphoto2](http://gphoto.org/doc/manual/using-gphoto2.html) command line interface to communicate with tethered cameras, so camera support will depend on [libgphoto2 supported cameras](http://gphoto.org/proj/libgphoto2/support.php).

Features:
- simultaneously tether to multiple cameras for remote triggering
- custom name for each camera
- take photos with all cameras
- automatic download of the images
- open photos for viewing after download
- choose folder to which images are saved
- image filename is a combination of given shot name and custom camera names

Remote configuration is not implemented. When triggered remotely, the camera takes a photo just as if the shutter button was pressed, so if you want to adjust any settings, like adjusting white balance, changing ISO, switching from Auto to Manual mode, etc., make those changes on the camera just as you would if it was not tethered.

Tested on Linux Mint with Python 3.6, using three Canon Rebel T5i cameras.
Some of the console commands are Linux-only, notably gphoto2, which is Linux-only.
