import logging
import voluptuous as vol
import json
from datetime import timedelta
import time

from homeassistant.components import sensor
from custom_components.smartthinq import (
    DOMAIN, LGE_DEVICES, LGEDevice)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_TOKEN, CONF_ENTITY_ID)
from homeassistant.exceptions import PlatformNotReady


import wideq

REQUIREMENTS = ['wideq']
DEPENDENCIES = ['smartthinq']

LGE_WASHER_DEVICES = 'lge_washer_devices'

# ATTR_CURRENT_STATUS = 'current_status'
ATTR_RUN_STATE = 'run_state'
ATTR_PRE_STATE = 'pre_state'
ATTR_REMAIN_TIME = 'remain_time'
ATTR_INITIAL_TIME = 'initial_time'
ATTR_RESERVE_TIME = 'reserve_time'
ATTR_CURRENT_COURSE = 'current_course'
ATTR_ERROR_STATE = 'error_state'
ATTR_SPIN_OPTION_STATE = 'spin_option_state'
ATTR_WASH_OPTION_STATE = 'wash_option_state'
ATTR_RINSE_OPTION_STATE = 'rinse_option_state'
ATTR_WATERTEMP_OPTION_STATE = 'watertemp_option_state'
ATTR_DRYLEVEL_STATE = 'drylevel_state'
ATTR_CREASECARE_MODE = 'creasecare_mode'
ATTR_CHILDLOCK_MODE = 'childlock_mode'
ATTR_STEAM_MODE = 'steam_mode'
ATTR_STEAM_SOFTENER_MODE = 'steam_softener_mode'
ATTR_DOORLOCK_MODE = 'doorlock_mode'
ATTR_PREWASH_MODE = 'prewash_mode'
ATTR_REMOTESTART_MODE = 'remotestart_mode'
ATTR_TURBOWASH_MODE = 'turbowash_mode'
ATTR_TUBCLEAN_COUNT = 'tubclean_count'

RUNSTATES = {
    'OFF': wideq.STATE_WASHER_POWER_OFF,
    'INITIAL': wideq.STATE_WASHER_INITIAL,
    'PAUSE': wideq.STATE_WASHER_PAUSE,
    'ERROR_AUTO_OFF': wideq.STATE_WASHER_ERROR_AUTO_OFF,
    'RESERVE': wideq.STATE_WASHER_RESERVE,
    'DETECTING': wideq.STATE_WASHER_DETECTING,
    'ADD_DRAIN': wideq.STATE_WASHER_ADD_DRAIN,
    'DETERGENT_AMOUNT': wideq.STATE_WASHER_DETERGENT_AMOUT,
    'RUNNING': wideq.STATE_WASHER_RUNNING,
    'PREWASH': wideq.STATE_WASHER_PREWASH,
    'RINSING': wideq.STATE_WASHER_RINSING,
    'RINSE_HOLD': wideq.STATE_WASHER_RINSE_HOLD,
    'SPINNING': wideq.STATE_WASHER_SPINNING,
    'DRYING': wideq.STATE_WASHER_DRYING,
    'END': wideq.STATE_WASHER_END,
    'REFRESHWITHSTEAM': wideq.STATE_WASHER_REFRESHWITHSTEAM,
    'COOLDOWN': wideq.STATE_WASHER_COOLDOWN,
    'STEAMSOFTENING': wideq.STATE_WASHER_STEAMSOFTENING,
    'ERRORSTATE': wideq.STATE_WASHER_ERRORSTATE,
    'TCL_ALARM_NORMAL': wideq.STATE_WASHER_TCL_ALARM_NORMAL,
    'FROZEN_PREVENT_INITIAL': wideq.STATE_WASHER_FROZEN_PREVENT_INITIAL,
    'FROZEN_PREVENT_RUNNING': wideq.STATE_WASHER_FROZEN_PREVENT_RUNNING,
    'FROZEN_PREVENT_PAUSE': wideq.STATE_WASHER_FROZEN_PREVENT_PAUSE,
    'ERROR': wideq.STATE_WASHER_ERROR,
}

WATERTEMPSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'COLD' : wideq.STATE_WASHER_WATERTEMP_COLD,
    'TWENTY' : wideq.STATE_WASHER_WATERTEMP_20,
    'THIRTY' : wideq.STATE_WASHER_WATERTEMP_30,
    'FOURTY' : wideq.STATE_WASHER_WATERTEMP_40,
    'FIFTY' : wideq.STATE_WASHER_WATERTEMP_50,
    'SIXTY': wideq.STATE_WASHER_WATERTEMP_60,
    'NINTYFIVE': wideq.STATE_WASHER_WATERTEMP_95,
    'OFF': wideq.STATE_WASHER_POWER_OFF,

}

SOILLEVELSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'LIGHT': wideq.STATE_WASHER_SOILLEVEL_LIGHT,
    'NORMAL': wideq.STATE_WASHER_SOILLEVEL_NORMAL,
    'HEAVY': wideq.STATE_WASHER_SOILLEVEL_HEAVY,
    'PRE_WASH': wideq.STATE_WASHER_SOILLEVEL_PRE_WASH,
    'SOAKING': wideq.STATE_WASHER_SOILLEVEL_SOAKING,
    'OFF': wideq.STATE_WASHER_POWER_OFF,

}

WASHOPTIONSTATES = {
    'NORMAL' : wideq.STATE_WASHER_WASHOPTION_NORMAL,
    'TURBO WASH' : wideq.STATE_WASHER_WASHOPTION_TURBO_WASH,
    'INTENSIVE' : wideq.STATE_WASHER_WASHOPTION_INTENSIVE,
    'TIMESAVE' : wideq.STATE_WASHER_WASHOPTION_TIMESAVE,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

SPINSPEEDSTATES = {
    'NOSPIN': wideq.STATE_WASHER_SPINSPEED_NOSPIN,
    'MAX': wideq.STATE_WASHER_SPINSPEED_MAX,
    'SPIN_400' : wideq.STATE_WASHER_SPINSPEED_400,
    'SPIN_600' : wideq.STATE_WASHER_SPINSPEED_600,
    'SPIN_700' : wideq.STATE_WASHER_SPINSPEED_700,
    'SPIN_800': wideq.STATE_WASHER_SPINSPEED_800,
    'SPIN_900': wideq.STATE_WASHER_SPINSPEED_900,
    'SPIN_1000' : wideq.STATE_WASHER_SPINSPEED_1000,
    'SPIN_1100' : wideq.STATE_WASHER_SPINSPEED_1100,
    'SPIN_1200' : wideq.STATE_WASHER_SPINSPEED_1200,
    'SPIN_1400': wideq.STATE_WASHER_SPINSPEED_1400,
    'SPIN_1600': wideq.STATE_WASHER_SPINSPEED_1600, 
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

RINSEOPTIONSTATES = {
    'RINSE++' : wideq.STATE_WASHER_RINSEOPTION_RINSE_PLUS_PLUS,
    'NORMAL' : wideq.STATE_WASHER_RINSEOPTION_NORMAL,
    'NORMALHOLD' : wideq.STATE_WASHER_RINSEOPTION_NORMALHOLD,
    'RINSE+' : wideq.STATE_WASHER_RINSEOPTION_RINSE_PLUS,
    'RINSE+HOLD' : wideq.STATE_WASHER_RINSEOPTION_RINSE_PLUS_HOLD,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

DRYLEVELSTATES = {
    'IRON': wideq.STATE_WASHER_DRYLEVEL_IRON,
    'NORMAL' : wideq.STATE_WASHER_DRYLEVEL_NORMAL,
    'LOW' : wideq.STATE_WASHER_DRYLEVEL_LOW,
    'ENERGY': wideq.STATE_WASHER_DRYLEVEL_ENERGY,
    'ECO': wideq.STATE_WASHER_DRYLEVEL_ECO,
    'SPEED': wideq.STATE_WASHER_DRYLEVEL_SPEED,
    'COOLING' : wideq.STATE_WASHER_DRYLEVEL_COOLING,
    'VERY' : wideq.STATE_WASHER_DRYLEVEL_VERY,  
    'TIME_30' : wideq.STATE_WASHER_DRYLEVEL_TIME_30,
    'TIME_60': wideq.STATE_WASHER_DRYLEVEL_TIME_60,
    'TIME_90': wideq.STATE_WASHER_DRYLEVEL_TIME_90,
    'TIME_120': wideq.STATE_WASHER_DRYLEVEL_TIME_120,
    'TIME_150': wideq.STATE_WASHER_DRYLEVEL_TIME_150,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

ERRORS = {
    'ERROR_dE2' : wideq.STATE_WASHER_ERROR_dE2,
    'ERROR_IE' : wideq.STATE_WASHER_ERROR_IE,
    'ERROR_OE' : wideq.STATE_WASHER_ERROR_OE,
    'ERROR_UE' : wideq.STATE_WASHER_ERROR_UE,
    'ERROR_FE' : wideq.STATE_WASHER_ERROR_FE,
    'ERROR_PE' : wideq.STATE_WASHER_ERROR_PE,
    'ERROR_tE' : wideq.STATE_WASHER_ERROR_tE,
    'ERROR_LE' : wideq.STATE_WASHER_ERROR_LE,
    'ERROR_CE' : wideq.STATE_WASHER_ERROR_CE,
    'ERROR_PF' : wideq.STATE_WASHER_ERROR_PF,
    'ERROR_FF' : wideq.STATE_WASHER_ERROR_FF,
    'ERROR_dCE' : wideq.STATE_WASHER_ERROR_dCE,
    'ERROR_EE' : wideq.STATE_WASHER_ERROR_EE,
    'ERROR_PS' : wideq.STATE_WASHER_ERROR_PS,
    'ERROR_dE1' : wideq.STATE_WASHER_ERROR_dE1,
    'ERROR_LOE' : wideq.STATE_WASHER_ERROR_LOE,        
    'NO_ERROR' : wideq.STATE_NO_ERROR,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

OPTIONITEMMODES = {
    'ON': wideq.STATE_OPTIONITEM_ON,
    'OFF': wideq.STATE_OPTIONITEM_OFF,
}

MAX_RETRIES = 5

LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    import wideq
    refresh_token = hass.data[CONF_TOKEN]
    client = wideq.Client.from_token(refresh_token)

    """Set up the LGE Washer components."""

    LOGGER.debug("Creating new LGE Washer")

    if LGE_WASHER_DEVICES not in hass.data:
        hass.data[LGE_WASHER_DEVICES] = []

    for device_id in (d for d in hass.data[LGE_DEVICES]):
        device = client.get_device(device_id)

        if device.type == wideq.DeviceType.WASHER:
            try:
                washer_entity = LGEWASHERDEVICE(client, device)
            except wideq.NotConnectError:
                LOGGER.info('Connection Lost. Retrying.')
                raise PlatformNotReady
            hass.data[LGE_WASHER_DEVICES].append(washer_entity)
    add_entities(hass.data[LGE_WASHER_DEVICES])

    LOGGER.debug("LGE Washer is added")
    
class LGEWASHERDEVICE(LGEDevice):
    def __init__(self, client, device):
        
        """initialize a LGE Washer Device."""
        LGEDevice.__init__(self, client, device)

        import wideq
        self._washer = wideq.WasherDevice(client, device)

        self._washer.monitor_start()
        self._washer.monitor_start()
        self._washer.delete_permission()
        self._washer.delete_permission()

        # The response from the monitoring query.
        self._state = None

        self.update()

    @property
    def supported_features(self):
        """ none """

    @property
    def state_attributes(self):
        """Return the optional state attributes."""
        data={}
        data[ATTR_RUN_STATE] = self.current_run_state
        data[ATTR_PRE_STATE] = self.pre_state
        data[ATTR_REMAIN_TIME] = self.remain_time
        data[ATTR_INITIAL_TIME] = self.initial_time
        data[ATTR_RESERVE_TIME] = self.reserve_time
        data[ATTR_CURRENT_COURSE] = self.current_course
        data[ATTR_ERROR_STATE] = self.error_state
        data[ATTR_WASH_OPTION_STATE] = self.wash_option_state
        data[ATTR_SPIN_OPTION_STATE] = self.spin_option_state
        data[ATTR_RINSE_OPTION_STATE] = self.rinse_option_state
        data[ATTR_WATERTEMP_OPTION_STATE] = self.watertemp_option_state
        data[ATTR_DRYLEVEL_STATE] = self.drylevel_state
        data[ATTR_CREASECARE_MODE] = self.creasecare_mode
        data[ATTR_CHILDLOCK_MODE] = self.childlock_mode
        data[ATTR_STEAM_MODE] = self.steam_mode
        data[ATTR_STEAM_SOFTENER_MODE] = self.steam_softener_mode
        data[ATTR_DOORLOCK_MODE] = self.doorlock_mode
        data[ATTR_PREWASH_MODE] = self.prewash_mode
        data[ATTR_REMOTESTART_MODE] = self.remotestart_mode
        data[ATTR_TURBOWASH_MODE] = self.turbowash_mode
        data[ATTR_TUBCLEAN_COUNT] = self.tubclean_count
        return data

    @property
    def is_on(self):
        if self._state:
            return self._state.is_on
            
    @property
    def state(self):
        """Return the state of the sensor."""
        if self._state:
            run = self._state.run_state
            return RUNSTATES[run.name]

    @property
    def current_run_state(self):
        if self._state:
            run = self._state.run_state
            return RUNSTATES[run.name]

    @property
    def run_list(self):
        return list(RUNSTATES.values())

    @property
    def pre_state(self):
        if self._state:
            pre = self._state.pre_state
            return RUNSTATES[pre.name]

    @property
    def remain_time(self):    
        if self._state:
            remain_hour = self._state.remaintime_hour
            remain_min = self._state.remaintime_min
            remaintime = [remain_hour, remain_min]
            if int(remain_min) < 10:
                return ":0".join(remaintime)
            else:
                return ":".join(remaintime)
            
    @property
    def initial_time(self):
        if self._state:
            initial_hour = self._state.initialtime_hour
            initial_min = self._state.initialtime_min
            initialtime = [initial_hour, initial_min]
            if int(initial_min) < 10:
                return ":0".join(initialtime)
            else:
                return ":".join(initialtime)

    @property
    def reserve_time(self):
        if self._state:
            reserve_hour = self._state.reservetime_hour
            reserve_min = self._state.reservetime_min
            reservetime = [reserve_hour, reserve_min]
            if int(reserve_min) < 10:
                return ":0".join(reservetime)
            else:
                return ":".join(reservetime)

    @property
    def current_course(self):
        if self._state:
            course = self._state.current_course
            smartcourse = self._state.current_smartcourse
            if course == '다운로드코스':
                return smartcourse
            elif course == 'OFF':
                return 'Off'
            else:
                return course

    @property
    def error_state(self):
        if self._state:
            error = self._state.error_state
            return ERRORS[error]
                
    @property
    def rinse_option_state(self):
        if self._state:
            rinse_option = self._state.rinse_option_state
            if rinse_option == 'OFF':
                return RINSEOPTIONSTATES['OFF']
            else:
                return RINSEOPTIONSTATES[rinse_option.name]

    @property
    def wash_option_state(self):
        if self._state:
            wash_option = self._state.wash_option_state
            if wash_option == 'OFF':
                return WASHOPTIONSTATES['OFF']
            else:
                return WASHOPTIONSTATES[wash_option.name]                
    
    @property
    def spin_option_state(self):
        if self._state:
            spin_option = self._state.spin_option_state
            if spin_option == 'OFF':
                return SPINSPEEDSTATES['OFF']
            else:
                return SPINSPEEDSTATES[spin_option.name]

    @property
    def watertemp_option_state(self):
        if self._state:
            watertemp_option = self._state.water_temp_option_state
            if watertemp_option == 'OFF':
                return WATERTEMPSTATES['OFF']
            else:
                return WATERTEMPSTATES[watertemp_option.name]   

    @property
    def drylevel_state(self):
        if self._state:
            drylevel = self._state.drylevel_option_state
            if drylevel == 'OFF':
                return DRYLEVELSTATES['OFF']
            else:
                return DRYLEVELSTATES[drylevel.name]    
    @property
    def creasecare_mode(self):
        if self._state:
            mode = self._state.creasecare_state
            return OPTIONITEMMODES[mode]

    @property
    def childlock_mode(self):
        if self._state:
            mode = self._state.childlock_state
            return OPTIONITEMMODES[mode]

    @property
    def steam_mode(self):
        if self._state:
            mode = self._state.steam_state
            return OPTIONITEMMODES[mode]

    @property
    def steam_softener_mode(self):
        if self._state:
            mode = self._state.steam_softener_state
            return OPTIONITEMMODES[mode]

    @property
    def prewash_mode(self):
        if self._state:
            mode = self._state.prewash_state
            return OPTIONITEMMODES[mode]

    @property
    def doorlock_mode(self):
        if self._state:
            mode = self._state.doorlock_state
            return OPTIONITEMMODES[mode]

    @property
    def remotestart_mode(self):
        if self._state:
            mode = self._state.remotestart_state
            return OPTIONITEMMODES[mode]

    @property
    def turbowash_mode(self):
        if self._state:
            mode = self._state.turbowash_state
            return OPTIONITEMMODES[mode]

    @property
    def tubclean_count(self):
        if self._state:
            return self._state.tubclean_count

    def update(self):

        import wideq

        LOGGER.info('Updating %s.', self.name)
        for iteration in range(MAX_RETRIES):
            LOGGER.info('Polling...')

            try:
                state = self._washer.poll()
            except wideq.NotLoggedInError:
                LOGGER.info('Session expired. Refreshing.')
                self._client.refresh()
                self._washer.monitor_start()
                self._washer.monitor_start()
                self._washer.delete_permission()
                self._washer.delete_permission()

                continue

            except wideq.NotConnectError:
                LOGGER.info('Connection Lost. Retrying.')
                self._client.refresh()
                time.sleep(60)
                continue

            if state:
                LOGGER.info('Status updated.')
                self._state = state
                self._client.refresh()
                self._washer.monitor_start()
                self._washer.monitor_start()
                self._washer.delete_permission()
                self._washer.delete_permission()
                return

            LOGGER.info('No status available yet.')
            time.sleep(2 ** iteration)

        # We tried several times but got no result. This might happen
        # when the monitoring request gets into a bad state, so we
        # restart the task.
        LOGGER.warn('Status update failed.')

        self._washer.monitor_start()
        self._washer.monitor_start()
        self._washer.delete_permission()
        self._washer.delete_permission()
