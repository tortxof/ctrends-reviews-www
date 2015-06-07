# ctrends-reviews-www

## A flask app for managing reviews.

The puropse of this app is to receive anonymous reviews, provide an admin
interface for managing the reviews, and serving public json data of approved
reviews.

### Setup

Clone the repo and build the docker image.

    git clone http://gitlab.djones.co/tortxof/ctrends-reviews-www.git
    cd ctrends-reviews-www
    docker build -t tortxof/ctrends-reviews

Run the image.

    docker run -d --restart always --name ctrends-reviews -p 8009:5000 tortxof/ctrends-reviews

A couple of files will be created in `/data` in the container.

- /data/reviews.db

    This is the sqlite3 database. You should back this up regularly.

- /data/key

    This is the flask `SECRET_KEY`. It should obviously be kept secret.


Create a data container. The database and key file will remain in this data
container when you remove the app container.

    docker create --name ctrends-reviews-data --volumes-from ctrends-reviews busybox

To update the app, stop and remove the app container, rebuild the image, and
start a new container like this.

    docker run -d --restart always --name ctrends-reviews --volumes-from ctrends-reviews-data -p 8009:5000 tortxof/ctrends-reviews
