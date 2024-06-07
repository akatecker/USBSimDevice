""" =============================================================================================
USBSimDevice Class
=================================================================================================
v0.1 / 18.05.2024 (cc) AkaTecker
v0.2 / Corrected set-reset bit for output
v0.3 / Input signed values using bit=-7
v0.4 / 30.05.2024 Added docstrings for all methods
v0.5 / 01.06.2024 Added blinking
v1.0 / 02.06.2024 Refactor

Simple python interaction layer for using non-ordinary USB Hid devices with Simconnect (i.e.MSFS)
=============================================================================================="""

from time import time
import hid
from collections import namedtuple
from typing import List

# Constants define the method of interaction with USB device

class METH:
    READ = 1
    READ_FEATURE = 2
    READ_LAST = 4
    WRITE = 8
    WRITE_FEATURE = 16

# Class for definition of Buttons and LEDs
# Byte valued Buttons or LEDs have bit set to 8
IO = namedtuple("IO", "name byte bit")

def setbit(b, bit_nr, nb):
    mask = 1 << bit_nr
    if nb == 1:
        return b | mask
    else:
        return b & ~mask

# ====== Main USBSimConnect Class handles interaction with devices ======

class USBSimDevice:
    """The USBSimDevice class capsulates the interaction with USB HID devices to be used by MSFS 2020
    
    The class keeps track of all active instances via the Workers class variable. Although USBSimDevices does not directly interact with SimConnect,
    instances can be configured with actions to do so, and the class variable Simvars can then be used to keep track of all necessary simvars.
    """
    # Keep Track of all instances
    Workers: List = [] # Type: : 
    # All necessery SimVars
    Simvars: List = []
    # Internal Constants
    STAT_NOK = 0
    STAT_OK  = 1
    # Time base for common blinking frequency of all devices
    BLINKTIME = 0.7
    blink_start = time()
    blink_phase = False
    

    def __init__(self,vendor_id, product_id, interface = 0, method = METH.READ, default=b'\0'*64):
        """
        Initializes the class instance with parameters specific to a certain HID device. Also a reference to
        the instance is placed into the Workers list of the class.
        
        Args:
            vendor_id (int): USB vendor ID of the HID Device
            product_id (int): USB product ID of the HID Device
            interface (int): USB interface to be used, defaults to 0
            method (int): sets up one or more access methods for the USB device, bitwise and for different mehtods is possible.
            default (bytes): default structure of the read/write buffer, could hold static or initial settings.
           
        Setting inputs and outputs is a shortcut to set_inputs and set_outputs methods.

        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface = interface
        self.dev = hid.device()
        self.status = USBSimDevice.STAT_NOK
        self.readbuffer = default
        self.old_readbuffer = default
        self.method = method
        self.writebuffer = bytearray(default)
        self.writeUpdate = False
        self.inputs = []
        self.outputs = []
        self.blinkers = dict()
        self.blink_start = USBSimDevice.blink_start
        USBSimDevice.Workers.append(self)
        self.update()

    def set_inputs(self, inputs):
        """Sets a list of possible Inputs for the USB HID device.
        
        Args:
            inputs (list): list containing IO objects configuring the possible inputs with name, byte and bitpositions.
                The bitposition can be 0-7 (bit inside the byte), 8 (full byte), 16 (integer) or -7 (signed byte)
        Example:
            my_usb_device.set_inputs([IO("Button1", 3, 0)] # Button1 references the first bit on the fourth byte of a HID input
        """
        self.inputs = inputs.copy()
        
    def set_outputs(self, outputs):
        """Sets a list of f possible Outputs for the USB HID device.
        
        Args:
            outputs (list): list containing IO objects configuring the possible outputs with name, byte and bitpositions.
                The bitposition can be 0-7 (bit inside the byte) or 8 (full byte)
        Example:
            my_usb_device.set_outputs([IO("Led1", 3, 0)] # Led1 references the first bit on the fourth byte of a HID output
        """
        self.outputs = outputs.copy()
        
    def set_actions(self, actions):
        """Sets a reference to a function that is performed when the instance method action is called. This function is defining the main
        interactions between HID inputs, Simvars, Simevents and HID outputs.
        
        Args:
            actions (callable): reference to a function.
        """
        if callable(actions):
            setattr(self, 'actions', actions.__get__(self, USBSimDevice))
            
    def set_simvars(self,simvars):
        """While USBSimDevice does not directly interact with SimConnect, the class variable Simvars can be set with this mehtod
        to keep track of all Simvars used by different instances in order not to load them multiple times.
        
        Args:
            simvars (list): list of simvars used by the instance to be added to the class variable Simvars
        """
        USBSimDevice.Simvars = list(set(USBSimDevice.Simvars + simvars))
        
        
    def blink_on(self, io, offvalue = 0):
        """Switch on blinking on specific IO
        
        Args:
            io (string): which IO to switch
            offvalue (int): value of output when swiched off
        """
        self.blinkers[io]=offvalue

    def blink_off(self, io):
        """Switch off blinking on specific IO
        
        Args:
            io (string): which IO to switch
        """
        self.blinkers.pop(io, False)

    def blink_apply(self, original_buffer):
        """Returns writebuffer modified by blinking

        Args:
            original_buffer (bytes): original write buffer unaffected by blinking
        """
        if bool(self.blinkers) == False:
            return original_buffer
        elif USBSimDevice.blink_phase == False:
            return original_buffer
        else:
            # modify all bytes / bits affected by blinking
            new_buffer = original_buffer.copy()
            for i in self.blinkers:
                io = next(item for item in self.outputs if item.name == i)
                if io.bit == 8:
                    new_buffer[io.byte] = self.blinkers[i]
                else:
                    new_buffer[io.byte] = setbit(new_buffer[io.byte], io.bit, self.blinkers[i])
            return new_buffer

    def update(self):
        """Main interaction method with the associated HID device. Calling this method will send prepared outputs via the
        configured method and also recieve new data from the devices input. Update should be called regularly on all instances of
        the USBSimDevice class.
        """
        # prepare blinking, synch with class timer.
        if time() - USBSimDevice.blink_start > USBSimDevice.BLINKTIME:
            USBSimDevice.blink_start = time()
            USBSimDevice.blink_phase = USBSimDevice.blink_phase ^ True
        if self.blink_start != USBSimDevice.blink_start:
            self.blink_start = USBSimDevice.blink_start
            self.writeUpdate = True
        # main update
        if self.status == USBSimDevice.STAT_NOK:
            # Try to connect / reconnect when offline
            try:
                self.dev.open_path([d for d in hid.enumerate(self.vendor_id,self.product_id) if d["interface_number"]==self.interface][0]["path"])
                self.dev.set_nonblocking(True)
                self.status = USBSimDevice.STAT_OK
            except:
                self.status = USBSimDevice.STAT_NOK
        else:
            # Do all read / write tasks
            self.old_readbuffer = self.readbuffer
            try:
                if self.method & METH.READ:
                    # read once using read method
                    red = self.dev.read(64)
                    if len(red)>0:
                        self.readbuffer = red
                if self.method & METH.READ_LAST:
                    # read until queue is empty, return last
                    while True:
                        red1=self.dev.read(64)
                        if not red1:
                            break
                        red = red1
                    if len(red)>0:
                        self.readbuffer = red
                if self.method & METH.READ_FEATURE:
                    # read once using feature report method
                    red = self.dev.get_feature_report(0,64)
                    if len(red)>0:
                        self.readbuffer = red
                if self.method & METH.WRITE and self.writeUpdate:
                    # write using write method
                    self.dev.write(self.blink_apply(self.writebuffer))
                    self.writeUpdate = False
                if self.method & METH.WRITE_FEATURE and self.writeUpdate:
                    # write using feature report method
                    self.dev.send_feature_report(self.blink_apply(self.writebuffer))
                    self.writeUpdate = False
            except:
                # If there is an error, reset connection and reconnect at next update()
                self.dev.close()
                self.status = USBSimDevice.STAT_NOK

    def input(self):
        """Returns the raw input buffer for the instance recieved on the previous update.
        """
        # Returns raw readbuffer and diff to old readbuffer as trigger
        return self.readbuffer, bytes(a ^ b for a, b in zip(self.readbuffer, self.old_readbuffer))
    
    def input_ios(self):
        """Returns a dict {IOname:currentvalue} of all configured IOs for which a change has been detected during the previous update. IOs that
        have not changed at last update will be reported as False.
        """
        # returns a dict of all triggered buttons 
        buff, trigger = self.input()
        triggered = {}
        for io in self.inputs:
            if io.bit == -7:
                if trigger[io.byte]!=0:
                    if buff[io.byte] & (1<<7):
                        triggered.update({io.name:(buff[io.byte]&127)-128})    
                    else:
                        triggered.update({io.name:buff[io.byte]})
                else:
                    triggered.update({io.name:False})           
            elif io.bit < 8:
                if trigger[io.byte] & (1<<io.bit):
                    triggered.update({io.name:(buff[io.byte] & (1<<io.bit))>>io.bit})
                else:
                    triggered.update({io.name:False})
            elif io.bit == 8:
                if trigger[io.byte]!=0:
                    triggered.update({io.name:buff[io.byte]})
                else:
                    triggered.update({io.name:False})
            elif io.bit == 16:
                if trigger[io.byte]!=0 or trigger[io.byte+1]!=0:
                    triggered.update({io.name:int.from_bytes(buff[io.byte:io.byte+2], byteorder='big', signed=False)})
                else:
                    triggered.update({io.name:False})
        return triggered

    def output(self, buffer, pos=0):
        """Replaces some or all data in the write buffer and triggers writing during next update.

        Args:
            buffer (bytes): data to write at next update. This could be a single byte or the complete buffer.
            pos (int): start position of provided data inside the write buffer 
        """
        # prepare simple unformated output, inserted after pos
        self.writebuffer[pos:len(buffer)] = buffer
        self.writeUpdate = True

    def output_io(self, io, value):
        """Replaces output values in a structured way and triggers writing during next update.

        Args:
            io (string): key to be changed
            value (int): values to be changed on next update 
        """
        io = next(item for item in self.outputs if item.name == io)
        if io.bit == 8:
            self.writebuffer[io.byte] = value
        else:
            self.writebuffer[io.byte] = setbit(self.writebuffer[io.byte], io.bit, value)
        self.writeUpdate = True