import tempfile

from omegaconf import DictConfig

from mloq.workflows import setup_push_workflow, setup_workflow_template


def test_setup_workflow_template(ledger):
    # test empty workflow
    with tempfile.TemporaryDirectory() as tmp:
        setup_workflow_template(
            root_path=tmp,
            config=DictConfig({"project": {}, "template": {}}),
            ledger=ledger,
        )
    # Test invalid name workflow
    setup_workflow_template(
        root_path=tmp,
        config=DictConfig({"project": dict(ci="miau_db"), "template": {}}),
        ledger=ledger,
    )


def test_setup_push_workflow(ledger):
    assert (
        setup_push_workflow(
            None,
            config=DictConfig({"project": {}, "template": {}}),
            ledger=ledger,
            overwrite=False,
        )
        is None
    )
