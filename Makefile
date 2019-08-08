# Name of pysal package to develop on
PACKAGE=geopyter

# build the container
container:
	docker build -t $(PACKAGE) .

# run jupyter notebook for development
nb:
	docker run --rm -p 8888:8888 -v ${PWD}:/home/jovyan $(PACKAGE)

# run a shell for development, manually launch jupyter 
cli:
	docker run -it -p 8888:8888 -v ${PWD}:/home/jovyan $(PACKAGE) sh -c "/home/jovyan/develop.sh && /bin/bash"
shell:
	docker run -it -p 8888:8888 -v ${PWD}:/home/jovyan $(PACKAGE)  /bin/bash
