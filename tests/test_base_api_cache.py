# -*- coding: utf-8 -*-
"""Base cache test cases."""

import pytest

from veil_api_client import VeilCacheAbstractClient, VeilCacheConfiguration

pytestmark = [pytest.mark.base]


class TestVeilCache:
    """VeilCacheAbstractClient test cases."""

    def test_abstract_desc(self):
        """Veil rest paginator init test case."""
        try:
            class BadDesc(VeilCacheAbstractClient):
                pass
            BadDesc()
        except TypeError:
            assert True
        else:
            raise AssertionError()

        class GoodDesc(VeilCacheAbstractClient):
            async def get_from_cache(self):
                pass
        GoodDesc()
        assert True


class TestVeilCacheConfiguration:
    """VeilCacheConfiguration test cases."""

    class GoodDesc(VeilCacheAbstractClient):
        """Good user cache."""

        async def get_from_cache(self, *args, **kwargs):
            """Return value from a cache."""
            return 'YES'

    def test_init(self):
        """Constructor test scenario."""
        try:
            VeilCacheConfiguration(cache_client=1, ttl=5)
        except TypeError:
            assert True
        else:
            raise AssertionError()

        VeilCacheConfiguration(cache_client=self.GoodDesc(), ttl=1)
        assert True

    @pytest.mark.asyncio
    async def test_get_from_cache(self):
        """Get value from a cache scenario."""

        async def simple_cor():
            pass

        good_cache = VeilCacheConfiguration(cache_client=self.GoodDesc(), ttl=1)
        assert True
        from_cache = await good_cache.get_from_cache(simple_cor,
                                                     'client',
                                                     'get',
                                                     'url',
                                                     'headers',
                                                     'params',
                                                     'ssl')
        assert from_cache == 'YES'

    @pytest.mark.asyncio
    async def test_disabled_cache(self):
        """Disabled cache scenario."""
        cache = VeilCacheConfiguration(cache_client=self.GoodDesc(), ttl=0)
        assert True

        async def simple_cor(*args, **kwargs):
            return 'simple_cor'

        no_cache = await cache.get_from_cache(simple_cor,
                                              'client',
                                              'get',
                                              'url',
                                              'headers',
                                              'params',
                                              'ssl')
        assert no_cache == 'simple_cor'

    @pytest.mark.asyncio
    async def test_no_cor(self):
        """Bad VeilCacheConfiguration scenario."""
        cache = VeilCacheConfiguration(cache_client=self.GoodDesc(), ttl=0)
        assert True

        def simple_func():
            return 'simple_func'

        try:
            await cache.get_from_cache(simple_func,
                                       'client',
                                       'get',
                                       'url',
                                       'headers',
                                       'params',
                                       'ssl')
        except NotImplementedError:
            assert True
        else:
            raise AssertionError()
