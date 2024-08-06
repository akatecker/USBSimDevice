# USBSimDevice
Connect various USB HID devices to MSFS via SimConnect
## Use case and alternatives to try first
This program has been written to overcome the difficulty to use some wiered and legacy Hardware with MSFS 2020. In fact, there is ready made software for the purpose of connecting more common hardware to MSFS, which I own, use and recommend for most use cases:
- [Spad.next](https://www.spadnext.com/home.html) is a popular option for this purpose. It is feature-rich and while not for complete beginners to programming, it is well maintained, offers a fast way to get the most out of some of the most popular Hardware devices - if supported - and is well worth the price. 
- [Mobiflight](https://www.mobiflight.com/en/index.html) Though the main focus of this open-source software was as a backend to your DIY hardware, it also features support for more popular Flight Simulator gear. In fact you should install Mobiflight in any case as it offers additional SimConnect Events like a functioning Garmin GS1000 support.

If those options do not work for you, for example because your hardware is to old, never intended for the purpose, the original software provide by the manufacturer is too limited, etc ... then this project might be a starting point for you.
## Using the sample application
This project consists of the USBSimDevice class (see later) and a reference application that illustrates the 
## Hardware implemented in the sample application
### MFT Challange Disk
The Challage Disk is originaly a therapeutical device manufactured for training and documentation of body balance. Using USBSimDevice sample application, you will be able to control elevator and aileron of an aircraft by shifting your body weigth up and down, left and right.  
### Contour Pro Wheele
Originaly intended for video cutting, the contour pro wheel features a rotary encoder, some zoom wheel and 5 buttons. Using USBSimDevice sample application, it is configued for the Garmin GS1000 direct to and waypoint selection. 
### Turtle Beach Velocity One Flight Yoke
While all imputs of the Velocity One Flight Yoke are directly supported by MSFS, the LED lights of the annunciator panel are not. There is a proprietary software, but it does only support a few variables and requires you to install yet another driver. Unfortunately, the impelentation is currently incomplete as the stop-watch function of the yoke is not yet implemented and there seems to be no way to control the LEDs on the throttle quadrant. 
### Saitek Multi Panel / Switch Panel
The Saitek panels are well established and well documented hardware addons for various flight simulators. The USBSimDevice sample application follows up on the project by [xxxx](https://www.github.com/xxx/fpanel), which has a very complete documentation but seems unfortunately to be discontinued.
## Some basics about the USBSimDevice Class
The complete documention of the USBSimDevice class method can be found at [USBSimDevice.md](USBSimDevice.md).
### Dependencies
- hidapi 0.14.0
- hidapi library 
- pysimconnect 0.2.6
### Reverse engineering USB devices
### Using SimConnect
### Limitations