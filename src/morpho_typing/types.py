from enum import StrEnum
from typing_extensions import Annotated
import pydantic


class ArcType(StrEnum):

    """
    Represents the atomic data types
    """

    INT = "INT"
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    STRING = "STRING"

    @property
    def native_type(self):
        """
        A mapping from an ArcType to its corresponding native python type
        """
        python_types = {
            self.INT: int,
            self.DOUBLE: float,
            self.FLOAT: float,
            self.STRING: str
        }
        return python_types[self]


class Field(pydantic.BaseModel):

    """
        Represents a field in an ArcSchema

        :param `field_name`: name of the field
        :param `field_type`: type of the field; ArcType
        :param `field_name`: name of the field
        :param `field_name`: name of the field
    """

    field_name: str
    field_type: ArcType
    field_unit: str
    field_range: list[int | float] = pydantic.Field(
        max_length=2, min_length=2)

    @pydantic.field_validator('field_range')
    @classmethod
    def range_validator(cls, range: list[int | float]) -> list[int | float]:
        if range[0] >= range[1]:
            raise ValueError(
                f"range {range} is not valid; {range[0]} is not lesser than {range[1]}")
        return range


class ArcSchema(pydantic.BaseModel):
    """
    Represents a set of named variadic parameters belonging to a project.

    Each field has a definite atomic type, along with it's unit and range of values.

    This schema is initialized with a dictionary.

    Example: {
        "STEP": {
            "UNIT": "",
            "TYPE": "INT",
            "RANGE": (0, 10)
        },
        "HEIGHT": {
            "UNIT": "m",
            "TYPE": "DOUBLE",
            "RANGE": (0, 100)
        }
    }
    """

    # A mapping of existing fields in the schema to their types
    fields: list[Field]

    @pydantic.computed_field
    def parameter_models(self) -> list[pydantic.BaseModel]:
        """
            Constructed list of validating models corresponding to each field in the schema
        """
        parameter_models = []
        for field in self.fields:
            ValueType = Annotated[field.field_type.native_type, pydantic.Field(
                ge=field.field_range[0],
                le=field.field_range[1]
            )]
            ParameterModel = pydantic.create_model(
                f"parameter_{field.field_name}",
                value=(ValueType, None)
            )
            parameter_models.append(ParameterModel)
        return parameter_models

    def validate_record(self, record: list[int | str | float]) -> tuple[bool, list[str]]:
        """
            Validates a list of parameters against an ArcSchema

            :param `record`: list of parameter values
            :returns: `(is_valid, list_of_errors)`
            :rtype: `(bool, list[str])`
        """

        if len(record) != len(self.parameter_models):
            raise Exception(
                f"Length of record does not match number of parameters {len(self.parameter_models)}")

        errors = []
        for item, parameter_model in zip(record, self.parameter_models):
            try:
                parameter_model.validate({"value": item})
            except pydantic.ValidationError as e:
                errors.append((e.errors()[0]['msg'], parameter_model.__name__))
        if len(errors) > 0:
            return (False, errors)
        else:
            return (True, [])
