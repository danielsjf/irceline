"""
Support for the Irceline Air Quality Monitors.
For more details about this platform, please refer to the documentation
"""
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ATTRIBUTION, ATTR_TIME, ATTR_TEMPERATURE, CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

CONF_REFRESH = "refresh_rate"

REQUIREMENTS = ['airqdata==0.2']

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Data provided Irceline'

# Sensor types are defined like: Name, units
SENSOR_TYPES = {
    'temperature': ['Temperature', '°C'],
    'co2': ['Carbon Dioxide (CO2)', 'ppm'],
    'pm01_0': ['Particulate matter < 1.0', 'µg/m³'],
    'pm02_5': ['Particulate matter < 2.5', 'µg/m³'],
    'pm10_0': ['Particulate matter < 10', 'µg/m³'],
}

# Sensor types are defined like: Name, Name_API
SENSOR_TYPES_NAMES = {
    'temperature': 'temperature',
    'co2': 'Carbon Dioxide',
    'pm01_0': 'Particulate Matter < 1 µm',
    'pm02_5': 'Particulate Matter < 2.5 µm',
    'pm10_0': 'Particulate Matter < 10 µm',
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default = None): cv.string,
    vol.Optional(CONF_LATITUDE, default = 50): cv.latitude,
    vol.Optional(CONF_LONGITUDE, default = 5): cv.longitude,
    vol.Optional(CONF_MONITORED_CONDITIONS, default = list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_REFRESH, default = 60): cv.positive_int,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Irceline sensor."""
    from airqdata.irceline import Metadata
    import airqdata

    _LOGGER.debug("Setting up the Irceline platform")

    name = config.get(CONF_NAME)
    refresh_rate = config.get(CONF_REFRESH)
    irceline_data = Metadata()
    stations = irceline_data.stations
    lat = 50
    lon = 5
    station_id = None

    # find station ID
    if name is not None:
        station = stations[stations['label'].str.contains(name)]
        name = station['label'].values[0]
        station_id = station.index.values[0]
        lat = station['lat'].values[0]
        lon = station['lon'].values[0]
    else:
        station_id = None
        lat = config.get(CONF_LATITUDE)
        lon = config.get(CONF_LONGITUDE)

    _LOGGER.debug("Setting station is %s", name)

    devs = []

    for indicator in config[CONF_MONITORED_CONDITIONS]:
        time_series_list = irceline_data.query_time_series(SENSOR_TYPES_NAMES[indicator], lat, lon)
        time_series_id = time_series_list.index[0]
        irceline_sensor = airqdata.irceline.Sensor(time_series_id)

        devs.append(IrcelineSensor(irceline_sensor, name, indicator, refresh_rate))

        _LOGGER.debug("Setting up %s", name)


    add_devices(devs)


class IrcelineSensor(Entity):
    """Implementation of an Irceline sensor."""

    _friendly_name: str

    def __init__(self, irceline_sensor: object, device_name: str, indicator: str, refresh_rate = 15):
        """Initialize the sensor."""
        import airqdata
        import time
        import datetime

        self._irceline_sensor = irceline_sensor
        self._indicator = indicator
        self._indicator_name = SENSOR_TYPES[indicator][0]
        self._unit = SENSOR_TYPES[indicator][1]
        self._device_name = device_name
        self._friendly_name = '{} - {}'.format(self._device_name,self._indicator_name)
        self._refresh_rate = refresh_rate
        self._last_update = datetime.datetime.now()

        today = time.strftime("%Y-%m-%d")
        self._data = self._irceline_sensor.get_last_measurement()

        _LOGGER.debug("Initialise %s", self._friendly_name)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._indicator == 'temperature':
            return 'mdi:thermometer'
        if self._indicator == 'co2':
            return 'mdi:periodic-table-co2'
        if self._indicator == 'pm01_0':
            return 'mdi:factory'
        if self._indicator == 'pm02_5':
            return 'mdi:factory'
        if self._indicator == 'pm10_0':
            return 'mdi:factory'

    @property
    def device_class(self):
        """Return the device class."""
        """Icon to use in the frontend, if any."""
        if self._indicator == 'temperature':
            return 'temperature'
        if self._indicator == 'co2':
            return 'carbon_dioxide'
        if self._indicator == 'pm01_0':
            return 'particulate_matter_1.0'
        if self._indicator == 'pm02_5':
            return 'particulate_matter_2.5'
        if self._indicator == 'pm10_0':
            return 'particulate_matter_10'

    @property
    def state(self):
        import datetime
        """Return the state of the device."""
        _LOGGER.debug("Get state for %s", self._friendly_name)
        if self._last_update + datetime.timedelta(minutes=self._refresh_rate) < datetime.datetime.now():
            self.update()

        return self._data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    def update(self):
        """Get the latest data and updates the states."""
        _LOGGER.debug("Update data for %s", self._friendly_name)

        self._data = self._irceline_sensor.get_last_measurement()