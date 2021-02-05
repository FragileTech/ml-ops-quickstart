import pytest


cli_input_defaults = (
    "test_project_name\n"  # Project name
    "my_test_description\n"  # Description
    "owner\n"  # project owner
    "owner@email.com\n"
    "\n"  # Authors, set to owner
    "\n"  # url default
    "\n"  # open source
    "\n"  # Mit license
    "Owner LTD\n"  # copyright owner
    "\n"  # Python versions
    "torch\n"  # requirements
    "\n"  # Workflow python
    "\n"  # default branch master
    "bot-account\n"  # bot
    "bot@email.com\n"  # bot email
    "\n"  # Default base docker image
    "\n"  # No ML Flow
    "\n"  # Init git repo
    "\n"  # No push
    "\n"  # Default commit message
    "y\n"  # Generate mloq.yml
    "\n"  # Overwrite files
)

cli_input_proprietary = (
    "test_project_name\n"  # Project name
    "my_test_description\n"  # Description
    "owner\n"  # project owner
    "owner@email.com\n"
    "\n"  # Authors, set to owner
    "\n"  # url default
    "n\n"  # open source
    "none\n"  # Mit license
    "Owner LTD\n"  # copyright owner
    "\n"  # Python versions
    "torch\n"  # requirements
    "\n"  # Workflow python
    "\n"  # default branch master
    "bot-account\n"  # bot
    "bot@email.com\n"  # bot email
    "\n"  # Default base docker image
    "\n"  # No ML Flow
    "n\n"  # Init git repo
    "y\n"  # Generate mloq.yml
    "\n"  # Overwrite files
)


@pytest.fixture(params=[cli_input_defaults, cli_input_proprietary], scope="module")
def cli_input(request):
    return request.param
