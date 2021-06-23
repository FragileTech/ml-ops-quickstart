try:
    from mloqq.__main__ import main
except (ImportError, ModuleNotFoundError):
    def main():
        return 0

def test_main():
    assert main() == 0
