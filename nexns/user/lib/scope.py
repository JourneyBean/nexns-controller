from enum import Enum


class ApiKeyScope:

    @staticmethod
    def from_dict(d: dict):
        s = ApiKeyScope()
        s.__dict__.update(d)
        return s

    def __init__(self) -> None:
        
        self.can_read_domains = False
        self.can_create_domains = False
        self.can_modify_domains = False
        self.can_delete_domains = False

        self.can_read_variables = False
        self.can_create_variables = False
        self.can_modify_variables = False
        self.can_delete_variables = False

        self.can_read_specific_domains = []
        self.can_modify_specific_domains = []

        self.can_read_specific_zones = []
        self.can_modify_specific_zones = []

        self.can_read_specific_records = []
        self.can_modify_specific_records = []

        self.can_read_specific_variables = []
        self.can_modify_specific_variables = []
