"""Tests for liquichange precondition.py."""

from __future__ import annotations

from xml.etree.ElementTree import tostring

from liquichange.precondition import (
    CypherCheckPrecondition,
    EditionPrecondition,
    Preconditions,
    VersionPrecondition,
)


def test_to_xml_nested_conditions() -> None:
    """Test to_xml method of Preconditions."""
    preconditions = Preconditions(
        on_fail=Preconditions.Action.WARN,
        on_fail_message="Epic Fail",
    )
    condition_1 = EditionPrecondition(community=True)
    condition_2 = VersionPrecondition(matches="1.2.3")

    preconditions.subelements = [condition_1, condition_2]
    xml_preconditions = preconditions.to_xml()
    expected_xml_str = (
        b'<preConditions onFail="WARN" onFailMessage="Epic Fail"><and>'
        b'<neo4j:edition community="true" />'
        b'<neo4j:version matches="1.2.3" />'
        b"</and></preConditions>"
    )
    assert tostring(xml_preconditions) == expected_xml_str


def test_to_xml_nested_preconditions() -> None:
    """Test to_xml method of LiquibaseElement with subelements."""
    parent_preconditions = Preconditions(on_fail=Preconditions.Action.CONTINUE)
    child_preconditions = Preconditions(conditional_logic=Preconditions.Logic.OR)
    child_condition = CypherCheckPrecondition(
        expected_result=0,
        text=(
            "MATCH (n) "
            "WHERE NONE(label IN LABELS(n) WHERE label STARTS WITH '__Liquibase') "
            "RETURN COUNT(n)"
        ),
    )
    grandchild_condition_1 = EditionPrecondition(enterprise=True)
    grandchild_condition_2 = VersionPrecondition(matches="4.4.0")

    child_preconditions.subelements = [grandchild_condition_1, grandchild_condition_2]
    parent_preconditions.subelements = [child_preconditions, child_condition]

    xml_preconditions = parent_preconditions.to_xml()
    expected_xml_str = (
        b'<preConditions onFail="CONTINUE">'
        b"<and>"
        b"<or>"
        b'<neo4j:edition enterprise="true" />'
        b'<neo4j:version matches="4.4.0" />'
        b"</or>"
        b'<neo4j:cypherCheck expectedResult="0">'
        b"MATCH (n) "
        b"WHERE NONE(label IN LABELS(n) WHERE label STARTS WITH '__Liquibase') "
        b"RETURN COUNT(n)"
        b"</neo4j:cypherCheck>"
        b"</and>"
        b"</preConditions>"
    )
    assert tostring(xml_preconditions) == expected_xml_str
