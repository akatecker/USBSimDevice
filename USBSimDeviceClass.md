
# **USBSimDevice**

The `USBSimDevice` class encapsulates the interaction with USB HID devices to be used by MSFS 2020. The class keeps track of all active instances via the `Workers` class variable. Although `USBSimDevices` does not directly interact with SimConnect, instances can be configured with actions to do so, and the class variable `Simvars` can then be used to keep track of all necessary simvars.

## Methods

### `__init__`

```python
def __init__(vendor_id, product_id, interface=0, method=METH.READ, default=(b'\x00' * 64)):
```

Initializes the class instance with parameters specific to a certain HID device. A reference to the instance is placed into the `Workers` list of the class.

#### Args:
- **vendor_id (int)**: USB vendor ID of the HID Device.
- **product_id (int)**: USB product ID of the HID Device.
- **interface (int)**: USB interface to be used, defaults to 0.
- **method (int)**: Sets up one or more access methods for the USB device; bitwise AND for different methods is possible.
- **default (bytes)**: Default structure of the read/write buffer, could hold static or initial settings.

Setting inputs and outputs is a shortcut to `set_inputs` and `set_outputs` methods.

### `set_inputs`

```python
def set_inputs(inputs):
```

Sets a list of possible inputs for the USB HID device.

#### Args:
- **inputs (list)**: List containing IO objects configuring the possible inputs with name, byte, and bit positions. The bit position can be 0-7 (bit inside the byte), 8 (full byte), 16 (integer), or -7 (signed byte).

#### Example:
```python
my_usb_device.set_inputs([IO("Button1", 3, 0)])  # Button1 references the first byte and 0th bit.
```

### `set_outputs`

```python
def set_outputs(outputs):
```

Sets a list of possible outputs for the USB HID device.

#### Args:
- **outputs (list)**: List containing IO objects configuring the possible outputs with name, byte, and bit positions. The bit position can be 0-7 (bit inside the byte), 8 (full byte), or 16 (integer).

#### Example:
```python
my_usb_device.set_outputs([IO("LED1", 4, 0)])  # LED1 references the fourth byte and 0th bit.
```

### `set_actions`

```python
def set_actions(actions):
```

Sets the actions to be performed based on input changes.

#### Args:
- **actions (list)**: List of actions to be executed, typically involving changes to the simulation environment.

### `set_simvars`

```python
def set_simvars(simvars):
```

Sets the simulation variables (simvars) to be tracked.

#### Args:
- **simvars (list)**: List of simulation variables to be monitored and updated.

### `blink_on`

```python
def blink_on(blink_interval):
```

Enables blinking with a specified interval.

#### Args:
- **blink_interval (float)**: Interval in seconds for the blinking cycle.

### `blink_off`

```python
def blink_off():
```

Disables the blinking feature.

### `blink_apply`

```python
def blink_apply(buffer):
```

Applies the blinking pattern to the buffer.

#### Args:
- **buffer (bytes)**: Data buffer to apply the blinking pattern to.

### `update`

```python
def update():
```

Triggers an update to read inputs and write outputs based on the current state and actions.

### `input`

```python
def input():
```

Reads the current state of inputs from the HID device.

#### Returns:
- **dict**: Dictionary of input states with names as keys and their respective values.

### `input_ios`

```python
def input_ios(trigger):
```

Processes input states based on the provided trigger and updates the state.

#### Args:
- **trigger (bytes)**: Byte array representing the trigger states.

#### Returns:
- **dict**: Dictionary of input states with names as keys and their respective values.

### `output`

```python
def output(buffer, pos=0):
```

Replaces some or all data in the write buffer and triggers writing during the next update.

#### Args:
- **buffer (bytes)**: Data to write at the next update. This could be a single byte or the complete buffer.
- **pos (int)**: Start position of provided data inside the write buffer.

### `output_io`

```python
def output_io(io, value):
```

Replaces output values in a structured way and triggers writing during the next update.

#### Args:
- **io (str)**: Key to be changed.
- **value (int)**: Value to be changed on the next update.
