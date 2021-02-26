# bravo-raspberrypi-demo

A simple demonstrator showing communication between the Bravo board and a Raspberry Pi device


## HW SETTINGS

 - Connect the Bravo board at the Raspberry Pi with the Berg connectors previously soldered (as reported in the Bravo Quick Start Guide)

![datei](./berg_connectors.PNG)

 - No external power is needed except for the Raspberry's 

 - Bring a GPIO from 1.8V from the Bravo board and connect it to GPIO19 of the Raspberry Pi (this GPIO is used to monitor the status of the modem (ON/OFF) from the Raspberry Pi)

 - Set UART SEL dip switches as shown below:

![datei](./CTS.PNG)

 - Insert a SIM card without PIN number inserted

 - Power on the modem with the power button on the Bravo Board




## SW SETTINGS

- Download the necessary files on a Directory in the Raspberry Pi (e.g. in the Desktop folder as "Desktop/Bravo_Project")

    - Bravo_PORT.py

    - settings.py

    - object_26250.xml

    - object_26251.xml

    - object_26242.xml


## Additional settings

In the `Bravo_PORT.py` file there are few parameters to configure:

 - `APN = ""` set it based on your mobile operator APN

 - Enable/disable the example you want to run between **"echo_demo"** or **"lwm2m_demo"** inside the `main` function


## Execution

To run the demo, execute the `Bravo_PORT.py` file

`./Bravo_PORT.py`

it will automatically search the `settings.py` file (if needed any of the required missing files will be copied in the module) and the demo previously selected will be executed.


