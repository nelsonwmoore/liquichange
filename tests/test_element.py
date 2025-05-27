"""Tests for liquichange element.py."""

from __future__ import annotations

from dataclasses import dataclass, field

from liquichange.element import LiquibaseElement, snake_to_camel


def test_tag() -> None:
    """Test tag property returns the correct tag name."""
    element_1 = LiquibaseElement()
    assert element_1.tag == ""

    element_2 = LiquibaseElement(_tag="testTag")
    assert element_2.tag == "testTag"


def test_get_attrs() -> None:
    """Test get_attrs() method returns the correct dictionary of attributes."""

    @dataclass
    class TestElement(LiquibaseElement):
        """Test Element."""

        include_int: int = 15
        include_bool: bool = True
        include_str: str = field(default="", metadata={"required": True})
        exclude_str: str = field(default="", metadata={"required": True})
        exclude_none: None = None
        _excluded_attrs: set[str] = field(
            default_factory=lambda: {
                "exclude_str",
                "exclude_none",
                "subelements",
                "_tag",
                "text",
                "NAMESPACE",
                "XSI_NAMESPACE",
                "NEO4J_NAMESPACE",
                "SCHEMA_LOCATION",
                "_excluded_attrs",
            },
        )

    element = TestElement(include_str="included", exclude_str="excluded")
    attrs = element.get_attrs()
    expected_attrs = {
        "includeInt": "15",
        "includeBool": "true",
        "includeStr": "included",
    }
    assert attrs == expected_attrs


def test_to_xml() -> None:
    """Test to_xml method of LiquibaseElement."""

    @dataclass
    class TestElement(LiquibaseElement):
        """Test Element."""

        _tag: str = "testTag"
        text: str = "test text"
        test_attr: str = "test attr value"

    element = TestElement()
    xml_element = element.to_xml()
    expected_attrs = {"testAttr": "test attr value"}
    assert xml_element.tag == "testTag"
    assert xml_element.text == "test text"
    assert xml_element.attrib == expected_attrs


def test_to_xml_nested() -> None:
    """Test to_xml method of LiquibaseElement with subelements."""

    @dataclass
    class ChildElement(LiquibaseElement):
        """Test Child Element."""

        _tag: str = "childTag"
        text: str = "test child text"
        child_attr: str = "test child value"

    @dataclass
    class ParentElement(LiquibaseElement):
        """Test Parent Element (Changelog)."""

        _tag: str = "parentTag"
        text: str = "test parent text"
        parent_attr: str = "test parent value"

    child_element = ChildElement()
    parent_element = ParentElement()
    parent_element.subelements.append(child_element)
    xml_element = parent_element.to_xml(_is_changelog=True)
    expected_attrs = {
        "xmlns": parent_element.NAMESPACE,
        "xmlns:xsi": parent_element.XSI_NAMESPACE,
        "xmlns:neo4j": parent_element.NEO4J_NAMESPACE,
        "xsi:schemaLocation": parent_element.SCHEMA_LOCATION,
        "parentAttr": "test parent value",
    }
    expected_child_attrs = {"childAttr": "test child value"}
    assert xml_element.tag == "parentTag"
    assert xml_element.attrib == expected_attrs
    assert len(xml_element.findall("childTag")) == 1
    xml_child = xml_element.find("childTag")
    if xml_child:
        assert xml_child.attrib == expected_child_attrs


def test_snake_to_camel() -> None:
    """Tests conversion of snake to camel case."""
    assert snake_to_camel("test_attr") == "testAttr"
    assert snake_to_camel("_test_attr") == "testAttr"
    assert snake_to_camel("test_attr_") == "testAttr"
    assert snake_to_camel("test") == "test"
