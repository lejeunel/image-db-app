#!/usr/bin/env python3
from urllib.parse import urlparse

import boto3
from aws_error_utils import get_aws_error_info
from botocore.client import ClientError as BotoClientError

from ..exceptions import DownloadException, ParsingException
from .base import BaseReader


def get_bucket_client():
    client = boto3.client("s3")

    return client


def get_pages(client, uri):
    uri = urlparse(uri)
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

        """
        uri = urlparse(uri)
        bucket = uri.netloc
        client = get_bucket_client()

        try:
            body = client.get_object(Bucket=bucket, Key=uri.path[1:])["Body"]
        except BotoClientError as e:
            e = get_aws_error_info(e)
            raise DownloadException(message=e.message, payload={'operation': e.operation_name})


        return body

    def list(self, uri) -> list[str]:

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
