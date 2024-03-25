"""
This module provides a set of schemas common to the Morpho Design Explorer Server and GA-Search Client.

There are two schemas available as of now:
1. MorphoProjectSchema: defines and provides validation for the general structure of a project's schema
2. MorphoAssetCollection: defines a set of assets / files that are associated with a schema.

Project Usage:

# to validate a project schema definition
schema = MorphoProjectSchema(values=[...])

# to validate a record against an existing project schema object
schema.validate_record(record)

# to validate an asset collection definition
asset_schema = MorphoAssetCollection(assets=[...])
"""

from morpho_typing.types import MorphoProjectSchema, MorphoBaseType, MorphoProjectField, MorphoAsset, MorphoAssetCollection, MorphoQueryFilter, ValidationError
