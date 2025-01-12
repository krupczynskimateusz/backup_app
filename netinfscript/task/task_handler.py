#!/usr/bin/env python3.10
import logging
import sys
from os import cpu_count
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait
from netinfscript.devices.base_device import BaseDevice
from netinfscript.task.backup_task import BackupTask
from netinfscript.agent.devices_load import Devices_Load


class Multithreading:
    def __init__(self, _thread_num: int = None) -> None:
        """
        An object that is responsible for dividing a task
        into many threads.

        :param threading: bool split the task into multiple threads,
        :param _thread_num: int maximum number of threads.
                          defualt = cpu threads * 2
        :return: None
        """
        if _thread_num is None:
            self._thread_num = cpu_count() * 2
        else:
            self._thread_num = _thread_num

    def _threading(self, *args, **kwargs) -> None:
        """
        The function splits the task into multiple threads

        :return: None
        """
        with ThreadPoolExecutor(max_workers=self._thread_num) as executor:
            wait(
                [
                    executor.submit(self.func, i, *args, **kwargs)
                    for i in self.lst
                ]
            )

    def execute(self, func: callable, lst: list, *args, **kwargs) -> None:
        """
        The function begins the process of splitting
        the received function into multiple threads.

        :param func: function to perform
        :param lst: List of objects on which
                    the sent function is to be executed.
        :return: None
        """
        self.func = func
        self.lst: list = lst
        self._threading(*args, **kwargs)


class TaskHandler:
    """
    An object respnsible for manage tasks.
    """

    def __init__(self, devices_config_file: Path) -> None:
        self.logger: logging = logging.getLogger(f"netinfscript.TaskHandler")
        self._devices_config_file: Path = devices_config_file
        self._created_devices_list = []
        self._exe_func = None

    @property
    def exe_func(self) -> str:
        """Get the task that need to be executed."""
        return self._exe_func

    @exe_func.setter
    def exe_func(self, task: str) -> None:
        """Set the task that need to be executed."""
        self._exe_func = task

    @property
    def devices_config_file(self) -> Path:
        """Get the agent object."""
        return self._devices_config_file

    @property
    def devices_config_file(self) -> Path:
        """Get the agent object."""
        return self._devices_config_file

    def task_handler(self) -> None:
        """
        Fuction that will optmalize execution of code with
        multithreading. Also is resposible for load devices from file.
        """
        self.logger.debug(f"Trying load devices from database.")
        try:
            self.device_database_load()
            ### send tuple for some reason
            for ip in self.devices_loaded.devices_data.items():
                _dev_obj = self.devices_loaded.create_devices(ip)
                self._created_devices_list.append(_dev_obj)
        except Exception as e:
            self.logger.error(f"Can't load devices from database.")
            sys.exit(10)
        try:
            self.logger.debug("Trying creat object for multithreading.")
            self.tasks = Multithreading()
            self.execute_with_threading()
        except Exception as e:
            self.logger.error(
                "Can't create multihreading object, executing without it."
            )
            self.execute_without_threading()

    def device_database_load(self) -> None:
        self.devices_loaded = Devices_Load(self.devices_config_file)

    def execute_with_threading(self) -> None:
        """The function that will execute task with multithreading."""
        if self.exe_func == "backup":
            self.logger.debug("Execut task with multithreading.")
            self.tasks.execute(self.backup_ssh, self._created_devices_list)

    def execute_without_threading(self) -> None:
        """The function that will execute task without multithreading."""
        if self.exe_func == "backup":
            self.logger.debug("Execut task.")
            for device in self._created_devices_list:
                self.backup_ssh(device)

    def backup_ssh(self, dev: BaseDevice) -> None:
        """The function that execute backup task."""
        self.logger.debug("Execut backup task.")
        backup = BackupTask(dev)
        backup.make_backup()


if __name__ == "__main__":
    pass