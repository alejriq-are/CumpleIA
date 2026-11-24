"""Test-only accommodation for roundtripping ancestor schemas below support history."""

from sqlalchemy import inspect, text

# Tablas posteriores cuyas FK hacia legal_assessments bloquean la bajada de las
# migraciones ancestro. Cada migración nueva con tabla propia se añade aquí.
DEPENDENT_TABLES = ("eipd_document_versions",)


def _detach_dependents(connection):
    tables = ",".join("'" + t + "'" for t in DEPENDENT_TABLES)
    rows = connection.execute(
        text(
            "SELECT conrelid::regclass::text, conname, pg_get_constraintdef(oid) "
            "FROM pg_constraint WHERE contype='f' "
            "AND confrelid='legal_assessments'::regclass "
            "AND conrelid::regclass::text IN (" + tables + ") ORDER BY 1,2"
        )
    ).all()
    detached = []
    for table, constraint, definition in rows:
        quoted = connection.dialect.identifier_preparer.quote(constraint)
        connection.execute(text("ALTER TABLE " + table + " DROP CONSTRAINT " + quoted))
        detached.append((table, quoted, definition))
    return detached


def _restore_dependents(connection, detached):
    for table, quoted, definition in detached:
        connection.execute(
            text(
                "ALTER TABLE " + table + " ADD CONSTRAINT " + quoted + " " + definition
            )
        )


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
    return name, _detach_dependents(connection)


def restore_support_parent(connection, handle):
    name, dependents = handle
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
    _restore_dependents(connection, dependents)
