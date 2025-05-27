"""Test for changelog.py."""

from xml.etree.ElementTree import tostring

from liquichange.changelog import Changelog, Changeset, CypherChange, Rollback


def test_changeset_to_xml() -> None:
    """Test changeset to_xml method."""


def test_changeset_add_preconditions() -> None:
    """Test changeset add_preconditions method."""


def test_changeset_set_rollback() -> None:
    """Test changeset set_rollback method."""


def test_changeset_set_comment() -> None:
    """Test changeset set_comment method."""


def test_changeset_add_changelog() -> None:
    """Test changeset add_changeset method."""
    changelog = Changelog()
    changeset = Changeset(
        id="1",
        author="William Gibson",
        change_type=CypherChange(text="MERGE (:Book {title: 'Neuromancer'})"),
    )
    changelog.add_changeset(changeset)
    assert changelog.subelements == [changeset]


def test_changelog_to_xml() -> None:
    """Test changeset to_xml method."""
    changelog = Changelog()
    changeset = Changeset(
        change_type=CypherChange(text="MERGE (:Movie {title: 'My Life'})"),
    )
    changeset.set_rollback(
        Rollback(text="MATCH (m:Movie {title: 'My Life'}) DETACH DELETE m"),
    )
    expected_xml_str = (
        b'<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'xmlns:neo4j="http://www.liquibase.org/xml/ns/dbchangelog-ext" '
        b'xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog '
        b'http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">'
        b"<changeSet>"
        b"<neo4j:cypher>MERGE (:Movie {title: 'My Life'})</neo4j:cypher>"
        b"<rollback>MATCH (m:Movie {title: 'My Life'}) DETACH DELETE m</rollback>"
        b"</changeSet>"
        b"</databaseChangeLog>"
    )

    changelog.subelements = [changeset]
    xml_changelog = changelog.to_xml()

    assert tostring(xml_changelog) == expected_xml_str


def test_count_changesets() -> None:
    """Test count_changesets method."""
    changelog = Changelog()
    changeset_1 = Changeset(
        change_type=CypherChange(text="MERGE (:Movie {title: 'My Life'})"),
    )
    changelog.add_changeset(changeset_1)
    assert changelog.count_changesets() == 1
    changeset_2 = Changeset(
        change_type=CypherChange(text="MERGE (:Movie {title: 'Heat'})"),
    )
    changelog.add_changeset(changeset_2)
    assert changelog.count_changesets() == 2  # noqa: PLR2004
