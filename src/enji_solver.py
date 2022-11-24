import sys, os,  json
from enji_verifier import evaluate_json, verify_components

if __name__ == '__main__':
    path_json = sys.argv[1]
    
    json_name = os.path.split(path_json)[-1]
    new_path_name = path_json[:-5] + '_evaluated.json' 

    with open(path_json, 'r') as file:
        json_template = json.load(file)

    verify_components(json_template)
    alias_value = evaluate_json(json_template)
    
    with open(new_path_name, 'w') as o:
        json.dump(alias_value, o, indent=2)
    
    print(f'\n \t The __{new_path_name}__ file saved successfully')

