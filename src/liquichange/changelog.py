"""
Changelog, Changeset, Rollback, Comment
"""
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from liquichange.element import LiquibaseElement
from liquichange.precondition import DbmsPrecondition, Preconditions


class ObjectQuotingStrategy(str, Enum):
    """values for objectQuotingStrategy attr"""

    LEGACY = "LEGACY"
    QUOTE_ALL_OBJECTS = "QUOTE_ALL_OBJECTS"
    QUOTE_ONLY_RESERVED_WORDS = "QUOTE_ONLY_RESERVED_WORDS"


class BooleanEnum(str, Enum):
    """values for fields that can be 'true' or 'false'"""

    TRUE = "true"
    FALSE = "false"


class RunOrder(str, Enum):
    """values for run orders"""

    FIRST = "first"
    LAST = "last"


class ChangeType(LiquibaseElement):
    """for type hinting various change type entities"""


@dataclass
class CypherChange(ChangeType):
    """neo4j:cypher change type"""

    _tag: str = "neo4j:cypher"


@dataclass
class Rollback(LiquibaseElement):
    """rollback statement for change types that don't auto-create them"""

    change_set_id: Optional[str] = None
    change_set_author: Optional[str] = None

    subelements: List[ChangeType] = field(default_factory=list)
    _tag: str = "rollback"

    change_type: Optional[ChangeType] = field(default=None, metadata={"required": True})

    def __post_init__(self):
        if self.change_type:
            self.subelements.append(self.change_type)


@dataclass
class Comment(LiquibaseElement):
    """liquibase comment"""

    _tag: str = "comment"


@dataclass
class Property(LiquibaseElement):
    """liquibase property"""

    name: Union[str, None] = field(default=None, metadata={"required": True})
    value: Union[str, None] = field(default=None, metadata={"required": True})
    file: Union[str, None] = field(default=None, metadata={"required": True})
    relative_to_changelog_file: Optional[str] = None
    context: Optional[str] = None
    dbms: Optional[DbmsPrecondition.DbmsType] = None
    global_: Optional[bool] = None

    _tag: str = "property"
    subelements: List["Property"] = field(default_factory=list)

    @staticmethod
    def validate_property_fields(values: Dict[str, str]) -> None:
        """
        Validates that exactly one of enterprise or community is set to True.
        """
        name = values.get("name")
        value = values.get("value")
        file = values.get("file")

        if not file and not (name or value):
            raise RuntimeError("If file isn't provided, name and value are required.")

    def __post_init__(self) -> None:
        self.validate_property_fields(self.get_attrs())


@dataclass
class Include(LiquibaseElement):
    """liquibase include element"""

    file: Union[str, None] = field(default=None, metadata={"required": True})
    relative_to_changelog_file: Optional[bool] = None
    context_filter: Optional[str] = None
    labels: Optional[str] = None

    _tag: str = "comment"
    subelements: None = None


@dataclass
class IncludeAll(LiquibaseElement):
    """liquibase include element"""

    path: Union[str, None] = field(default=None, metadata={"required": True})
    error_if_missing_or_empty: Optional[bool] = None
    relative_to_changelog_file: Optional[bool] = None
    resource_comparator: Optional[str] = None
    filter: Optional[str] = None
    context_filter: Optional[str] = None

    _tag: str = "comment"
    subelements: None = None


@dataclass
class Changeset(LiquibaseElement):
    """
    One unit of change in liquibase changelog
    """

    id: Union[str, None] = field(default=None, metadata={"required": True})
    author: Union[str, None] = field(default=None, metadata={"required": True})
    change_type: Union[ChangeType, None] = field(
        default=None, metadata={"required": True}
    )

    dbms: Optional[str] = None
    context_filter: Optional[str] = None
    created: Optional[str] = None
    labels: Optional[str] = None
    logical_file_path: Optional[str] = None
    run_order: Optional[RunOrder] = None
    fail_on_error: Optional[bool] = None
    ignore: Optional[bool] = None
    object_quoting_strategy: Optional[ObjectQuotingStrategy] = None
    run_always: Optional[bool] = None
    run_in_transaction: Optional[bool] = None
    run_on_change: Optional[bool] = None

    _tag: str = "changeSet"
    subelements: List[
        Union[
            ChangeType, Optional[Comment], Optional[Preconditions], Optional[Rollback]
        ]
    ] = field(default_factory=list)

    _excluded_attrs: Set[str] = field(
        default_factory=lambda: set(
            LiquibaseElement._merge_excluded_attrs({"change_type"})
        )
    )

    def __post_init__(self):
        if self.change_type:
            self.subelements.append(self.change_type)

    def add_preconditions(self, precondition: Preconditions):
        """adds a precondition to the changeSet"""
        precondition_ele = next(
            (e for e in self.subelements if isinstance(e, Preconditions)), None
        )
        if not precondition_ele:
            self.subelements.append(precondition)
        else:
            precondition_ele.subelements.append(precondition)

    def set_rollback(self, rollback: Rollback):
        """sets the rollback statement for the changeSet"""
        self.subelements.append(rollback)

    def set_comment(self, comment: Comment):
        """sets a comment for the changeSet"""
        self.subelements.append(comment)


@dataclass
class Changelog(LiquibaseElement):
    """liquibase changelog"""

    logical_file_path: Optional[str] = None
    object_quoting_strategy: Optional[ObjectQuotingStrategy] = None

    _tag: str = "databaseChangeLog"
    subelements: List[
        Union[Optional[Preconditions], Property, Changeset, Include, IncludeAll]
    ] = field(default_factory=list)

    def to_xml(self, _is_changelog: bool = True) -> ET.Element:
        """Returns ET.Element representation of Changelog."""
        return super().to_xml(_is_changelog=_is_changelog)

    def save_to_file(self, file_path: str, encoding: Optional[str] = None):
        """writes changelog to xml file"""
        with open(file_path, "wb") as file:
            xml_element_tree = ET.ElementTree(self.to_xml())
            ET.indent(xml_element_tree)
            xml_element_tree.write(
                file, encoding=encoding, xml_declaration=True, method="xml"
            )
