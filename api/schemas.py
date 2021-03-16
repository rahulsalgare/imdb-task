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