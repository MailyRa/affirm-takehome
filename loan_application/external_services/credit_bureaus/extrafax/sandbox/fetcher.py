from dataclasses import MISSING
from datetime import date
from typing import Union
import os

from ..fetcher import RemoteFetcherBase

_FIXTURES_PATH = os.path.join(os.path.dirname(__file__), 'fixtures/')

class RemoteFetcherSandbox(RemoteFetcherBase):
    def pull_remote(self) -> Union[str, MISSING.__class__]:
        """
        Sandbox implementation for the ExTraFax bureau's credit report pulls.
        Looks up file-based fixtures defined in the fixtures/ directory.
        :return: str
        """
        return fixture_repo.lookup_fixture(self)


_FIXTURE_MAPPING = [
    ## Francis Fitzgerald, DOB 12/21/1940, SSN 987-65-1111, FICO 575:
    # can be used to test:
    #   1. name mismatch (Scott Fitzgerald hits but doesn't match report)
    #   2. SSN mismatch (987-65-1112 hits, but doesn't match report)
    (
        ("Scott Fitzgerald", date(1940, 12, 21), "1111"),
        "fscott.xml"),
    (
        ("Scott Fitzgerald", date(1940, 12, 21), "1112"),
        "fscott.xml"),
    (
        ("Francis Fitzgerald", date(1940, 12, 21), "1111"),
        "fscott.xml"),
    (
        ("Francis Fitzgerald", date(1940, 12, 21), "1112"),
        "fscott.xml"),
    (
        ("Scott Fitzgerald", date(1940, 12, 21), "987-65-1111"),
        "fscott.xml"),
    (
        ("Scott Fitzgerald", date(1940, 12, 21), "987-65-1112"),
        "fscott.xml"),
    (
        ("Francis Fitzgerald", date(1940, 12, 21), "987-65-1111"),
        "fscott.xml"),
    (
        ("Francis Fitzgerald", date(1940, 12, 21), "987-65-1112"),
        "fscott.xml"),

    ## Z Fitzgerald, DOB 3/10/1948, SSN 987-65-3333, FICO 794:
    # can be used to test:
    #   1. frozen credit report (report has a temporary freeze)
    (
        ("Z Fitzgerald", date(1948, 3, 10), "3333"),
        "zscott.xml"),
    (
        ("Z Fitzgerald", date(1948, 3, 10), "987-65-3333"),
        "zscott.xml"),

    ## E Hemingway, DOB 7/2/1961, SSN 987-65-2222, FICO 803:
    # can be used to test:
    #   1. No hit on SSN last 4 (customer must provide full SSN)
    (
        ("E Hemingway", date(1961, 7, 2), "987-65-2222"),
        "ehemingway.xml"),

]


class _FixtureRepo(object):
    def __init__(self):
        self._storage = {}
        self._default_key = MISSING

    def lookup_fixture(
            self,
            fetcher: RemoteFetcherSandbox
    ) -> Union[str, MISSING.__class__]:
        # if full SSN has been provided, use it for the lookup
        if fetcher.ssn is not MISSING:
            ssn = fetcher.ssn
        else:
            ssn = fetcher.ssn_last4
        params = (
            fetcher.full_name,
            fetcher.date_of_birth,
            ssn
        )
        return self._storage.get(params, self._storage[self._default_key])

    @staticmethod
    def _load_fixture_by_name(filename):
        with open(os.path.join(_FIXTURES_PATH, filename), 'r') as f:
            return f.read()

    def load_fixtures(self):
        """
        Load mocked ExTraFax fixtures from the fixtures/ directory. This should
        be run at process startup.
        :return:
        """
        # default to no hit fixture
        self._storage[self._default_key] = \
            self._load_fixture_by_name('nohit.xml')

        # load and index mocks
        for params, filename in _FIXTURE_MAPPING:
            self._storage[params] = self._load_fixture_by_name(filename)

fixture_repo = _FixtureRepo()

__all__ = (
    'RemoteFetcherSandbox',
    'fixture_repo'
)
