import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from google.cloud.bigquery import Client, QueryJobConfig
from google.cloud.bigquery.dataset import DatasetReference
from google.cloud.bigquery.table import RangePartitioning, TableReference, TimePartitioning
from google.cloud.storage import Client
from pandas import DataFrame

import helpers.toad_utils as ToadUtils
from helpers.enum_factory import CreateDisposition, Priority, WriteDisposition
from helpers.environment_helper import EnvHelper


# =================================================================================================================== #

def get_dataset_ref(
        project: str,
        dataset: Union[str, DatasetReference]
) -> DatasetReference:
    """Gets google DatasetReference object.

    Function accepts DatasetReference object because the output is used where a
         DatasetReference type is required, but the input is uncertain.

    Parameters
    ----------
    project : str
        Project name.
    dataset : Union[str, DatasetReference]
        Dataset name or reference object.

    Returns
    -------
        dataset_ref : DatasetReference
            google.cloud.bigquery_utils.dataset.DatasetReference
    """
    if isinstance(dataset, str):
        return DatasetReference(project, dataset)
    else:
        return dataset


def get_table_ref(
        dataset: Union[str, DatasetReference],
        table: str,
        project: Optional[str]
) -> TableReference:
    """
    Gets google TableReference object.

    Parameters
    ----------
    dataset : str or DatasetReference
        Dataset name or reference object -> see get_dataset_ref().
    table : str
        Table name.
    project : str, optional
        Project name.

    Returns
    -------
    table_ref : TableReference
        google.cloud.bigquery_utils.table.TableReference
    """
    if isinstance(dataset, str):
        if project is not None:
            dataset = get_dataset_ref(project, dataset)
        else:
            raise ValueError(f'Project parameter is required if dataset provided as string.')

    return TableReference(dataset, table)

# =================================================================================================================== #

@dataclass
class DownloadBlob:
    filename: str
    gcs_dir: Optional[str] = None
    project: Optional[str] = None
    bucket: Optional[str] = None


    def __post_init__(self):
        self.project = self.project or EnvHelper().gcp_project
        self.bucket = self.bucket or EnvHelper().gcp_bucket
        self.gcs_filepath = self.get_gcs_filepath()
        self.client = Client(
                project=self.project,
                # credentials=BqUtils.get_application_credentials()
        )

    def get_gcs_filepath(self) -> str:
        if self.gcs_dir is None:
            return self.filename
        else:
            return os.path.join(self.gcs_dir, self.filename)

    def download(self) -> str:
        _bucket = self.client.bucket(self.bucket)
        _blob = _bucket.blob(self.gcs_filepath)
        return str(_blob.download_as_bytes(), 'UTF-8')

# =================================================================================================================== #

@dataclass
class QueryJob:
    query: str
    dataset: str
    table: str
    project: Optional[str] = None
    job_id_prefix: Optional[str] = None
    timeout: Optional[float] = None
    allow_large_results: Optional[bool] = None
    create_disposition: Optional[CreateDisposition] = None
    dry_run: Optional[bool] = None
    flatten_results: Optional[bool] = None
    labels: Optional[dict] = None
    priority: Optional[Priority] = None
    range_partitioning: Optional[RangePartitioning] = None
    time_partitioning: Optional[TimePartitioning] = None
    use_legacy_sql: Optional[bool] = None
    use_query_cache: Optional[bool] = None
    write_disposition: Optional[WriteDisposition] = None


    def __post_init__(self):
        # self.client = Client(credentials=BqUtils.get_application_credentials())
        self.client = Client()
        self.project = self.project or EnvHelper().gcp_project
        self.table_ref = self.get_table_ref()
        self.query_job_config = self.get_job_config()

    def get_table_ref(self) -> TableReference:
        return get_table_ref(
                dataset=self.dataset,
                table=self.table,
                project=self.project
        )

    def get_job_config(self) -> QueryJobConfig:
        param_dict = {
                'allow_large_results': self.allow_large_results,
                'create_disposition' : self.create_disposition.value if self.create_disposition is not None else None,
                'dry_run'            : self.dry_run,
                'flatten_results'    : self.flatten_results,
                'labels'             : self.labels,
                'priority'           : self.priority.value if self.priority is not None else None,
                'range_partitioning' : self.range_partitioning,
                'time_partitioning'  : self.time_partitioning,
                'use_legacy_sql'     : self.use_legacy_sql,
                'use_query_cache'    : self.use_query_cache,
                'write_disposition'  : self.write_disposition.value if self.write_disposition is not None else None
        }

        params = ToadUtils.drop_none_val_from_dict(param_dict)
        return QueryJobConfig(**params)


    def run_query(self) -> list:
        param_dict = {
                'query'        : self.query,
                'job_config'   : self.query_job_config,
                'job_id_prefix': self.job_id_prefix,
                'timeout'      : self.timeout
        }

        params = ToadUtils.drop_none_val_from_dict(param_dict)
        query = self.client.query(**params)

        df = query.result().to_dataframe()
        df2 = df.to_json(orient='records')
        return json.loads(df2)

# =================================================================================================================== #

@dataclass
class UploadBlob:
    filename: str
    gcs_dir: Optional[str] = None
    project: Optional[str] = None
    bucket: Optional[str] = None

    def __post_init__(self):
        self.project = self.project or EnvHelper().gcp_project
        self.bucket = self.bucket or EnvHelper().gcp_bucket
        self.gcs_filepath = self.get_gcs_filepath()
        self.client = Client(
                project=self.project,
                # credentials=BqUtils.get_application_credentials()
        )

    def get_gcs_filepath(self) -> str:
        if self.gcs_dir is None:
            return self.filename
        else:
            return os.path.join(self.gcs_dir, self.filename)

    def get_source_filepath(self, source_dir: str) -> str:
        _root_dir = Path(__file__).parent.parent.parent.parent.parent

        if Path(source_dir).is_dir():
            _filepath = os.path.join(source_dir, self.filename)
        elif Path(os.path.join(_root_dir, source_dir)).is_dir():
            _filepath = os.path.join(_root_dir, source_dir, self.filename)
        else:
            raise FileNotFoundError(f'Unable to locate source directory: {source_dir}')

        if Path(_filepath).is_file():
            return _filepath
        else:
            raise FileNotFoundError(f'{self.filename} not found in ~/{source_dir}')

    def get_blob(self):
        _bucket = self.client.bucket(self.bucket)
        return _bucket.blob(self.gcs_filepath)

    def upload_from_dataframe(self, dataframe: DataFrame) -> bool:
        _blob = self.get_blob()
        csv = dataframe.to_csv(index=False)
        _blob.upload_from_string(
              data=csv,
              content_type='text/csv'
        )
        return _blob.exists()

    def upload_from_filename(self, source_dir: str) -> bool:
        _blob = self.get_blob()
        _blob.upload_from_filename(self.get_source_filepath(source_dir))
        return _blob.exists()

    def upload_from_string(self, data: str) -> bool:
        _blob = self.get_blob()
        _blob.upload_from_string(str(data))
        return _blob.exists()


# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
