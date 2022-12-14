import json
import os
from dataclasses import dataclass
from typing import List, Union, Dict

from python_graphql_client import GraphqlClient


@dataclass
class CalcComponent:
    variable_name: str
    alias: str
    constant_formula: Union[str, float]
    unit: str
    description: str
    comment: str

    @classmethod
    def from_data(cls, data):
        return cls(
            data["variable-name"],
            data["alias"],
            data["constant-formula"],
            data["unit"],
            data["description"],
            data["comment"],
        )

    def to_update_variable(self) -> Dict:
        return {
            "glyph": self.variable_name,
            "value": str(self.constant_formula),
            "unit": self.unit,
            "description": self.description,
            "comment": self.comment,
        }


@dataclass
class Section:
    section_name: str
    variables: List[str]

    @classmethod
    def from_data(cls, data):
        return cls(
            data["section-name"],
            data["variables"],
        )


@dataclass
class Project:
    title: str
    calc_components: List[CalcComponent]
    sections: List[Section]

    @classmethod
    def from_data(cls, data):
        return cls(
            data["title"],
            list(map(CalcComponent.from_data, data["calc-components"])),
            list(map(Section.from_data, data["sections"])),
        )

    def to_import_document(self):
        return {
            "title": self.title,
            "symbols": list(map(lambda v: {
                "varname": v.alias,
                "glyph": v.variable_name,
                "aliases": [v.alias],
                "value": str(v.constant_formula),
                "unit": v.unit,
                "description": v.description,
                "comment": v.comment,
            }, self.calc_components)),
            "sections": list(map(lambda v: {
                "title": v.section_name,
                "symbols": v.variables,
            }, self.sections)),
        }


def create_project_json(project: Project, filename: str):
    project_json = project.to_import_document()
    with open(filename, 'w') as fout:
        json.dump({"project": project_json}, fout, indent=2)


QUERY_CREATE_PROJECT = "mutation { activeResult: createProject { id version title } }"

QUERY_UPDATE_PROJECT = """
mutation($projectId: ID!, $version: Int!, $project: ProjectInput!) {
  activeResult: updateProject(id: $projectId, version: $version, project: $project) { id version title }
}
"""

QUERY_CREATE_SYMBOL = """
mutation($projectId: ID!, $symbol: SymbolInput!) {
  activeResult: createSymbol(projectId: $projectId, symbol: $symbol) { id version }
}
"""

QUERY_CREATE_UPDATE_SYMBOL_ALIAS = """
mutation($symbolId: ID! $symbolAlias: SymbolAliasInput!) {
  activeResult: createSymbolAlias(symbolId: $symbolId, symbolAlias: $symbolAlias) { id version value }
}
"""


def run_query(client, query, variables):
    reply = client.execute(query, variables)
    result = reply and reply.get("data") and reply.get("data").get("activeResult")
    if result is None:
        raise Exception(f"Query failed: {reply}")
    res_id, res_version = result['id'], result['version']
    del result['id']
    del result['version']
    return res_id, res_version, result


def import_project(project: Project):

    client = GraphqlClient(
        endpoint=os.environ.get("GRAPHQL_URL", "https://app.silael.com/api/graphql"),
        headers={"Cookie": "JSESSIONID=YOU_NEED_TO_COPY_FROM_BROWSER"}
    )

    def _run_query(query, variables=None):
        return run_query(client, query, variables or dict())

    project_id, project_version, project_data = _run_query(QUERY_CREATE_PROJECT)
    print(f"Created project {project_id}")

    qv = {"projectId": project_id, "version": project_version, "project": {"title": project.title}}
    project_id, project_version, project_data = _run_query(QUERY_UPDATE_PROJECT, qv)
    if project_data["title"] != project.title:
        raise Exception(f"Title check fail")
    print(f"Updated project {project_id}")

    for i, symbol in enumerate(project.calc_components):

        qv = {"projectId": project_id, "symbol": symbol.to_update_variable()}
        symbol_id, symbol_version, _ = _run_query(QUERY_CREATE_SYMBOL, qv)
        print(f"Created symbol {symbol_id}")

        qv = {"symbolId": symbol_id, "symbolAlias": {"value": symbol.alias}}
        symbol_alias_id, symbol_alias_version, symbol_alias_data = _run_query(QUERY_CREATE_UPDATE_SYMBOL_ALIAS, qv)
        print(f"Created-Updated symbol alias {symbol_id} ({symbol_alias_data.get('value')})")


def main():
    with open("../tests/test_cli/creep_coefficient_ec2.json") as fin:
        data = json.load(fin)
    project = Project.from_data(data)
    create_project_json(project, "tmp.json")
    import_project(project)


if __name__ == '__main__':
    main()
