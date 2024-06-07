
# **USBSimDevice**

The `USBSimDevice` class encapsulates the interaction with USB HID devices to be used by MSFS 2020. The class keeps track of all active instances via the `Workers` class variable. Although `USBSimDevices` does not directly interact with SimConnect, instances can be configured with actions to do so, and the class variable `Simvars` can then be used to keep track of all necessary simvars.

## Methods

### `__init__`

```
def __init__(vendor_id, product_id, interface=0, method=METH.READ, default=(b'\x00' * 64)):
```

Initializes the class instance with parameters specific to a certain HID device. A reference to the instance is placed into the `Workers` list of the class. There should be only one instance per USB device, supporting read and write methods.

#### Args:
- **vendor_id (int)**: USB vendor ID of the HID Device.
- **product_id (int)**: USB product ID of the HID Device.
- **interface (int)**: USB interface to be used, defaults to 0.
- **method (int)**: Sets up one or more access methods for the USB device as defined in the METH class; bitwise OR for different methods is possible.
- **default (bytes)**: Default structure of the read/write buffer, could hold static or initial settings.

#### Example:
```python
example_device = USBSimDevice(0x079D, 0x0201, 0, METH.READ | METH.WRITE)
```

### `set_inputs`

```
def set_inputs(inputs):
```

Sets a list of possible structured inputs for the USB HID device, i.e. buttons or axes.

#### Args:
- **inputs (list)**: List containing IO objects configuring the possible inputs with name, byte, and bit positions. The bit position can be 0-7 (bit inside the byte), 8 (full byte), 16 (integer), or -7 (signed byte).

#### Example:
```python
example_device.set_inputs([IO("Aileron", 0, 8), 
                           IO("Elevator", 1, 8), 
                           IO("Button1", 2, 0),
                           IO("Button2", 2, 1)])
```

### `set_outputs`

```
def set_outputs(outputs):
```

Sets a list of possible structured outputs for the USB HID device, i.e. LEDs and digital objects.

#### Args:
- **outputs (list)**: List containing IO objects configuring the possible outputs with name, byte, and bit positions. The bit position can be 0-7 (bit inside the byte), 8 (full byte), or 16 (integer).

#### Example:
```python
example_device.set_outputs([
    IO("LED1", 0, 0), 
    IO("LED2", 1, 0)])
```

### `set_actions`
```
def set_actions(actions):
```

Sets the actions to be performed based on input changes.

#### Args:
- **actions (callable)**: Functions defining actions to be executed, typically involving changes to the simulation environment or reactions to such changes.

#### Example:
```python
def ActionExampleDevice(self):
    ins = self.input_ios()
    if ins["Button1"] == 0: 
        sc.send_event("AUTOPILOT_ON")
        
example_device.set_actions(ActionExampleDevice)
```

### `set_simvars`

```
def set_simvars(simvars):
```

Adds a list of simulation variables (simvars) to the the class variable `Simvars` droping duplicates. The retreaval of the simvars itself has to be done outside of the USBSimDevice class.

#### Args:
- **simvars (list)**: List of simulation variables to be monitored and updated.

#### Example:
```python
example_device.set_simvars(["Airspeed", "Altitude"])
```

### `blink_on`

```
def blink_on(io, offvalue):
```

Enables blinking on a specific output. Blinking is synchronised between all outputs of the class.

#### Args:
- **io (string)**: Name of output that should blink.
- **offvalue (int)**: Value for the output during the off phase.

#### Example:
```python
example_device.blink_on("LED1", 0)
```

### `blink_off`

```
def blink_off():
```

Disables the blinking on a specific output.

#### Args:
- **io (string)**: Name of output that should stop blinking.

#### Example:
```python
example_device.blink_off()
```

### `blink_apply`

```
def blink_apply(buffer):
```

Applies the blinking pattern to the buffer.

#### Args:
- **buffer (bytes)**: Data buffer to apply the blinking pattern to.

#### Returns:
- **buffer (bytes)**: Data buffer with the blinking pattern applied.

#### Example:
```python
example_device.write(example_device.blink_apply(example_buffer))
```

### `update`

```
def update():
```

Main interaction method with the associated HID device. Calling this method will send prepared outputs via the configured method and also recieve new data from the devices input. Update should be called regularly on all instances of the USBSimDevice class. After the update, the `actions()` method should be called separately to handle the changes.

#### Example:
```python
while True:
    for worker in USBSimDevice.Workers:
        worker.update()
        worker.actions()
```

### `input`

```
def input():
```

Returns the raw input buffer for the instance recieved on the previous update.

#### Returns:
- **bytes**: Input buffer.

#### Example:
```python
buffer = example_device.input()
```

### `input_ios`

```
def input_ios():
```

Returns a dict {IOname:currentvalue} of all configured IOs for which a change has been detected during the previous update. IOs that have not changed at last update will be reported as False.

#### Returns:
- **dict**: Dictionary of input states with names as keys and their respective values.

#### Example:
```python
ins = self.input_ios()
if ins["Button1"] == 0: 
    sc.send_event("AUTOPILOT_ON")
```

### `output`

```
def output(buffer, pos=0):
```

Replaces some or all data in the write buffer and triggers writing during the next update.

#### Args:
- **buffer (bytes)**: Data to write at the next update. This could be a single byte or the complete buffer.
- **pos (int)**: Start position of provided data inside the write buffer.

#### Example:
```python
# Output data to the device
example_device.output(b'\x01\x02', pos=1)
```

### `output_io`

```
def output_io(io, value):
```

Replaces output values in a structured way and triggers writing during the next update.

#### Args:
- **io (str)**: Key to be changed.
- **value (int)**: Value to be changed on the next update.

#### Example:
```
example_device.output_io("LED1", 1)
```
