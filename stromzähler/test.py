from unittest import TestCase 
from unittest.mock import patch, Mock
import GlobalStorage
import SmartMeter

class STROM(TestCase):

    meters = [SmartMeter.Meter(), SmartMeter.Meter(), SmartMeter.Meter()]

    def test_smart_meter_creater(self):
        assert self.meters


    def test_add_meter(self):
        assert GlobalStorage.add_meter(self.meters[0]) != False


    def test_remove_meter(self):
        assert GlobalStorage.remove_meter(self.meters[0].uuid) != False


    def test_list_meters(self):
        print(self.meters[0].uuid)
        assert GlobalStorage.list_meters()


    def test_get_meter(self):
        assert GlobalStorage.get_meter('123') != False


    def test_export_meters(self):
        assert GlobalStorage.export_meters()


    def test_import_meters(self):
        assert GlobalStorage.import_meters(GlobalStorage.export_meters()) != False

    def test_meter_kill(self):
        assert self.meters[0].cut_off_power

    def test_to_from_meter(self):
        assert self.meters[0].from_dict(self.meters[0].to_dict())

    def test_factory_reset(self):
        assert self.meters[0].factory_reset != False
    
    def test_init(self):
        assert SmartMeter.Meter.__init__(SmartMeter.Meter()) != False

    def test_restart(self):
        assert self.meters[0].restart != False