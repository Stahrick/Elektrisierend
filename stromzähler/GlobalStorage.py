import json

meter_dict = {}


def add_meter(meter):
    meter_dict[str(meter.uuid)] = meter


def remove_meter(uuid):
    meter_dict.pop(uuid)


def list_meters():
    global meter_dict
    return list(meter_dict.keys())


def get_meter(uuid):
    return meter_dict[uuid] if uuid in meter_dict else None


def export_meters():
    global meter_dict
    return {uuid: meter.to_dict() for uuid, meter in meter_dict.items()}


def import_meters(import_data: dict):
    global meter_dict
    meter_dict = import_data
