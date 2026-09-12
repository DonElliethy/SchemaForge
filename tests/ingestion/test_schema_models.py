import pytest
from pydantic import ValidationError
from schemaforge.ingestion.schema_models import Column, Foriegn_key, Table, Schema
from schemaforge.ingestion.ddl_parser import parse_ddl

def test_table_build():
    user = Table(
        name="users",
        cols=[
            Column(name="id", data_type="INTEGER", is_primary=True, nullable=False),
            Column(name="email", data_type="VARCHAR(255)"),
        ],
    )
    assert user.get_cols_names() == {"id", "email"}
    assert user.pk_col().name == "id"
    assert user.get_col("email").data_type == "VARCHAR(255)"
    assert user.get_col("should not find it") is None


def test_fk_tables():
    orders = Table(
        name="orders",
        cols=[
            Column(name="id", data_type="INTEGER", is_primary=True, nullable=False),
            Column(name="user_id", data_type="INTEGER"),
        ],
        fkeys=[
            Foriegn_key(column="user_id", ref_table="users", ref_col="id"),
        ],
    )
    orders.fk_validator()


def test_blank_name_reject():
    with pytest.raises(ValidationError):
        Column(name="   ", data_type="INTEGER")


def test_fk_to_missing_col_reject():
    bad_table = Table(
        name="orders",
        cols=[Column(name="id", data_type="INTEGER", is_primary=True, nullable=False)],
        fkeys=[Foriegn_key(column="user_id", ref_table="users", ref_col="id")],
    )
    with pytest.raises(ValueError):
        bad_table.fk_validator()

def test_primary_key_cannot_be_nullable():
    with pytest.raises(ValidationError):
        Column(name="id", data_type="INTEGER", is_primary=True, nullable=True)




# --- DDL tests for the parser ---


def test_parse_ddl_with_foreign_key():
    sql = """
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """

    expected = Schema(
        tables=[
            Table(
                name="orders",
                cols=[
                    Column(name="id", data_type="INT", is_primary=True, nullable=False),
                    Column(name="user_id", data_type="INT"),
                ],
                fkeys=[
                    Foriegn_key(column="user_id", ref_table="users", ref_col="id"),
                ],
            )
        ]
    )

    assert parse_ddl(sql) == expected

def test_parse_ddl_simple():


    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email VARCHAR(255)
    );
    """

    expected = Schema(
        tables=[
        Table(
    name="users",
    cols=[
        Column(name="id", data_type="INT", is_primary=True, nullable=False),
        Column(name="email", data_type="VARCHAR(255)"),
        ],
        )
        ]
    )

    assert parse_ddl(sql) == expected

def test_parse_ddl_without_null():

        
    sql = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );
    """
    expected = Schema(
        tables=[
            Table(
        name="products",
        cols=[
            Column(name="id", data_type="INT", is_primary=True, nullable=False),
            Column(name="name", data_type="VARCHAR(100)", nullable=False),
            ],
            )       
            ]
        )

    assert parse_ddl(sql) == expected
