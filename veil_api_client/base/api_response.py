# -*- coding: utf-8 -*-
"""Veil api response."""
import logging

logger = logging.getLogger('veil-api-client.response')
logger.addHandler(logging.NullHandler())


class VeilApiResponse:
    """VeiL api response object.

    Attributes:
        status_code: http response status code.
        data: response json dictionary.
        headers: response headers.

    Properties:
        paginator_results: value of results key from response data. May presents only in list() queries.
    """

    __SUCCESS_STATUSES = frozenset((200, 201, 202, 204))

    def __init__(self, status_code, data, headers, api_object) -> None:
        """Please see help(VeilApiResponse) for more info."""
        self.status_code = status_code
        self.data = data
        self.headers = headers
        self.__api_object = api_object
        if status_code not in (200, 202):
            logger.warning('request status code is %s', status_code)
        logger.debug('response data: %s', data)

    @property
    def paginator_results(self) -> list:
        """Value of results key from response data. May presents only in list() queries."""
        # Эксперементальный блок - нет уверенности, что у VeiL все ответы такие.
        if self.status_code != 200 or not isinstance(self.data, dict) or 'results' not in self.data.keys():
            return list()
        else:
            return self.data['results']

    @property
    def value(self) -> dict:
        """Value of single-count entity from response data. May present in info() query."""
        # Эксперементальный блок - нет уверенности, что у VeiL все ответы такие.
        if self.status_code != 200 or not isinstance(self.data, dict):
            return dict()
        else:
            return self.data

    @property
    def response(self) -> list:
        """List with calling VeilApiObject entities instances.

        1. Determine calling VeilApiObject instance to copy.
        2. Determine response type (paginator or info).
        3. Return list with 1-M elements.
        :return:
        """
        api_object_list = list()
        if self.__api_object:
            if self.paginator_results:
                for result in self.paginator_results:
                    inst = self.__api_object.copy()
                    inst.update_public_attrs(result)
                    api_object_list.append(inst)
            else:
                inst = self.__api_object.copy()
                inst.update_public_attrs(self.value)
                api_object_list.append(inst)
        return api_object_list

    @property
    def task(self):
        """Return VeilTask if response is 202."""
        # TODO: Task in return annotation
        if self.status_code != 202 or not isinstance(self.data, dict) or not self.data.get('_task'):
            return
        task_inst = self.__api_object.task
        task_inst.update_public_attrs(self.data['_task'])
        return task_inst

    @property
    def success(self) -> bool:
        """Determine that requests response goes well."""
        return self.status_code in self.__SUCCESS_STATUSES
