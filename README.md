# liquichange
Build and modify Liquibase changelogs in Python.

## Installation

```bash
$ pip install liquichange
```

## Usage

`liquichange` can be used to generate Liquibase XML changelogs as follows:

```python
from liquichange.changelog import Changelog, Changeset, CypherChange

# instantiate Changelog
changelog = Changelog()

# add Changeset with change_type neo4j:cypher to Changelog
changeset = Changeset(
  id="42",
  author="Nelson",
  change_type=CypherChange(
    text="MERGE (:property {handle: 'fastq_name', model: 'GDC'})"
  )
)
changelog.add_changeset(changeset)

# write changelog to XML file
file_path = "path/to/file.xml"
changelog.save_to_file(
  file_path=file_path,
  encoding="UTF-8"
)
```

## License

`liquichange` is licensed under the terms of the the Apache 2.0 license.

LIQUIBASE is a registered trademark of Liquibase, INC. Liquibase Open Source is released under the Apache 2.0 license.
