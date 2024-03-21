# Morpho Typing

This module provides a set of schemas common to the Morpho Design Explorer Server and GA-Search Client.

There are two schemas available as of now:
1. MorphoProjectSchema: defines and provides validation for the general structure of a project's schema
2. MorphoAssetCollection: defines a set of assets / files that are associated with a schema.

## Installation:
```shell
pip install morpho_typing
```

## Project Usage:

##### to validate a project schema definition
```python
schema = MorphoProjectSchema(values=[...])
```

##### to validate a record against an existing project schema object
```python
schema.validate_record(record)
```

##### to validate an asset collection definition
```python
asset_schema = MorphoAssetCollection(assets=[...])
```


