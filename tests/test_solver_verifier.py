import sys, os
import json
import pytest
import subprocess

verifier_path = os.path.join(
    'src',
    'enji_verifier.py'
)

solver_path = os.path.join(
    'src',
    'enji_solver.py'
)

template_path = os.path.join(
    'tests',
    'test_cli',
    'creep_coefficient_ec2.json'
)

invalid_template_path = os.path.join(
    'tests',
    'test_cli',
    'creep_coefficient_ec2_INVALID.json'
)

evaluated_json_path = os.path.join(
    'tests',
    'test_cli',
    'creep_coefficient_ec2_evaluated.json'
)

verified_evaluated_template_path = os.path.join(
    'tests',
    'test_cli',
    'creep_coefficient_ec2_evaluated&checked.json'
)

with open(template_path, 'r') as file:
    enji_template = json.load(file)


with open(verified_evaluated_template_path, 'r') as file:
    verified_evaluated_template = json.load(file)


def test_verifier():
    try:
        command = 'python ' + verifier_path + ' ' + template_path
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError: 
        pytest.fail("Testing template cannot be verified")


def test_invalid_template():
    command = 'python ' + verifier_path + ' ' + invalid_template_path
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(command, shell=True, check=True)


def test_solver():
    if os.path.exists(evaluated_json_path): os.remove(evaluated_json_path) 

    try:
        command = 'python ' + solver_path + ' ' + template_path
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError: 
        pytest.fail("Testing template cannot be solved")

    with open(evaluated_json_path, 'r') as file:
        evaluated = json.load(file)
    
    if verified_evaluated_template != evaluated:
        pytest.fail("Evaluated files are not identical")
