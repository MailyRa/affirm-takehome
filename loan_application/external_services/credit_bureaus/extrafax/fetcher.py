import abc

from datetime import date
from dataclasses import MISSING
from typing import Union
from loan_application.models.addresses import Address


class RemoteFetcherBase(object):
    def __init__(
            self,
            full_name: str,
            date_of_birth: date,
            address: Address,
            ssn_last4: str,
            ssn: Union[str, MISSING.__class__] = MISSING
    ):
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.address = address
        self.ssn_last4 = ssn_last4
        self.ssn = ssn

    @abc.abstractmethod
    def pull_remote(self) -> str:
        """
        Abstract method for fetching a credit report. Returns the raw report
        XML, as a str.
        :return: str
        """
        raise NotImplementedError


class RemoteFetcherLive(RemoteFetcherBase):
    def pull_remote(self) -> str:
        raise NotImplementedError("""
        Live pulling is out of scope for this assignment! Please use the
        sandbox fetcher to build your solution.
        """)
