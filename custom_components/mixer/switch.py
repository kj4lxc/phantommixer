from homeassistant.components.switch import SwitchEntity
from datetime import timedelta
import logging
import xair_api

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
  """Set up the switch platform."""
  # Retrieve the IP address from configuration.yaml
  host = config.get("host")
  scan_interval = timedelta(seconds=10)
  # Check if the host is provided
  if not host:
    _LOGGER.error("No host specified in configuration.yaml")
    return

  # Add your switches here
  switches = []
  for index in range(1, 5):  # Assuming 4 switches
    switches.append(CustomSwitchEntity(host, index, scan_interval))
  async_add_entities(switches)

class CustomSwitchEntity(SwitchEntity):
  """Representation of a custom switch."""

  def __init__(self, host, index, scan_interval):
    """Initialize the switch."""
    self._host = host  # Save the host for later use
    self._index = "0"+str(index)
    self._name = f"Phantom Power {index}"
    self._is_on = False
    self._available = True
    self._scan_interval = scan_interval

  @property
  def name(self):
    """Return the name of the switch."""
    return self._name

  @property
  def is_on(self):
    """Return the state of the switch."""
    return self._is_on
  
  @property
  def available(self):
    """Return if the switch is available."""
    return self._available

  def turn_on(self, **kwargs):
    """Turn the switch on."""
    try:
      with xair_api.connect("XR12", ip=self._host, connect_timeout=2) as mixer:
        mixer.send(f"/headamp/{self._index}/phantom", 1)
      self._is_on = True
      self.schedule_update_ha_state()
    except Exception as e:
      _LOGGER.error("Failed turn on for switch %s: %s", self._index, str(e))
      self._available = False
    finally:
      self.schedule_update_ha_state()

  def turn_off(self, **kwargs):
    """Turn the switch off."""
    try:
      with xair_api.connect("XR12", ip=self._host, connect_timeout=2) as mixer:
        mixer.send(f"/headamp/{self._index}/phantom", 0)
      self._is_on = False
      self.schedule_update_ha_state()
    except Exception as e:
      _LOGGER.error("Failed turn off for switch %s: %s", self._index, str(e))
      self._available = False
    finally:
      self.schedule_update_ha_state()
        
  def update(self):
    """Fetch the latest state."""
    try:
      with xair_api.connect("XR12", ip=self._host, connect_timeout=2) as mixer:
        state = mixer.query(f"/headamp/{self._index}/phantom")
        self._is_on = state[0] == 1
        self._available = True  # Switch is available if we got a valid response
    except Exception as e:
      # _LOGGER.error("Failed to update state for switch %s: %s", self._index, str(e))
      self._available = False  # Mark the switch as unavailable if there's an error
    finally:
      self.schedule_update_ha_state()
