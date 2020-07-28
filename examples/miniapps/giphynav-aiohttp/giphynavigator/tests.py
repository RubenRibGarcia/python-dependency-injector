"""Tests module."""

from unittest import mock

import pytest

from giphynavigator.application import create_app
from giphynavigator.giphy import GiphyClient


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app, aiohttp_client, loop):
    return loop.run_until_complete(aiohttp_client(app))


async def test_index(client, app):
    giphy_client_mock = mock.AsyncMock(spec=GiphyClient)
    giphy_client_mock.search.return_value = {
        'data': [
            {'url': 'https://giphy/gif1.gif'},
            {'url': 'https://giphy/gif2.gif'},
        ],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get(
            '/',
            params={
                'query': 'test',
                'limit': 10,
            },
        )

    assert response.status == 200
    data = await response.json()
    assert data == {
        'query': 'test',
        'limit': 10,
        'gifs': [
            {'url': 'https://giphy/gif1.gif'},
            {'url': 'https://giphy/gif2.gif'},
        ],
    }


async def test_index_no_data(client, app):
    giphy_client_mock = mock.AsyncMock(spec=GiphyClient)
    giphy_client_mock.search.return_value = {
        'data': [],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get('/')

    assert response.status == 200
    data = await response.json()
    assert data['gifs'] == []


async def test_index_default_params(client, app):
    giphy_client_mock = mock.AsyncMock(spec=GiphyClient)
    giphy_client_mock.search.return_value = {
        'data': [],
    }

    with app.container.giphy_client.override(giphy_client_mock):
        response = await client.get('/')

    assert response.status == 200
    data = await response.json()
    assert data['query'] == app.container.config.search.default_query()
    assert data['limit'] == app.container.config.search.default_limit()
