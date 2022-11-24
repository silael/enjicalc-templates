import sys, os, json
from typing import Any, Dict

from ast_evaluator import evaluate_formula

class TemplateStructureError(Exception):
    pass

standard_template_path = os.path.join(
    os.getcwd(), 
    'templates', 
    'enjicalc_standard_template.json'
)

with open(standard_template_path, 'r') as file:
    ENJI_JSON_STRUCTURE = json.load(file)

_ , components, sections = list(ENJI_JSON_STRUCTURE.keys())


def verify_components(json_template: Dict[str, Any]) -> None:
    if json_template.keys() != ENJI_JSON_STRUCTURE.keys(): 
        raise TemplateStructureError('The main structure is not aligned with Enjicalc standard template organisation')

    if type(json_template[components]) != list: 
        raise TemplateStructureError('Components need to be organized in a list data structure []')

    enji_component_keys = ENJI_JSON_STRUCTURE[components][0].keys()
    enji_component_required_keys = set(list(enji_component_keys)[1:4])
    
    for component in json_template[components]:
        intersection = set(component.keys()) & enji_component_required_keys
        if  intersection != enji_component_required_keys: 
            raise TemplateStructureError(f'Invalid structure of the component {component}')

    if type(json_template[sections]) != list: 
        raise TemplateStructureError('Section need to be organized in a list data structure []')

    return

def evaluate_json(json_template: Dict[str, Any]) -> Dict[str, float]:
    symbol_values = {}

    for component in json_template[components]:
        try: 
            int(component['constant-formula'])
            symbol_values.update({component['alias'] : float(component['constant-formula']) }) 
        except BaseException: 
            symbol_values.update({component['alias'] : evaluate_formula(component['constant-formula'], symbol_values)}) 

    return symbol_values

def verify_latex_symbols():
    pass

if __name__ == '__main__':
    path = sys.argv[1]
    json_name = os.path.split(path)[-1]

    with open(path, 'r') as file:
        json_template = json.load(file)

    verify_components(json_template)
    evaluate_json(json_template)
    
    print(f'\n \t The __{json_name}__ file structure is correct')
