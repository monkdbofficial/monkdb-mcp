import sys
from unittest.mock import MagicMock

# Mock monkdb module so unit tests don't require real MonkDB SDK
sys.modules["monkdb"] = MagicMock()
sys.modules["monkdb.client"] = MagicMock()
