from enum import StrEnum
from typing_extensions import Annotated, Literal, Optional
import pydantic
from pydantic import ValidationError


class MorphoBaseType(StrEnum):

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
        A mapping from an MorphoBaseType to its corresponding native python type
        """
        python_types = {
            self.INT: int,
            self.DOUBLE: float,
            self.FLOAT: float,
            self.STRING: str
        }
        return python_types[self]


class MorphoProjectField(pydantic.BaseModel):

    """
        Represents a field in an MorphoSchema

        :param `field_name`: name of the field
        :param `field_type`: type of the field; MorphoBaseType
        :param `field_name`: name of the field
        :param `field_name`: name of the field
    """

    field_name: str
    field_type: MorphoBaseType
    field_unit: str
    field_range: list[int | float] = pydantic.Field(
        max_length=2, min_length=2)
    field_step: int | float
    field_precision: Optional[int]

    @pydantic.validator('field_precision')
    def precision_should_be_int(cls, field_precision: int | None) -> int | None:
        if field_precision is not None:
            assert isinstance(field_precision, int)
        return field_precision

    @pydantic.field_validator('field_range')
    @classmethod
    def range_validator(cls, range: list[int | float]) -> list[int | float]:
        if range[0] >= range[1]:
            raise ValueError(
                f"range {range} is not valid; {range[0]} is not lesser than {range[1]}")
        return range


class MorphoProjectSchema(pydantic.BaseModel):
    """
    Represents a set of named variadic parameters belonging to a project.

    Each field has a definite atomic type, along with its unit and range of values.

    This schema is initialized with a dictionary.

    Example: schema = MorphoSchma(values=[
        {
            "field_name": "step",
            "field_unit": "",
            "field_type": "INT",
            "field_range": (0, 10)
            "field_step": 1
        },
        {
            "field_name": "height",
            "field_unit": "m",
            "field_type": "DOUBLE",
            "field_range": (0, 100)
            "field_step": 2.5
        }
    ])
    """

    # A mapping of existing fields in the schema to their types
    fields: list[MorphoProjectField]

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
            Validates a list of parameters against an MorphoSchema

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
            except ValidationError as e:
                errors.append((e.errors()[0]['msg'], parameter_model.__name__))
        if len(errors) > 0:
            return (False, errors)
        else:
            return (True, [])


class MorphoAsset(pydantic.BaseModel):
    """
    Definition of an Asset within the schema of a project.
    """
    tag: str
    description: str
    extension: str
    mime_type: str


class MorphoAssetCollection(pydantic.BaseModel):
    """
    Represents a collection of Asset definition
    Example: MorphoAssetCollection(values=[
        {
            tag: "jpg1",
            description: "A heat model of the architectural model",
            extension: "jpg",
            mimetype: "image/jpeg"
        }
    ])
    """
    assets: list[MorphoAsset]


class MorphoQueryFilter(pydantic.BaseModel):
    field_name: str
    comparator: Literal[">", "<", ">=", "<=", "==", "!="]
    value: MorphoBaseType


if __name__ == "__main__":
    # test run

    project_schema = [
        {
            "field_name": "step",
            "field_unit": "",
            "field_type": "INT",
            "field_range": (0, 10)
        },
        {
            "field_name": "height",
            "field_unit": "m",
            "field_type": "DOUBLE",
            "field_range": (0, 100)
        }
    ]

    asset_schema = [
        {
            "tag": "jpg1",
            "description": "heatmap of a building",
            "extension": "jpg",
            "mime_type": "image/jpeg"
        }
    ]

    ps = MorphoProjectSchema(fields=project_schema)
    a = MorphoAssetCollection(assets=asset_schema)

    print(ps)
    print(a)
