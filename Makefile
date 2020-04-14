OWNER=nielsbohr
IMAGE=fair-projects
TAG=edge
SERVER_NAME=fair.erda.dk
APP_NAME=fair-projects
APP_DIR=/var/${APP_NAME}
ARGS=

all: clean build push

build:
	mkdir -m775 -p persistence
	chgrp 33 persistence
	docker build -t ${OWNER}/${IMAGE}:${TAG} --build-arg SERVER_NAME=${SERVER_NAME} \
	                                         --build-arg APP_NAME=${APP_NAME} \
						 					 --build-arg APP_DIR=${APP_DIR} ${ARGS} .

clean:
	rm -fr persistence
	docker rmi -f ${OWNER}/${IMAGE}:${TAG}

push:
	docker push ${OWNER}/${IMAGE}:${TAG}
