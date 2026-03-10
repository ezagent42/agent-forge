import sys
import os

# Make agent_forge importable as a package from this directory
sys.path.insert(0, os.path.dirname(__file__))

# Map agent_forge to the current package directory
import importlib
import types

agent_forge = types.ModuleType("agent_forge")
agent_forge.__path__ = [os.path.dirname(__file__)]
sys.modules["agent_forge"] = agent_forge
