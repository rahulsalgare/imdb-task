movie_schema = {
    "name": {
        "type": "string"
    },
    "director": {
        "type": "string"
    },
    "genres": {
        "type": "list",
        "schema": {
            "type": "string"
        }
    }
}

user_schema = {
    "name": {
        "type": "string"
    },
    "password": {
        "type": "string"
    }
}

genres_schema = {
    "genres": {
        "type": "list",
        "schema": {
            "type": "string"
        }
    }
}

review_schema = {
    "movie_id": {
        "type": "integer"
    },
    "rating": {
        "type": "integer",
        "min": 1,
        "max": 10
    },
    "comment": {
        "type": "string"
    }
}
