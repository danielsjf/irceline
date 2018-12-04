# Irceline platform for Home assistant
[Home Assistant](https://www.home-assistant.io/) platform for the [Irceline](http://www.irceline.be/) air quality network.

This platform extends the sensor component. To enable this platform, create a new file with the contents of `irceline.py` in `<config>/custom_components/sensor/irceline.py`.

Next, add the following lines to your `configuration.yaml`:

```yaml
sensor:
  - platform: irceline
    name: (optional) Name of the station
    latitude: (optional) Latitude of your location (will find the closest station)
    longitude: (optional) Longitude of your location (will find the closest station)
    monitored_conditions:
      - temperature
      - co2
      - pm01_0
      - pm02_5
      - pm10_0
    refresh_rate: 15 # minutes between polling; default is 15
```

The custom component uses the [airqdata package](https://pypi.org/project/airqdata/) that can be found on pypi.
