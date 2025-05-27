"""Changelog, Changeset, Rollback, and Comment classes."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from liquichange.element import LiquibaseElement
from liquichange.precondition import DbmsPrecondition, Preconditions


class ObjectQuotingStrategy(str, Enum):
    """Values for objectQuotingStrategy attr."""

    LEGACY = "LEGACY"
    QUOTE_ALL_OBJECTS = "QUOTE_ALL_OBJECTS"
    QUOTE_ONLY_RESERVED_WORDS = "QUOTE_ONLY_RESERVED_WORDS"


class RunOrder(str, Enum):
    """Values for run orders."""

    FIRST = "first"
    LAST = "last"


class ChangeType(LiquibaseElement):
    """Class for type hinting various change type entities."""


@dataclass
class CypherChange(ChangeType):
    """Class for neo4j:cypher change type."""

    _tag: str = "neo4j:cypher"


@dataclass
class Rollback(LiquibaseElement):
    """
    Rollback statement for change types that don't auto-create them.

    Attributes:
        change_set_id (str): The ID of the changeset to rollback.
        change_set_author (str): The author of the changeset to rollback.
        change_type (ChangeType): The change type to rollback. Required.
    """

    change_set_id: str | None = None
    change_set_author: str | None = None

    subelements: list[ChangeType] = field(default_factory=list)
    _tag: str = "rollback"

    change_type: ChangeType | None = field(default=None, metadata={"required": True})

    def __post_init__(self) -> None:
        """Post-init method."""
        if self.change_type:
            self.subelements.append(self.change_type)


@dataclass
class Comment(LiquibaseElement):
    """Comment in Liquibase changelog."""

    _tag: str = "comment"


@dataclass
class Property(LiquibaseElement):
    """
    Property tag in Liquibase changelog.

    Used to substitute values for replacement tokens in the format of ${property-name}.

    Attributes:
        name (str): The name of the parameter. Required if file is not set.
        value (str): The value of the property. Required if file is not set.
        file (str): The name of the file from which the properties should be loaded.
            It will create a property for all properties in the file.
            The content of the file must follow the Java properties file format.
            Required if name and value not set.
        relative_to_changelog_file (str): used in conjunction with the file attribute
            to allow Liquibase to find referenced file without configuring search-path.
        context (str): Contexts in which the property is valid. Comma-separated list.
        dbms (DbmsPrecondition.DbmsType): Specifies which database type(s) a changeset
            is to be used for.
        global_ (bool): Property is global or limited to the actual DATABASECHANGELOG.
    """

    name: str | None = field(default=None, metadata={"required": True})
    value: str | None = field(default=None, metadata={"required": True})
    file: str | None = field(default=None, metadata={"required": True})
    relative_to_changelog_file: str | None = None
    context: str | None = None
    dbms: DbmsPrecondition.DbmsType | None = None
    global_: bool | None = None

    _tag: str = "property"
    subelements: list[Property] = field(default_factory=list)

    @staticmethod
    def validate_property_fields(values: dict[str, str]) -> None:
        """Validate that exactly one of enterprise or community is set to True."""
        name = values.get("name")
        value = values.get("value")
        file = values.get("file")

        if not file and not (name or value):
            msg = "If file isn't provided, name and value are required."
            raise RuntimeError(msg)

    def __post_init__(self) -> None:
        """Post-init method."""
        self.validate_property_fields(self.get_attrs())


@dataclass
class Include(LiquibaseElement):
    """
    include tag in Liquibase changelog.

    Use the include tag in the root changelog to reference other changelogs.

    Attributes:
        file (str): Name of the file you want to import required. Required.
        relative_to_changelog_file (bool): Specifies whether the file path is relative
            to the changelog file rather than looked up in the search path.
        context_filter (str): Appends a context (using AND statement) to all contained
            changesets.
        labels (str): Appends a label (using an AND statement) to all contained
            changesets.
    """

    file: str | None = field(default=None, metadata={"required": True})
    relative_to_changelog_file: bool | None = None
    context_filter: str | None = None
    labels: str | None = None

    _tag: str = "comment"
    subelements: None = None


@dataclass
class IncludeAll(LiquibaseElement):
    """
    includeAll tag in Liquibase changelog.

    Used to specify a directory that contains multiple changelog files.

    Attributes:
        file (str): Name of the file you want to import required. Required.
        relative_to_changelog_file (bool): Specifies whether the file path is relative
            to the changelog file rather than looked up in the search path.
        context_filter (str): Appends a context (using an AND statement) to all
            contained changesets.
        labels (str): Appends a label (with AND statement) to all contained changesets.
    """

    path: str | None = field(default=None, metadata={"required": True})
    error_if_missing_or_empty: bool | None = None
    relative_to_changelog_file: bool | None = None
    resource_comparator: str | None = None
    filter: str | None = None
    context_filter: str | None = None

    _tag: str = "comment"
    subelements: None = None


@dataclass
class Changeset(LiquibaseElement):
    """
    changeSet tag in Liquibase changelog.

    Basic unit of change in Liquibase. Changesets are stored in a Changelog.
    Best practice is to specify only one type of change per changeset.
    Nested elements (in subelements list): Comment, Preconditions, & Rollback.

    Attributes:
        id (str): Specifies an alpha-numeric identifier. Required.
        author (str): Specifies the creator of the changeset. Required.
        change_type (ChangeType): The type of change (neo4j:cypher, etc.). Required.
        dbms (str): Specifies which database type(s) a changeset is to be used for.
        context_filter (str): Specifies the changeset contexts to match.
        created (str): Stores dates, versions, or other string of value without using
            remarks (comments) attributes.
        labels (str): Specifies the changeset labels to match.
        logical_file_path (str): Overrides the file name and path when creating the
            unique identifier of changesets.
        run_order (RunOrder): The order in which the changeset should run relative to
            other changesets.
        fail_on_error (bool): Defines whether a database migration will fail if an error
            occurs while executing the changeset.
        ignore (bool): Tells Liquibase to treat a particular changeset as if it does not
            exist.
        object_quoting_strategy (ObjectQuotingStrategy): Controls how object names are
            quoted in SQL files generated by Liquibase and used in calls to database.
        run_always (bool): Executes the changeset on every run, even if run before.
        run_in_transaction (bool): Specifies whether the changeset can be run as
            a single transaction (if possible).
        run_on_change (bool): Executes the changeset when you create it and each time it
            changes.

    Methods:
        add_preconditions(precondition): Adds a precondition to the changeSet.
        set_rollback(rollback): Sets the rollback statement for the changeSet.
        set_comment(comment): Sets a comment for the changeSet.
    """

    id: str | None = field(default=None, metadata={"required": True})
    author: str | None = field(default=None, metadata={"required": True})
    change_type: ChangeType | None = field(
        default=None,
        metadata={"required": True},
    )

    dbms: str | None = None
    context_filter: str | None = None
    created: str | None = None
    labels: str | None = None
    logical_file_path: str | None = None
    run_order: RunOrder | None = None
    fail_on_error: bool | None = None
    ignore: bool | None = None
    object_quoting_strategy: ObjectQuotingStrategy | None = None
    run_always: bool | None = None
    run_in_transaction: bool | None = None
    run_on_change: bool | None = None

    _tag: str = "changeSet"
    subelements: list[ChangeType | Comment | Preconditions | Rollback | None] = field(
        default_factory=list,
    )

    _excluded_attrs: set[str] = field(
        default_factory=lambda: set(
            LiquibaseElement._merge_excluded_attrs({"change_type"}),  # noqa: SLF001
        ),
    )

    def __post_init__(self) -> None:
        """Post-init method."""
        if self.change_type:
            self.subelements.append(self.change_type)

    def add_preconditions(self, precondition: Preconditions) -> None:
        """Add a precondition to the changeSet."""
        precondition_ele = next(
            (e for e in self.subelements if isinstance(e, Preconditions)),
            None,
        )
        if not precondition_ele:
            self.subelements.append(precondition)
        else:
            precondition_ele.subelements.append(precondition)

    def set_rollback(self, rollback: Rollback) -> None:
        """Set the rollback statement for the changeSet."""
        self.subelements.append(rollback)

    def set_comment(self, comment: Comment) -> None:
        """Set a comment for the changeSet."""
        self.subelements.append(comment)


@dataclass
class Changelog(LiquibaseElement):
    """
    changeSet tag in Liquibase changelog.

    Sequential list of changes to be made to database, with individual units of change
    contained in changesets. Currently supports changelogs in XML format.

    Nested elements (in subelements list) may include Preconditions, Changesets,
    Include, & IncludeAll.

    Attributes:
        logical_file_path(str): Overrides the file name and path when creating the
            unique identifier of changesets.
        object_quoting_strategy: Controls how object names are quoted in the SQL files
            generated by Liquibase and used in calls to the database.

    Methods:
        add_changeset(changeset): Adds a changeset to the changelog by appending to its
            subelement list.
        to_xml(_is_changelog: bool = True) -> ET.Element: Returns the XML representation
            of the element. Overrides the LiquibaseElement method.
        save_to_file(file_path): Writes changelog to xml file at file_path.
    """

    logical_file_path: str | None = None
    object_quoting_strategy: ObjectQuotingStrategy | None = None

    _tag: str = "databaseChangeLog"
    subelements: list[
        Preconditions | Property | Changeset | Include | IncludeAll | None
    ] = field(default_factory=list)

    def add_changeset(self, changeset: Changeset) -> None:
        """Add a changeset to the changelog by appending to its subelement list."""
        self.subelements.append(changeset)

    def to_xml(self, *, _is_changelog: bool = True) -> ET.Element:
        """Return ET.Element representation of Changelog."""
        return super().to_xml(_is_changelog=_is_changelog)

    def save_to_file(self, file_path: str | Path, encoding: str | None = None) -> None:
        """Write changelog to xml file at file_path."""
        with Path(file_path).open("wb") as file:
            xml_element_tree = ET.ElementTree(self.to_xml())
            ET.indent(xml_element_tree)
            xml_element_tree.write(
                file,
                encoding=encoding,
                xml_declaration=True,
                method="xml",
            )

    def count_changesets(self) -> int:
        """Count the number of changesets in the changelog."""
        return len([x for x in self.subelements if isinstance(x, Changeset)])
