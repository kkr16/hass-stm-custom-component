"""Sensor for the City of Montreal's Planif-Neige snow removal APIs."""

from datetime import datetime
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.restore_state import RestoreEntity

DEPENDENCIES = ['stm']

_LOGGER = logging.getLogger(__name__)

ATTR_UPDATED = 'updated'
DATA_STM = 'data_stm'


STM_ATTRIBUTION = "Information provided by the STM."

LINE_COLOR = {
    1: 'Green',
    2: 'Orange',
    4: 'Yellow',
    5: 'Blue'
}


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the PlanifNeige platform."""
    data = hass.data[DATA_STM]
    async_add_entities(
        [StmSensor(data, sensor) for sensor in data.data]
    )


class StmSensor(RestoreEntity):
    """PlanifNeige sensor."""

    def __init__(self, data, sensor):
        """Initialize the sensor."""
        self._data = sensor
        self._line = sensor['NoLigne']
        self._state = self.state
        self._description = self.description
        self._name = 'STM ' + LINE_COLOR[int(self._line)] + ' Line'
        self._date_updated = self.date_updated
        self._icon = 'mdi:train'

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def date_updated(self):
        """Return the date updated of the sensor."""
        self._date_updated = datetime.now().replace(microsecond=0).isoformat()
        return self._date_updated

    @property
    def description(self):
        """Return the descriptions of the sensor."""
        self._description = self._data['msgAnglais']
        return self._description

    @property
    def state(self):
        """Return the state of the sensor."""
        if 'Normal métro service.' in self._data['msgAnglais']:
            return 'Normal'
        return 'Stopped'

    def update(self):
        """Update device state."""
        self._state = self.state
        self._description = self.description
        self._date_updated = self.date_updated

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            'description': self._description,
            ATTR_ATTRIBUTION: STM_ATTRIBUTION
        }

    @property
    def icon(self):
        """Return the icon."""
        return self._icon
