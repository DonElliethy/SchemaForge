from pydantic import BaseModel,field_validator, model_validator
from typing import Optional



class Column(BaseModel):
    name: str
    data_type:str
    nullable:bool = True
    is_primary:bool = False

    @field_validator("name","data_type")
    @classmethod
    def not_blank(cls, value:str)->str:
        if not value.strip():
            raise ValueError("the name or the data type valaue was blank, ensure it is not")
        return value

    @model_validator(mode="after")
    def primary_key_cannot_be_nullable(self):
        if self.is_primary and self.nullable:
            raise ValueError(f"column '{self.name}' is a primary key but marked nullable")
        return self

#note to self: separating the foriegn key in a separate definition removes confusing not needed redundency of decalring or 
# defining it in the col class itself as most of the cols would already not be foriegn keys

class Foriegn_key(BaseModel):
    column:str
    ref_col:str
    ref_table:str


class Table(BaseModel):

    name:str
    cols: list[Column]
    fkeys: list[Foriegn_key] = []

    @field_validator("cols")
    @classmethod
    def cols_exist(cls, cols: list[Column]) -> list[Column]:
        if not cols:
            raise ValueError("any table must have columns")
        return cols

    def get_cols_names(self)->set[str]:
        return {col.name for col in self.cols}

    def get_col(self, name:str)->Optional[Column]:
        for col in self.cols:
            if name == col.name:
                return col
        return None

    def pk_col(self)->Optional[Column]:
        for col in self.cols:
            if col.is_primary:
                return col
        return None

    def fk_validator(self) ->None:

        for fk in self.fkeys:
            if fk.column not in self.get_cols_names():
                raise ValueError(
                    f"foreign key references column '{fk.column}' "
                    f"which does not exist on table '{self.name}'"
                )


class Schema(BaseModel):

    tables: list[Table]

    def table_names(self) -> set[str]:

        return {table.name for table in self.tables}

    def get_table(self,name: str)-> Optional[Table]:

        for table in self.tables:
            if table.name == name:
                return table

        return None

    def fk_acrossTables_fks(self)->None:

        for table in self.tables:
            table.fk_validator()
            for fk in table.fkeys:
                target_table = self.get_table(fk.ref_table)
                if target_table is None:
                    raise ValueError(
                        f"Table '{table.name}' has a foreign key referencing "
                        f"unknown table '{fk.ref_table}'"
                    )
                if fk.ref_col not in target_table.get_cols_names(): 
                    raise ValueError(
                        f"Table '{table.name}' has a foreign key referencing "
                        f"'{fk.ref_table}.{fk.ref_col}', "
                        f"but that column does not exist"
                    )     
        return self