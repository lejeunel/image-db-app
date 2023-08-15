#!/usr/bin/env python3
import re
import boto3
from urllib.parse import urlparse
from pathlib import PurePosixPath
from .base import BaseReader
from ..exceptions import ParsingException
import numpy as np
from PIL import Image
from botocore.client import ClientError as BotoClientError
from aws_error_utils import get_aws_error_info


def get_bucket_client():
    client = boto3.client("s3")

    return client


def get_pages(client, uri):
    uri = urlparse(uri)
    path = uri.path
    paginator = client.get_paginator("list_objects_v2")

    pages = paginator.paginate(Bucket=uri.netloc, Prefix=uri.path, Delimiter="/")

    return pages


class S3Reader(BaseReader):
    """
    Class that lists and reads image files on S3
    """

    def __init__(self):
        self.client = get_bucket_client()

    def __call__(self, uri) -> bytes:
        """
        Return bytes from bucket

        TODO throw and re-raise boto ClientError as ReaderException
        """
        uri = urlparse(uri)
        bucket = uri.netloc
        client = get_bucket_client()

        body = client.get_object(Bucket=bucket, Key=uri.path[1:])["Body"]

        return body

    def list(self, uri) -> list[str]:
        if uri[-1] != "/":
            return uri

        try:
            pages = get_pages(self.client, uri)

            # gather all items at location excluding children nodes ("directories")
            items = []
            for p in pages:
                if "Contents" in p.keys():
                    for o in p["Contents"]:
                        f = o["Key"]
                        items.append(uri)
        except BotoClientError as e:
            e = get_aws_error_info(e)
            raise ParsingException(message=e.message, payload={'operation': e.operation_name})

        return items
