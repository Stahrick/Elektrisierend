import re

class DataValidator:
    @staticmethod
    def _validate_name(name: str):
        if not isinstance(name, str):
            return False
        if not re.match(r"^[a-zA-Z]{2,}$", name):
            return False
        return True

    @staticmethod
    def is_valid_first_name(first_name: str):
        return DataValidator._validate_name(first_name)

    @staticmethod
    def is_valid_last_name(last_name: str):
        return DataValidator._validate_name(last_name)

    @staticmethod
    def is_valid_email(email: str):
        if not isinstance(email, str):
            return False
        if not re.match(r"^[a-zA-Z0-9]+([._+-][a-zA-Z0-9]+)*@[0-9a-zA-Z]+.[a-zA-Z]{2,4}+([.][a-zA-Z]{2,3})?$", email):
            return False
        return True

    @staticmethod
    def is_valid_state(state: str):
        return DataValidator._validate_name(state)

    @staticmethod
    def valid_city(city: str):
        return DataValidator._validate_name(city)

    @staticmethod
    def valid_zip_code(zip_code: str):
        if not isinstance(zip_code, str):
            return False
        if not re.match(r"^(?!01000|99999)(0[1-9]\d{3}|[1-9]\d{4})$"):
            return False
        return True

    @staticmethod
    def is_valid_address(address: str):
        if not isinstance(address, str):
            return False
        if not re.match(r"^([a-zA-Z]{2,})((-([a-zA-Z]{2,}))|([a-zA-Z]{2,}))*\s*(\.|\s)\s*[0-9]{1,4}[a-z]?$"):
            return False
        return True

    @staticmethod
    def is_valid_iban(iban: str):
        if not isinstance(iban, str):
            return False
        if not re.match(r"^[0-9]+([0-9]|\s)*$"):
            return False
        return True

    @staticmethod
    def is_valid_em_id(em_id: str):
        if not isinstance(em_id, str):
            return False
        if not re.match(r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"):
            return False
        return True
