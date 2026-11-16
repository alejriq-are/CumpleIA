"""Test-only accommodation for roundtripping ancestor schemas below support history."""

from sqlalchemy import inspect, text


def detach_empty_support_parent(connection):
    # Never invoke against an operational destination or discard support history.
    assert connection.in_transaction()
    assert connection.scalar(text("SELECT current_database()")) in (
        "cumpleia_test",
        "cumpleia_eipd_tests_20261009",
    )
    assert (
        connection.scalar(text("SELECT count(*) FROM assessment_support_records")) == 0
    )
    constraints = inspect(connection).get_foreign_keys("assessment_support_records")
    parent = [c for c in constraints if c["referred_table"] == "legal_assessments"]
    assert len(parent) == 1
    constraint = parent[0]
    assert constraint["constrained_columns"] == [
        "assessment_id",
        "treatment_id",
        "organization_id",
    ]
    assert constraint["referred_columns"] == ["id", "treatment_id", "organization_id"]
    assert constraint["options"]["ondelete"] == "RESTRICT"
    name = connection.dialect.identifier_preparer.quote(constraint["name"])
    connection.execute(
        text("ALTER TABLE assessment_support_records DROP CONSTRAINT " + name)
    )
    return name


def restore_support_parent(connection, name):
    connection.execute(
        text(
            "ALTER TABLE assessment_support_records ADD CONSTRAINT "
            + name
            + " FOREIGN KEY (assessment_id,treatment_id,organization_id) REFERENCES legal_assessments (id,treatment_id,organization_id) ON DELETE RESTRICT"
        )
    )
    parent = [
        c
        for c in inspect(connection).get_foreign_keys("assessment_support_records")
        if c["referred_table"] == "legal_assessments"
    ]
    assert len(parent) == 1 and parent[0]["options"]["ondelete"] == "RESTRICT"
