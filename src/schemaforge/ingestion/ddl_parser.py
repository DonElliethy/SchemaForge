import sqlglot
from sqlglot import exp

from schemaforge.ingestion.schema_models import Column, Foriegn_key, Table, Schema

#according to this shape of sqlglot parsing and storing we shall base our parser

#>>> import sqlglot
# ... from sqlglot import exp
# ... 
# ... sql = """
# ...  CREATE TABLE orders (
# ...      id INTEGER PRIMARY KEY NOT NULL,
# ...      FOREIGN KEY (user_id) REFERENCES users(id)
# ...  ); """
# ... tree = sqlglot.parse_one(sql, dialect="postgres")
# ... print(tree)
# ... 
# CREATE TABLE orders (id INT PRIMARY KEY NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id))
# >>> 
# ... for col in tree.find_all(exp.ColumnDef):
# ...     print(col.name, col.args)
# ... 
# ... for pk in tree.find_all(exp.PrimaryKeyColumnConstraint):
# ...     print(pk)
# ... for fk in tree.find_all(exp.ForeignKey):
# ...     print(fk, fk.args)
# ...     
# id {'this': Identifier(this=id, quoted=False), 'kind': DataType(this=DType.INT, nested=False), 'constraints': [ColumnConstraint(
#   kind=PrimaryKeyColumnConstraint()), ColumnConstraint(
#   kind=NotNullColumnConstraint())], 'position': None}
# PRIMARY KEY
# FOREIGN KEY (user_id) REFERENCES users (id) {'expressions': [Identifier(this=user_id, quoted=False)], 'reference': Reference(
#   this=Schema(
#     this=Table(
#       this=Identifier(this=users, quoted=False)),
#     expressions=[
#       Identifier(this=id, quoted=False)])), 'options': []}
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def parse_ddl(sql_text: str, dialect: str = "postgres")->Schema:

    statements = sqlglot.parse(sql_text,dialect=dialect)
    tables = []

    for st in statements:
        if isinstance(st,exp.Create):
            tables.append(_build_table(st))
    return Schema(tables=tables)


def _build_table(stmt: exp.Create) -> Table:
    table_name = stmt.this.this.name 

    columns = [_build_column(col) for col in stmt.find_all(exp.ColumnDef)]
    fkeys = [_build_foreign_key(fk) for fk in stmt.find_all(exp.ForeignKey)]

    return Table(name=table_name, cols=columns, fkeys=fkeys)

    
def _build_column(col: exp.ColumnDef) -> Column:
    is_pk = _is_primary_key(col)
    return Column(
        name=col.name,
        data_type=str(col.args["kind"]),
        is_primary=is_pk,
        nullable=False if is_pk else not _is_not_null(col),
    )


def _is_primary_key(col: exp.ColumnDef) -> bool:
    return any(
        isinstance(c.kind, exp.PrimaryKeyColumnConstraint)
        for c in col.args.get("constraints", [])
    )


def _is_not_null(col: exp.ColumnDef) -> bool:
    return any(
        isinstance(c.kind, exp.NotNullColumnConstraint)
        for c in col.args.get("constraints", [])
    )

def _build_foreign_key(fk: exp.ForeignKey) -> Foriegn_key:

    return Foriegn_key(
        column=fk.args['expressions'][0].name,
        ref_table=fk.args['reference'].this.this.name,
        ref_col=fk.args['reference'].this.expressions[0].name,
    )