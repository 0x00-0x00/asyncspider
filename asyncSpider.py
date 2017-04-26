#!/usr/bin/env python3.6
#coding:utf-8
import argparse
import requests
import re
import asyncio
import aiohttp
import tqdm
import string
import random
import sys
import os
import shemutils.logger

logger = shemutils.logger.Logger("Spider")

def format_url(url):
    if not url.endswith("/"):
        return url + "/"
    return url

@asyncio.coroutine
def get(url, conn):
    response = yield from aiohttp.request('GET', url,  connector=conn)
    #return (yield from response.read())
    #return (yield from response.status)
    return response


def write_to_file(filename, content):
    with open(filename, "wb") as f:
        f.write(content)
    return 0


@asyncio.coroutine
def query_url(url, connector):
    #  Use the semaphore
    status_code = 0
    file_name = url.split("/")[-1:][0]  # get the filename
    with (yield from r_semaphore):
        resp = yield from asyncio.async(get(url, connector))
        status_code = resp.status
        content = yield from resp.read()

    if status_code == 200:
        #logger.info("Found: {0}".format(url))
        write_to_file(file_name, content)
    return status_code


@asyncio.coroutine
def progressbar(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        yield from f

class Spider(object):
    """
    Spider Object
    """
    def __init__(self, *args, **kwargs):
        self.args = args[0]
        self.url = format_url(self.args.url)
        self.wordlist = self.args.wordlist
        self.exclude = self.args.exclude
        self.tries = set()
        self.file_formats = [
            ".js",
            ".php",
            ".txt",
            ".html",
            ".xhtml",
            ".htm",
        ]
        self._check()
        self._exclude_ff()
        self._populate()

    def _check(self):
        if not os.path.exists(self.wordlist):
            return sys.exit(1)

    def _populate(self):
        with open(self.wordlist, "r") as f:
            for line in f.readlines():
                line = line.replace("\n","")
                for ff in self.file_formats:
                    self.tries.add(self.url + line + ff)  # add the link to a queue
        logger.info("Spider has generated {0} combinations.".format(len(self.tries)))
        return 0

    def _exclude_ff(self):
        """
        Format the excluded string into a list and then filter the obj ff list.
        """
        if self.exclude is None:
            return 0
        else:
            ffs = str(self.exclude).replace(" ", "")
            ffs = ["." + x for x in ffs.split(",")]
            for ff in ffs:
                self.file_formats.remove(ff)
                logger.info("Excluded file format: {0}".format(ff))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL to attack", required=True)
    parser.add_argument("-w", "--wordlist", help="Wordlist file to use for generate url names.", required=True)
    parser.add_argument("-e", "--exclude", help="File format(s) to exclude separated by comma", required=False)
    args = parser.parse_args()
    spid = Spider(args)
    #coroutines = [query_url(url.decode(), connector) for url in spid.tries]
    coroutines = [query_url(url, connector) for url in spid.tries]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(progressbar(coroutines))
    return 0


if __name__ == "__main__":
    r_semaphore = asyncio.Semaphore(3)     #  Maximum of 10 simultaneous downloads
    connector = aiohttp.TCPConnector(verify_ssl=False)
    main()

