"""Custom component for reading values from knx group address"""

import asyncio
import voluptuous as vol
from homeassistant.components.knx import DATA_KNX
import homeassistant.helpers.config_validation as cv

DOMAIN = 'knx_reader'

SERVICE_KNX_READ = "read"
SERVICE_KNX_ATTR_ADDRESS = "address"

DEPENDENCIES = ['knx']

SERVICE_KNX_SEND_SCHEMA = vol.Schema({
    vol.Required(SERVICE_KNX_ATTR_ADDRESS): cv.string,
})

@asyncio.coroutine
def async_setup(hass, config):
    """Ensure KNX is there."""

    if DATA_KNX not in hass.data \
            or not hass.data[DATA_KNX].initialized:
        return False

    @asyncio.coroutine
    def service_read_from_knx_bus(call):
        """Issue read request to the bus."""
        from xknx.core import ValueReader
        from xknx.knx import Address
        attr_address = call.data.get(SERVICE_KNX_ATTR_ADDRESS)
        knx_address = Address(attr_address)

        value_reader = ValueReader(hass.data[DATA_KNX].xknx, knx_address)
        yield from value_reader.send_group_read()

    hass.services.async_register(
        DOMAIN, SERVICE_KNX_READ,
        service_read_from_knx_bus,
        schema=SERVICE_KNX_SEND_SCHEMA)

    return True
