import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values as dotenvValues


# =================================================================================================================== #

@dataclass
class EnvHelper:
    env_dir: Optional[str] = None
    env_file: Optional[str] = None


    def __post_init__(self):
        self.env_dir = self.env_dir or Path(__file__).parent.parent
        self.env_file = self.env_file or '.env'
        self.env_path = self._get_env_path()
        self.env_dict = dotenvValues(self.env_path)
        self.workspace = self.env_dict['WORKSPACE_DIR']
        self.pythonpath = self.env_dict['PYTHONPATH']
        self.gcp_app_creds = self.env_dict['GOOGLE_APPLICATION_CREDENTIALS']
        self.gcp_project = self.env_dict['GCP_PROJECT']
        self.gcp_bucket = self.env_dict['GCP_BUCKET']


    def _get_env_path(self) -> str:
        _path = os.path.join(self.env_dir, self.env_file)
        if Path(_path).is_file():
            return _path
        else:
            raise FileNotFoundError(f'Environment file {_path} not found.')


    def get_env_value(self, env_var: str) -> str:
        _key = env_var.upper().strip()
        if _key not in self.env_dict:
            _abr_path = os.path.join('~', os.path.basename(self.env_dir), self.env_file)
            raise KeyError(f'Environment variable {_key} not found in {_abr_path}.')
        return self.env_dict[_key]


# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
