import importlib
import os
import uuid
from types import ModuleType
from typing import Optional

import pytest

current_path = os.path.dirname(os.path.abspath(__file__))
package = os.path.dirname(os.path.relpath(__file__)).replace("/", ".")


@pytest.fixture
def load_generated_code():
    def _inner(code_text: str, module_name: Optional[str] = None) -> ModuleType:
        """method saves & returns new generated python module
        code_text - code to be saved in new module
        module_name: str - name of the module to use for saving the code
        """
        if not module_name:
            module_name = f"module_{uuid.uuid1()}"

        with open(os.path.join(current_path, f"{module_name}.py"), "w+") as f:
            f.write(code_text)

        module = importlib.import_module(f"{package}.{module_name}")

        return module

    yield _inner
