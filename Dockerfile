# lightweight linux distro
FROM python:3

LABEL maintainer="Isaac Rockafellow <isaac.rockafellow@gmail.com>"
WORKDIR /home
# Get dependencies
ADD . /home
