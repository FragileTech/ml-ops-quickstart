import tempfile

from mloq.workflows import setup_push_workflow, setup_workflow_template


def test_setup_workflow_template():
    # test empty workflow
    with tempfile.TemporaryDirectory() as tmp:
        setup_workflow_template(root_path=tmp, project_config=dict(), template=dict())
    # Test invalid name workflow
    setup_workflow_template(root_path=tmp, project_config=dict(ci="miau_db"), template=dict())


def test_setup_push_workflow():
    assert setup_push_workflow(None, project_config={}, template={}, override=False) is None
