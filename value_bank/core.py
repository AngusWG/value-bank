import datetime
import os
from typing import Dict, List, Optional, Tuple, Union

from prompt_toolkit.clipboard import pyperclip
from pydantic import BaseModel

# config_file = os.path.join(os.path.expanduser("~"), r".v_bank.config")
store_file = os.path.join(os.path.expanduser("~"), ".v_bank_store.json")


class V(BaseModel):
    main_key: str
    value: str
    keys: List[str] = []
    _id: datetime.datetime = datetime.datetime.now()

    def __repr__(self):
        return f"V(main_key={self.main_key}, value={self.value}, ex_keys={self.keys})"

    def __str__(self):
        return repr(self)


class Bank(BaseModel):
    v_set: List[V] = list()
    keys: Dict[str, V] = dict()
    last: Optional[V] = None

    def store(self) -> str:
        with open(store_file, "w+", encoding="utf-8") as f:
            f.write(self.json(indent=4))
        return store_file

    @classmethod
    def read(cls) -> "Bank":
        if os.path.exists(store_file):
            return cls.parse_file(store_file)
        else:
            return cls()

    def set_key(self, fields: Tuple[str, ...], force: bool = False) -> Union[str, V]:
        if len(fields) == 2:
            main_key, value = fields
            key = None
        elif len(fields) == 3:
            key, main_key, value = fields
        else:  # fields > 3 or fields < 2:
            return "Error: invalid number of fields"

        if key in self.keys:
            self._delete_v(self.keys[key], force=force)

        account = V(main_key=main_key, value=value)
        self.v_set.append(account)

        if key:
            self.keys[key] = account
            account.keys.append(key)
            return account
        return account

    def get(self, key: str) -> Optional[V]:
        if self.last and key == self.last.main_key:
            pyperclip.pyperclip.copy(self.last.value)
            return self.last
        if key in self.keys:
            stuff = self.keys[key]
            pyperclip.pyperclip.copy(stuff.main_key)
            self.last = stuff
            return stuff
        else:
            for stuff in self.v_set:
                if key == stuff.main_key:
                    pyperclip.pyperclip.copy(stuff.value)
                    self.last = stuff
                    return stuff
        return None

    def find(self, key: str) -> List[V]:
        res = []
        for _key in self.keys:
            if key in _key:
                res.append(self.keys[_key])
        for account in self.v_set:
            if key in account.main_key or key in account.value:
                res.append(account)
        return res

    def delete(self, key: str, force: bool = False) -> str:
        if key in self.keys:
            self._delete_v(self.keys[key], force)
            return "delete"
        else:
            for stuff in self.v_set:
                if key == stuff.main_key or key in stuff.value:
                    self._delete_v(stuff, force)
            return "delete"

    def _delete_v(self, stuff: V, force: bool = False) -> bool:
        if force or input(f"Are you sure to delete {stuff}? (y/n) ") == "y":
            self.v_set.remove(stuff)
            for key in stuff.keys:
                del self.keys[key]
                self.last = None
                return True
        return False

    def clean(self, force: bool = False) -> str:
        if force or input("Are you sure to clean value-bank ? (y/n) ") == "y":
            self.v_set.clear()
            self.keys.clear()
            self.last = None
            with open(store_file, "w+", encoding="utf-8") as f:
                f.write("{}")
        return store_file

