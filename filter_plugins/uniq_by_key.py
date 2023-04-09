from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @staticmethod
    def uniq_by_key(value, key=None):
        """Filter a list of dictionaries.

        Filter the provided list of dictionaries, so it contains only
        one instance of dictionary which has a certain value in the
        specified key.

        Example:

            ```
            some_list:
              - key: foo
              - key: bar
              - key: bar
            ```

            ```
            - name:
              ansible.builtin.debug:
                msg: "{{ some_list | uniq_by_key('key') }}"

            # => [{"key": "foo"}, {"key": "bar"}]
            ```
        """
        if not isinstance(value, list):
            raise AnsibleFilterTypeError("Data to be filtered needs to be a list of dicts, "
                                         "got %s instead" % type(value))

        if not key:
            raise AnsibleFilterTypeError("No key provided to filter for.")

        key_values = []
        new_value = []
        for item in value:
            if item[key] in key_values:
                continue

            key_values.append(item[key])
            new_value.append(item)

        return new_value

    def filters(self):
        return {
            'uniq_by_key': self.uniq_by_key
        }
