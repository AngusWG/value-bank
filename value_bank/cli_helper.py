#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2021/10/20 14:40
# @author  : zza
# @Email   : 740713651@qq.com
# @File    : content.py
import os
from getpass import getpass

from value_bank.config import Config
from value_bank.core import Bank


class CliHelper:
    """value_bank is use to store/get value by keys to your clipboard"""

    _config_file: str = os.path.join(os.path.expanduser("~"), ".v_bank.json")
    _store_file: str = os.path.join(os.path.expanduser("~"), ".v_bank_store.json")

    def __init__(self):
        self._conf = Config.read(self._config_file)
        if self._conf.use_password:
            print("input your v_bank pin:")
            self._password = str(getpass())
        else:
            self._password = None
        self._conf.download_to_file(self._store_file)
        self._bank: Bank = Bank.read(self._store_file, self._password)

    def __del__(self):
        store_context = self._bank.store(self._store_file, self._password)
        self._conf.update_to_gist(store_context)
        self._conf.store(self._config_file)

    def __call__(self, *args: str, force: bool = False):
        """
        Examples:
        set: > vbank ubuntu root 123456
             V(main_key=root, value=123456, ex_keys=['ubuntu'])
        get: > vbank ubuntu
             V(main_key=root, value=123456, ex_keys=['ubuntu'])
             # your clipboard is root
        get: > vbank root
             V(main_key=root, value=123456, ex_keys=['ubuntu'])
             # your clipboard is 123456
        """
        if len(args) == 1:
            key = args[0]
            return self._bank.get(key)

        return self._bank.set_key(args, force)

    def gist(self, token: str = None) -> str:
        """
        vbank gist token aaabbbcc

        Args:
            token: from https://github.com/settings/tokens

        Returns:
            gist_url
        """
        if token is None:
            return "make gist token at url: https://github.com/settings/tokens"
        self._conf.gist_token = token

    def pin(self, password: str = None):
        self._password = str(password)
        self._conf.use_password = True

    def clean(self):
        self._bank.clean()

    def find(self, key: str):
        """
        find:> vbank find ubuntu
            V(main_key=root, value=111111, ex_keys=['win'])
            V(main_key=root, value=123123, ex_keys=['centos'])

        Args:
            key:

        Returns:

        """
        self._bank.find(key)

    def rm(self, key: str, force: bool = False):
        """delete: > vbank rm ubuntu # or vbank rm root
        > Are you sure to delete V(main_key=root, value=123456, ex_keys=['ubuntu'])? (y/n) y

        Args:
            key:
            force:

        Returns:

        """
        return self._bank.delete(key, force=force)

    def version(self) -> str:
        """显示当前版本"""
        import value_bank

        return value_bank.__version__

    def get(self, key: str):
        return self._bank.get(key)

    def set(self, key, *args, force: bool = False):
        self._bank.set_key([key, *args], force)