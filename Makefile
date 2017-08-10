default: all

.PHONY: clean test build docker

all: clean test build

OUTPUTS = dist *.egg-info .eggs
PYTHON = python3
P_FLAGS = -W ignore::UserWarning:distutils.dist

clean: setup-clean clean_docker_folder
	rm -rf $(OUTPUTS)

setup-%:
	$(PYTHON) $(P_FLAGS) setup.py $*

test: setup-test

build: setup-sdist

upload:
	devpi upload --from-dir dist

docker:
	cp dist/*.tar.gz docker
	cd docker; ./build.sh
	$(MAKE) clean_docker_folder

clean_docker_folder:
	rm -f docker/*.tar.gz
