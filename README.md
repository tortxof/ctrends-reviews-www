# ctrends-reviews-www

## A flask app for managing reviews.

The puropse of this app is to receive anonymous reviews, provide an admin
interface for managing the reviews, and serving public json data of approved
reviews.

### Setup

Clone the repo on the server you are hosting from.

    git clone sol.djones.co:/srv/software/git/ctrends-reviews-www.git
    cd ctrends-reviews-www

Build the docker image.

    docker build -t local/ctrends-reviews .

Run the image.

    docker run -d --restart always --name ctrends-reviews -p 8009:5000 -v $(pwd):/app local/ctrends-reviews

A couple of files will be created.

- reviews.db

    This is the sqlite3 database. You should back this up regularly.

- key

    This is the flask `SECRET_KEY`. It should obviously be kept secret.

If you wish to pass additional configuration to flask, put it in `app.conf`.
