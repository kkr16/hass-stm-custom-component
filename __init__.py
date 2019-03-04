"""Platform for the City of Montreal's Planif-Neige snow removal APIs."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

DOMAIN = 'stm'
DATA_STM = 'data_stm'

DATA_UPDATED = '{}_data_updated'.format(DOMAIN)

STM_ATTRIBUTION = "Information provided by the STM."

REQUIREMENTS = ['stm-metro-client==0.0.5']

_LOGGER = logging.getLogger(__name__)

DEFAULT_INTERVAL = timedelta(minutes=1)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL,
                     default=DEFAULT_INTERVAL): vol.All(
                         cv.time_period, cv.positive_timedelta)
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Set up the PlanifNeige component."""
    from stm_metro_client import stm_metro_client

    conf = config[DOMAIN]

    stm = stm_metro_client.StmMetroClient()

    data = hass.data[DATA_STM] = StmMetroData(hass, stm)

    async_track_time_interval(
        hass, data.update, conf[CONF_SCAN_INTERVAL]
        )

    def update(call=None):
        """Service call to manually update the data."""
        data.update()

    hass.services.async_register(DOMAIN, 'update', update)

    hass.async_create_task(
        async_load_platform(
            hass,
            SENSOR_DOMAIN,
            DOMAIN,
            data,
            config
        )
    )
    return True


class StmMetroData:
    """Get the latest data from PlanifNeige."""

    def __init__(self, hass, stm):
        """Initialize the data object."""
        self.data = []
        self._hass = hass
        self._stm = stm
        self._lines = self._stm.get_lines()
        self.update()

    def update(self, now=None):
        """Get the latest data from PlanifNeige."""
        self.data = self._stm.get_state()

        dispatcher_send(self._hass, DATA_UPDATED)
