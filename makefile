commits := master..HEAD

all: flake8 mypy pytest coverage gitlint licence whitespace package lintian clean
	@echo SUCCESS

flake8:
#	Manually specify files without .py extension
	flake8 --count . vyatta_policy_qos_vci/policy_qos

mypy:
	mypy .

pytest:
	coverage run --source . -m pytest

coverage:
	coverage html
	coverage report

gitlint:
	gitlint --commits $(commits)

licence:
#	check changed files have the correct licence information
	$(eval changed_files := $(shell git diff -G'.' --diff-filter=rd --find-renames=100% --name-only $(commits) | tr '\n' ' '))
	ci-pipeline-scripts/check-licence.py $(changed_files)

whitespace:
#	Check changed files for trailing whitespace.
	$(eval changed_files := $(shell git diff -G'.' --diff-filter=rd --find-renames=100% --name-only $(commits) | tr '\n' ' '))
#	/dev/null prevents grep from hanging if changed_files is empty
	! grep --with-filename --line-number --only-matching "\s$$" $(changed_files) /dev/null

package:
	dpkg-buildpackage
	mkdir -p deb_packages
	cp ../*.deb ./deb_packages/
	dh_clean

lintian:
	lintian --fail-on warning --profile vyatta

clean:
	dh_clean
	py3clean .

build-container:
	sudo docker image build --tag vplane-config-qos .

run-container:
	sudo docker run \
		--interactive \
		--tty \
		--mount type=bind,src=${PWD},dst=/home/docker/code \
		--mount type=bind,src=${HOME}/.gitconfig,dst=/home/docker/.gitconfig \
		--mount type=bind,src=${HOME}/.bashrc,dst=/home/docker/.bashrc \
		--mount type=bind,src=${HOME}/.bash_profile,dst=/home/docker/.bash_profile \
		--mount type=bind,src=${HOME}/.ssh,dst=/home/docker/.ssh \
		--mount type=bind,src=${HOME}/.bash_history,dst=/home/docker/.bash_history \
		--user $$(id -u):$$(id -g) \
		--rm \
		vplane-config-qos