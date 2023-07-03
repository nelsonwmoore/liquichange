"""
Liquibase Element
"""
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import ClassVar, Dict, List, Set


@dataclass
class LiquibaseElement:
    """
    Base Liquibase class for elements such as Changelog, Changeset,
    Preconditions, Comment, and Rollback.

    Attributes:
        subelements (List[LiquibaseElement]): A list of sub-elements.
        _tag (str): The tag name of the element.
        text (str): The text content of the element.

    Class Variables:
        NAMESPACE (str): The XML namespace for the Liquibase elements.
        XSI_NAMESPACE (str): The XML namespace for the XML Schema Instance.
        NEO4J_NAMESPACE (str): The XML namespace for Neo4j extensions.
        SCHEMA_LOCATION (str): The location of the XML schema.

    Methods:
        tag() -> str: Returns the tag name of the element.
        get_attrs() -> Dict[str, str]: Returns the element attributes as a dictionary.
        to_xml(_is_changelog: bool = False) -> ET.Element: Returns the XML representation
            of the element.
    """

    subelements: List["LiquibaseElement"] = field(default_factory=list)
    _tag: str = ""
    text: str = ""

    NAMESPACE: ClassVar[str] = "http://www.liquibase.org/xml/ns/dbchangelog"
    XSI_NAMESPACE: ClassVar[str] = "http://www.w3.org/2001/XMLSchema-instance"
    NEO4J_NAMESPACE: ClassVar[str] = "http://www.liquibase.org/xml/ns/dbchangelog-ext"
    SCHEMA_LOCATION: ClassVar[str] = f"{NAMESPACE} {NAMESPACE}/dbchangelog-latest.xsd"

    COMMON_EXCLUDED_ATTRS: ClassVar[Set[str]] = {
        "subelements",
        "_tag",
        "text",
        "NAMESPACE",
        "XSI_NAMESPACE",
        "NEO4J_NAMESPACE",
        "SCHEMA_LOCATION",
        "_excluded_attrs",
    }

    _excluded_attrs: Set[str] = field(
        default_factory=lambda: set(LiquibaseElement.COMMON_EXCLUDED_ATTRS)
    )

    @property
    def tag(self) -> str:
        """LiquibaseElement.tag getter"""
        return self._tag

    def get_attrs(self) -> Dict[str, str]:
        """returns liquibase element attrs as a dict"""
        return {
            snake_to_camel(attr): str(val.value)
            if isinstance(val, Enum)
            else str(val).lower()
            if isinstance(val, bool)
            else str(val)
            for attr, val in asdict(self).items()
            if val is not None and attr not in self._excluded_attrs
        }

    @classmethod
    def _merge_excluded_attrs(cls, child_excluded_attrs: Set[str]) -> Set[str]:
        return cls.COMMON_EXCLUDED_ATTRS.union(child_excluded_attrs)

    def to_xml(self, _is_changelog: bool = False) -> ET.Element:
        """Returns ET.ElementTree representation of element."""
        root = ET.Element(self.tag)
        if _is_changelog:
            root.attrib.update(
                {
                    "xmlns": self.NAMESPACE,
                    "xmlns:xsi": self.XSI_NAMESPACE,
                    "xmlns:neo4j": self.NEO4J_NAMESPACE,
                    "xsi:schemaLocation": self.SCHEMA_LOCATION,
                }
            )
        root.text = self.text
        root.attrib.update(self.get_attrs())
        for subelement in self.subelements:
            root.append(subelement.to_xml())
        return root


def snake_to_camel(snake_str: str) -> str:
    """converts string from snake case to camel case"""
    components = snake_str.split("_")
    components = [c for c in components if c]
    return components[0] + "".join(x.title() for x in components[1:])
