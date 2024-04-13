from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

import odoo.models


class OdooModel(BaseModel):
    @classmethod
    def from_odoo(cls: type["OdooModel"], record: odoo.models.Model) -> "OdooModel":
        vals: dict = dict()
        for field_name, field_info in cls.model_fields.items():
            field_type: type = field_info.annotation
            field_value = getattr(record, field_name, None)

            if field_value is None and isinstance(field_info.default, PydanticUndefinedType):
                raise ValueError("Field required")

            if isinstance(field_value, odoo.models.Model):
                odoo_field_type = record._fields[field_name]
                if (isinstance(odoo_field_type, odoo.fields.One2many)
                        or isinstance(odoo_field_type, odoo.fields.Many2many)):
                    vals[field_name] = field_value.ids
                else:
                    vals[field_name] = field_value.id

            else:
                vals[field_name] = field_value is not None and field_value or None

        return cls(**vals)
