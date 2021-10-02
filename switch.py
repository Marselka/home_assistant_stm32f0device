"""Support for switch sensor using I2C MCP23017 chip."""
#from adafruit_mcp230xx.mcp23017 import MCP23017
#import board
#import busio
#import digitalio
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import DEVICE_DEFAULT_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity

import serial

CONF_INVERT_LOGIC = "invert_logic"
CONF_I2C_ADDRESS = "i2c_address"
CONF_PINS = "pins"
CONF_PULL_MODE = "pull_mode"
CONF_SERIAL_PORT = "serial_port"

DEFAULT_INVERT_LOGIC = False
DEFAULT_I2C_ADDRESS = 0x20

_SWITCHES_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PINS): _SWITCHES_SCHEMA,
        vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
        vol.Optional(CONF_I2C_ADDRESS, default=DEFAULT_I2C_ADDRESS): vol.Coerce(int),
        vol.Required(CONF_SERIAL_PORT): vol.Coerce(str),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MCP23017 devices."""
    invert_logic = config.get(CONF_INVERT_LOGIC)
    i2c_address = config.get(CONF_I2C_ADDRESS)
    ser = serial.Serial(config.get(CONF_SERIAL_PORT))

    switches = []
    pins = config.get(CONF_PINS)
    for pin_num, pin_name in pins.items():
        switches.append(STM32F0DeviceSwitch(pin_name, pin_num, invert_logic, ser))
    add_entities(switches)


class STM32F0DeviceSwitch(ToggleEntity):
    """Representation of a  MCP23017 output pin."""

    def __init__(self, name, pin_num, invert_logic, ser):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._pin_num = pin_num
        self._invert_logic = invert_logic
        self._state = False

        #self._pin.direction = digitalio.Direction.OUTPUT
        #self._pin.value = self._invert_logic

        self._ser = ser

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def assumed_state(self):
        """Return true if optimistic updates are used."""
        return True

    def turn_on(self, **kwargs):
        """Turn the device on."""
        #self._pin.value = not self._invert_logic
        values = bytearray([self._pin_num | 0b00000000, 90 | 0b10000000])
        self._ser.write(values)
        
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        #self._pin.value = self._invert_logic
        values = bytearray([self._pin_num | 0b00000000, 0 | 0b10000000])
        self._ser.write(values)

        self._state = False
        self.schedule_update_ha_state()

    def set_value(self, **kwargs):
        pass
