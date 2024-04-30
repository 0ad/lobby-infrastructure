import os

from ansible.errors import AnsibleFilterTypeError


class FilterModule:

    @classmethod
    def convert_value(cls, value):
        if isinstance(value, (list, tuple)):
            l = [cls.convert_value(i) for i in value]
            return "[ " + ", ".join(l) + " ]"
        elif isinstance(value, dict):
            l = [f"{k} = {cls.convert_value(v)}" for k, v in value.items()]
            return "{ " + ", ".join(l) + " }"
        elif isinstance(value, str):
            return f"\"{value}\""
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            return str(value)

    @staticmethod
    def to_toml(value):
        """Convert a dictionary to TOML.

        This is a very naive, but good enough Jinja filter to convert a
        dictionary to TOML.

        Using a library like `tomli-w` would be more elegant, but would
        add an additional dependency for being able to run the Ansible
        code.
        """
        if not isinstance(value, dict):
            raise AnsibleFilterTypeError("Data to be converted to TOML needs to be a dictionary, "
                                         "got %s instead" % type(value))

        new_value = ""
        for key, value2 in value.items():
            converted_value = FilterModule.convert_value(value2)
            new_value += f"{key} = {converted_value}" + os.linesep
        return new_value

    def filters(self):
        return {
            'to_toml': self.to_toml
        }
