#!/usr/bin/env python3
import logging
from modules.config_load import Config_Load
from modules.devices import Devices_Load, Device
from modules.connections import SSH_Connection
from modules.git_operations import Git
import subprocess
from pathlib import Path



CONFIG_LOADED = Config_Load()
LOGGER = CONFIG_LOADED.set_logging()



class Backup():


    def __init__(self) -> None:
        self.logger = logging.getLogger("backup_app.Backup")
        self.devices = Devices_Load()
        self.devices.load_jsons(CONFIG_LOADED.devices_path)
        self.devices.create_devices()
        self.configs_path = CONFIG_LOADED.configs_path


    def _file_working(self, ip, name, stdout):
        try:
            dir_path = f"{self.configs_path}/{name}_{ip}"
            file_path = f"{self.configs_path}/{name}_{ip}/{ip}_conf.txt"

            path = Path(dir_path)

            self.logger.debug(f"{ip} - Check if the folder exist.")

            if not path.is_dir():
                self.logger.info(
                    f"{self.devices.ip} - The folder doesn't exist or account doesn't have permissions."
                    )
                self.logger.info(f"{ip} - Creating a folder.")
                path.mkdir()

            try:
                self.logger.debug(f"{ip} - Opening the file.")
                with open(file_path, "w") as f:
                    self.logger.debug(f"{ip} - Writing config.")
                    f.writelines(stdout)
                return True

            except PermissionError:
                self.logger.warning(f"{ip} - The file cannot be opened. Permission error.")
                return False

        except Exception as e:
            self.logger.error(f"{ip} - Error: {e}")
            pass


    def execute_backup(self):
        for dev in Device.devices_lst:
            self.logger.info(f"{dev.ip} - Start creating backup.")
            ssh = SSH_Connection(dev)
            stdout = ssh.get_config()

            if isinstance(stdout, str):
                self.logger.debug(f"{dev.ip} - Writing config to the file.")
                done = self._file_working(dev.ip, dev.name, stdout)

                if done:
                    self.logger.debug(f"{dev.ip} - Git commands execute.")
                    _git = Git(dev.ip, dev.name, self.configs_path)
                    done = _git.git_exceute()

                    if not done:
                        self.logger.warning(f"{dev.ip} - Unable to create backup.")
                        pass

                else:
                    self.logger.warning(f"{dev.ip} - Unable to create backup.")
                    pass

            else:
                self.logger.warning(f"{dev.ip} - Unable to connect to device.")
                pass



def backup_execute():

    data = Backup()
    data.execute_backup()

    return True


if __name__ == "__main__":
    pass