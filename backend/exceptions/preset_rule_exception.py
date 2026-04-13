class PresetRuleAlreadyExists(Exception):
    """常用規則已存在時引發的例外。"""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Preset rule name: '{name}' already exists")


class PresetRuleNotFound(Exception):
    """常用規則不存在時引發的例外。"""

    def __init__(self, preset_rule_id: str):
        self.preset_rule_id = preset_rule_id
        super().__init__(f"Preset rule Id: '{preset_rule_id}' not found")
