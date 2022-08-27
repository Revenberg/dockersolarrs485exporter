"""Application exporter"""

import rs485eth
import os
import time
from prometheus_client import start_http_server, Gauge, Enum, Info
import logging
import requests

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARN")

PROMETHEUS_PREFIX = os.getenv("PROMETHEUS_PREFIX", "solarrs485exporter")
PROMETHEUS_PORT   = int(os.getenv("PROMETHEUS_PORT", "9003"))

server = os.getenv("RS485_ADDRESS", "localhost")
port = int(os.getenv("RS485_PORT", "8899"))

polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "15"))

LOGFORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(level=LOG_LEVEL, format=LOGFORMAT)
LOG = logging.getLogger("solarrs485exporter-export")

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    _prometheus = {}

    def __init__(self, PROMETHEUS_PREFIX='', server=server, port=port, polling_interval_seconds=5):

        if PROMETHEUS_PREFIX != '':
            PROMETHEUS_PREFIX = PROMETHEUS_PREFIX + "_"

        self.server=server
        self.port=port
            
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self._prometheus['generatedalltime']   = Gauge(PROMETHEUS_PREFIX + 'generatedalltime', 'Generated (All time)  Read All Time Energy (KWH Total) as Unsigned 32-Bit')
        self._prometheus['generatedtoday']     = Gauge(PROMETHEUS_PREFIX + 'generatedtoday', 'Generated (Today)  Read Today Energy (KWH Total) as 16-Bit')
        self._prometheus['generatedyesterday'] = Gauge(PROMETHEUS_PREFIX + 'generatedyesterday', 'Generated (Yesterday) Read Today Energy (KWH Total) as 16-Bit')
        self._prometheus['acwatts']            = Gauge(PROMETHEUS_PREFIX + 'acwatts', 'AC Watts (W) Read AC Watts as Unsigned 32-Bit')
        self._prometheus['dcvoltage1']         = Gauge(PROMETHEUS_PREFIX + 'dcvoltage1', 'DC Voltage 1 (V) Read DC Volts as Unsigned 16-Bit')
        self._prometheus['dccurrent1']         = Gauge(PROMETHEUS_PREFIX + 'dccurrent1', 'DC Current 1 (A) Read DC Current as Unsigned 16-Bit')
        self._prometheus['dcvoltage2']         = Gauge(PROMETHEUS_PREFIX + 'dcvoltage2', 'DC Voltage 2 (V) Read DC Volts as Unsigned 16-Bit')
        self._prometheus['dccurrent2']         = Gauge(PROMETHEUS_PREFIX + 'dccurrent2', 'DC Current 2 (A) Read DC Current as Unsigned 16-Bit')
        self._prometheus['acvoltage1']         = Gauge(PROMETHEUS_PREFIX + 'acvoltage1', 'AC voltage 1 (V) Read AC Volts as Unsigned 16-Bit')
        self._prometheus['acvoltage2']         = Gauge(PROMETHEUS_PREFIX + 'acvoltage2', 'AC voltage 2 (V) Read AC Volts as Unsigned 16-Bit')
        self._prometheus['acvoltage3']         = Gauge(PROMETHEUS_PREFIX + 'acvoltage3', 'AC voltage 3 (V) Read AC Volts as Unsigned 16-Bit')
        self._prometheus['accurent1']          = Gauge(PROMETHEUS_PREFIX + 'accurent1', 'AC Current 1 (A)')
        self._prometheus['accurent2']          = Gauge(PROMETHEUS_PREFIX + 'accurent2', 'AC Current 2 (A)')
        self._prometheus['accurent3']          = Gauge(PROMETHEUS_PREFIX + 'accurent3', 'AC Current 3 (A)')
        self._prometheus['frequency']          = Gauge(PROMETHEUS_PREFIX + 'frequency', 'AC Frequency (Hz) Read AC Frequency as Unsigned 16-Bit')
        self._prometheus['temprature']         = Gauge(PROMETHEUS_PREFIX + 'temprature', 'Inverter Temperature (c) Read Inverter Temperature as Signed 16-bit')
        self._prometheus['timestamp']          = Info(PROMETHEUS_PREFIX + 'timestamp', 'Timestamp')
        self._prometheus['acpower']            = Gauge(PROMETHEUS_PREFIX + 'acpower', 'ac power (A)')
        self._prometheus['pvpower']            = Gauge(PROMETHEUS_PREFIX + 'pvpower', 'pv power (V)')
        self._prometheus['totalenergy']        = Gauge(PROMETHEUS_PREFIX + 'totalenergy', 'Total energy (W)')
        self._prometheus['monthenergy']        = Gauge(PROMETHEUS_PREFIX + 'monthenergy', 'Month energy (W)')
        self._prometheus['lastmonth']          = Gauge(PROMETHEUS_PREFIX + 'lastmonth', 'Last month energy')
        self._prometheus['yearenergy']         = Gauge(PROMETHEUS_PREFIX + 'yearenergy', 'Year energy')
        self._prometheus['lastyear']           = Gauge(PROMETHEUS_PREFIX + 'lastyear', 'Last year energy')
        self._prometheus['error']              = Info(PROMETHEUS_PREFIX + 'error', 'Error')

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def getValueLong(instrument, addr, _functioncode=0, _signed=False):
        rc = instrument.read_long(addr, functioncode=_functioncode, signed=_signed)
        LOG.info( rc )
        return rc

    def getValueRegister(instrument, addr, _numberOfDecimals=0, _functioncode=0, _signed=False):
        rc = instrument.read_register(addr, numberOfDecimals=_numberOfDecimals, functioncode=_functioncode, signed=_signed)
        LOG.info( rc )
        return rc

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        LOG.info(self.server)
        LOG.info(self.port)

        instrument = rs485eth.Instrument(self.server, self.port, 1, debug=True) # port name, slave address

        self._prometheus['generatedalltime'].set(self.getValueLong(instrument,3008, functioncode=4, signed=False))
        self._prometheus['generatedtoday'].set(self.getValueRegister(3014, numberOfDecimals=1, functioncode=4, signed=False)/10)
        self._prometheus['generatedyesterday'].set(self.getValueRegister(3015, numberOfDecimals=1, functioncode=4, signed=False)/10 )
        self._prometheus['acwatts'].set(self.getValueLong(instrument,3004, functioncode=4, signed=False))
        self._prometheus['dcvoltage1'].set(self.getValueRegister(3021, functioncode=4, signed=False) / 10)
        self._prometheus['dccurrent1'].set(self.getValueRegister(3022, functioncode=4, signed=False) / 10)
        self._prometheus['dcvoltage2'].set(self.getValueRegister(3023, functioncode=4, signed=False) / 10)
        self._prometheus['dccurrent2'].set(self.getValueRegister(3024, functioncode=4, signed=False) / 10)
        self._prometheus['acvoltage1'].set(self.getValueRegister(3033, functioncode=4, signed=False) / 10)
        self._prometheus['acvoltage2'].set(self.getValueRegister(3034, functioncode=4, signed=False) / 10)
        self._prometheus['acvoltage3'].set(self.getValueRegister(3035, functioncode=4, signed=False) / 10)
        self._prometheus['accurent1'].set(self.getValueRegister(3036, functioncode=4, signed=False) / 10)
        self._prometheus['accurent2'].set(self.getValueRegister(3037, functioncode=4, signed=False) / 10)
        self._prometheus['accurent3'].set(self.getValueRegister(3038, functioncode=4, signed=False) / 10)
        self._prometheus['frequency'].set( self.getValueRegister(3042, functioncode=4, signed=False) / 100)
        self._prometheus['temprature'].set(self.getValueRegister(3041, functioncode=4, signed=True) / 10)

        Realtime_DATA_yy = self.getValueRegister(3072, functioncode=4, signed=False) #Read Year
        Realtime_DATA_mm = self.getValueRegister(3073, functioncode=4, signed=False) #Read Month
        Realtime_DATA_dd = self.getValueRegister(3074, functioncode=4, signed=False) #Read Day
        Realtime_DATA_hh = self.getValueRegister(3075, functioncode=4, signed=False) #Read Hour
        Realtime_DATA_mi = self.getValueRegister(3076, functioncode=4, signed=False) #Read Minute
        Realtime_DATA_ss = self.getValueRegister(3077, functioncode=4, signed=False) #Read Second
        
        self._prometheus['timestamp'].info( {  'yy': Realtime_DATA_yy, 'mm': Realtime_DATA_mm, 'dd': Realtime_DATA_dd, 'hh': Realtime_DATA_hh, 'mi': Realtime_DATA_mi, 'ss': Realtime_DATA_ss} )
        self._prometheus['acpower'].set(self.getValueRegister(3005, functioncode=4, signed=False))
        self._prometheus['pvpower'].set(self.getValueRegister(3007, functioncode=4, signed=False))
        self._prometheus['totalenergy'].set(self.getValueRegister(3009, functioncode=4, signed=False))
        self._prometheus['monthenergy'].set(self.getValueRegister(3011, functioncode=4, signed=False))
        self._prometheus['lastmonth'].set(self.getValueRegister(3013, functioncode=4, signed=False))
        self._prometheus['yearenergy'].set( self.getValueRegister(3017, functioncode=4, signed=False))
        self._prometheus['lastyear'].set(self.getValueRegister(3019, functioncode=4, signed=False))
        self._prometheus['error'].info({ 'error': self.getValueRegister(3043, functioncode=4, signed=False) })

        LOG.info("Update prometheus")

def main():
    """Main entry point"""

    app_metrics = AppMetrics(
        PROMETHEUS_PREFIX=PROMETHEUS_PREFIX,
        server=server,
        port=port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(PROMETHEUS_PORT)
    LOG.info("start prometheus port: %s", PROMETHEUS_PORT)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()