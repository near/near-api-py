from typing import Union


class BinarySerializer:
    def __init__(self, schema: dict):
        self.array = bytearray()
        self.schema = schema

    def serialize_num(self, value: int, n_bytes: int):
        orig_value = value
        assert value >= 0, "Can't serialize negative numbers %d" % value    # TODO: Need to replace to Exception
        for i in range(n_bytes):
            self.array.append(value & 255)
            value //= 256
        assert value == 0, "Value %d has more than %d bytes" % (orig_value, n_bytes)    # TODO: Need to replace to Exception

    def serialize_field(self, value: Union[str, int], field_type: Union[str, list, dict, type]):
        try:
            if type(field_type) == str:
                if field_type[0] == 'u':
                    self.serialize_num(value, int(field_type[1:]) // 8)
                elif field_type == 'string':
                    b = value.encode('utf8')
                    self.serialize_num(len(b), 4)
                    self.array += b
                else:
                    assert False, field_type        # TODO: Need to replace to Exception
            elif type(field_type) == list:
                assert len(field_type) == 1    # TODO: Need to replace to Exception
                if type(field_type[0]) == int:
                    assert type(value) == bytes, "type(%s) = %s != bytes" % (value, type(value))    # TODO: Need to replace to Exception
                    assert len(value) == field_type[0], "len(%s) = %s != %s" % (value, len(value), field_type[0])    # TODO: Need to replace to Exception
                    self.array += bytearray(value)
                else:
                    self.serialize_num(len(value), 4)
                    for el in value:
                        self.serialize_field(el, field_type[0])
            elif type(field_type) == dict:
                assert field_type['kind'] == "option"    # TODO: Need to replace to Exception
                if value is None:
                    self.serialize_num(0, 1)
                else:
                    self.serialize_num(1, 1)
                    self.serialize_field(value, field_type['type'])
            elif type(field_type) == type:
                assert type(value) == field_type, "%s != type(%s)" % (field_type, value)    # TODO: Need to replace to Exception
                self.serialize_struct(value)
            else:
                assert False, type(field_type)    # TODO: Need to replace to Exception
        except Exception:
            print("Failed to serialize %s as %s" % (value, field_type))
            raise

    def serialize_struct(self, obj):
        struct_schema = self.schema[type(obj)]
        if struct_schema['kind'] == "struct":
            for fieldName, fieldType in struct_schema['fields']:
                self.serialize_field(getattr(obj, fieldName), fieldType)
        elif struct_schema['kind'] == "enum":
            name = getattr(obj, struct_schema['field'])
            for idx, (fieldName, fieldType) in enumerate(struct_schema['values']):
                if fieldName == name:
                    self.serialize_num(idx, 1)
                    self.serialize_field(getattr(obj, fieldName), fieldType)
                    break
        else:
            assert False, struct_schema     # TODO: Need to replace to Exception

    def serialize(self, obj):
        self.serialize_struct(obj)
        return bytes(self.array)
