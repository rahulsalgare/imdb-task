import unittest

import requests


class ApiTest(unittest.TestCase):
    API_URL = 'http://127.0.0.1:5000'
    user = 'user'
    password = 'user'
    token = ''
    movie_id = 0

    genre_obj = {
        "genres": ["Fantasy"]
    }

    movie_obj = {
        "name": "test_movie",
        "director": "test_director",
        "genres": [
            "Fantasy"
        ]
    }

    patch_movie = {
        "name": "test_movie",
        "director": "changed"
    }

    def test_1_get_movies(self):
        r = requests.get(ApiTest.API_URL + '/movies')
        self.assertEqual(r.status_code, 200)
        assert 'movies' in r.json()
        assert type(r.json()['movies']) is list

    def test_2_get_movie(self):
        id = 1
        r = requests.get(ApiTest.API_URL + '/movies/' + str(id))
        self.assertEqual(r.status_code, 200)

    def test_3_login(self):
        r = requests.get(ApiTest.API_URL + '/login', auth=(ApiTest.user, ApiTest.password))
        self.assertEqual(r.status_code, 200)
        assert 'token' in r.json()
        ApiTest.token = r.json()['token']

    def test_4_add_genre(self):
        r = requests.post(ApiTest.API_URL + '/add_genres', json=ApiTest.genre_obj,
                          headers={'x-access-token': ApiTest.token})
        assert r.status_code == 200 or r.status_code == 201

    def test_5_add_movie(self):
        r = requests.post(ApiTest.API_URL + '/movies', json=ApiTest.movie_obj,
                          headers={'x-access-token': ApiTest.token})
        self.assertEqual(r.status_code, 201)
        ApiTest.movie_id = r.json()['movie']['id']

    def test_6_patch_movie(self):
        id = ApiTest.movie_id
        r = requests.patch(ApiTest.API_URL + '/movies/update/' + str(id), data=ApiTest.patch_movie,
                           headers={'x-access-token': ApiTest.token})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ApiTest.patch_movie['name'], r.json()['movie']['name'])
        self.assertEqual(ApiTest.patch_movie['director'], r.json()['movie']['director'])

    def test_7_delete_movie(self):
        id = ApiTest.movie_id
        r = requests.delete(ApiTest.API_URL + 'movies/delete/' + str(id), headers={'x-access-token': ApiTest.token})
        self.assertEqual(r.status_code, 204)


if __name__ == '__main__':
    unittest.main()
