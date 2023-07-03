"""Liquibase Preconditions"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Set, Union

from liquichange.element import LiquibaseElement


class Condition(LiquibaseElement):
    """For type hinting various precondition entities."""

    subelements: None = None


@dataclass
class Preconditions(LiquibaseElement):
    """
    Container class for preconditions used to group Preconditions and/or
    Condition objects that follow the same conditional_logic.

    Preconditions are tags you add to your changelog or individual changesets
    to control the execution of an update based on the state of the database.

    Use by adding any Preconditions or Condition type objects to the subelements list.

    Attributes:
        conditional_logic (Logic): AND or OR. Default AND.
        on_error (Action): Controls what happens if there is an error checking
            whether the precondition passed or not.
        on_error_message (str): rovides a custom message to output when preconditions fail.
        on_fail (Action): Controls what happens if the preconditions check fails.
        on_fail_message (str): Provides a custom message to output when preconditions fail.
        on_sql_output (SqlAction): Controls how preconditions are evaluated in the
            update-sql mode for XML, YAML, and JSON changelogs.
        on_update_sql (SqlAction): Controls how preconditions are evaluated in the
            update-sql mode for formatted SQL changelogs.

    Class Variables:
        Action (Enum): The Action enum.
        SqlAction (Enum): The SqlAction enum.
        Logic (Enum): The Logic enum.

    Methods:
        to_xml(_is_changelog: bool = False) -> ET.Element: Returns the XML representation
            of the element. Overrides the LiquibaseElement method to incorporate conditional
            logic of preconditions.
    """

    class Action(str, Enum):
        """Values for precondition types: onFail, onError."""

        CONTINUE = "CONTINUE"
        HALT = "HALT"
        MARK_RAN = "MARK_RAN"
        WARN = "WARN"

    class SqlAction(str, Enum):
        """Values for precondition types: onSqlOutput, onUpdateSql."""

        FAIL = "FAIL"
        IGNORE = "IGNORE"
        TEST = "TEST"

    class Logic(str, Enum):
        """Values for precondition conditional logic."""

        AND = "and"
        OR = "or"
        NOT = "not"

    on_error: Optional[Action] = None
    on_error_message: Optional[str] = None
    on_fail: Optional[Action] = None
    on_fail_message: Optional[str] = None
    on_sql_output: Optional[SqlAction] = None
    on_update_sql: Optional[SqlAction] = None

    _tag: str = "preConditions"
    conditional_logic: Logic = Logic.AND

    _excluded_attrs: Set[str] = field(
        default_factory=lambda: set(
            LiquibaseElement._merge_excluded_attrs({"conditional_logic"})
        )
    )

    def to_xml(self, _is_changelog: bool = False) -> ET.Element:
        root = ET.Element(self.tag)
        root.text = self.text
        root.attrib.update(self.get_attrs())

        root_logic = ET.Element(self.conditional_logic.value)

        for subelement in self.subelements:
            if isinstance(subelement, Preconditions):
                child_logic = ET.Element(subelement.conditional_logic.value)
                for element in subelement.subelements:
                    child_logic.append(element.to_xml())
                root_logic.append(child_logic)
            else:
                root_logic.append(subelement.to_xml())
        root.append(root_logic)
        return root


@dataclass
class DbmsPrecondition(Condition):
    """Defines if the database executed against matches the type specified."""

    class DbmsType(str, Enum):
        """potential database types for DbmsPrecondition"""

        NEO4J = "neo4j"

    type: Union[DbmsType, None] = field(default=None, metadata={"required": True})
    _tag: str = "dbms"


@dataclass
class VersionPrecondition(Condition):
    """
    Asserts the expected Neo4j version

    matches: expected Neo4j version as a string in the format:
        "major.minor.patch"
    """

    matches: Union[str, None] = field(default=None, metadata={"required": True})
    _tag: str = "neo4j:version"

    @staticmethod
    def validate_matches_format(values: Dict[str, str]) -> None:
        """
        Validates that matches attribute is in the format "major.minor.patch".
        """
        matches = values.get("matches", "")
        if not re.match(r"^\d+\.\d+\.\d+$", matches):
            raise ValueError(
                "Version number must be in the format 'major.minor.patch'."
            )

    def __post_init__(self) -> None:
        self.validate_matches_format(self.get_attrs())


@dataclass
class EditionPrecondition(Condition):
    """
    Asserts the expected Neo4j edition (Community or Enterprise).
    """

    enterprise: Union[bool, None] = field(default=None, metadata={"required": True})
    community: Union[bool, None] = field(default=None, metadata={"required": True})
    _tag: str = "neo4j:edition"

    @staticmethod
    def validate_edition_fields(values: Dict[str, str]) -> None:
        """
        Validates that exactly one of enterprise or community is set to True.
        """
        enterprise = values.get("enterprise")
        community = values.get("community")
        if (enterprise and community) or (not enterprise and not community):
            raise RuntimeError(
                "Exactly one of 'enterprise' or 'community' must be set to True."
            )

    def __post_init__(self) -> None:
        self.validate_edition_fields(self.get_attrs())


@dataclass
class CypherCheckPrecondition(Condition):
    """
    Executes a Cypher string and checks the returned value.

    The Cypher must return a single row with a single value.

    expectedResult: the value to compare the SQL result to. (required)
    """

    expected_result: Union[int, float, None] = field(
        default=None, metadata={"required": True}
    )
    _tag: str = "neo4j:cypherCheck"

    @staticmethod
    def validate_expected_result_format(values: Dict[str, str]) -> None:
        """
        Validates that the expected_result attribute is a valid integer or float.
        """
        expected_result = values.get("expectedResult", "")
        if not re.match(r'^["\']?\d+\.?\d*["\']?$', expected_result):
            raise ValueError("Expected result must be a valid integer or float.")

    def __post_init__(self) -> None:
        self.validate_expected_result_format(self.get_attrs())
