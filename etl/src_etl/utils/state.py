import abc
import json
import os
from typing import Any


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str) -> None:
        self.file_path = f"state/{file_path}"

    def save_state(self, state: dict[str, Any]) -> None:
        with open(self.file_path, "w") as f:
            json.dump(state, f)

    def retrieve_state(self) -> dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}


class State:
    def __init__(self, storage: BaseStorage, state_key: str) -> None:
        self.storage = storage
        self.state_key = state_key
        self.state = self.storage.retrieve_state()

    def set_state(self, key: str, value: str) -> None:
        self.state[key] = value
        self.storage.save_state(self.state)

    def get_state(self, key: str) -> str:
        return self.state.get(key, "1970-01-01 00:00:00.000000+00")
