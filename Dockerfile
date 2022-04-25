FROM debian:11
USER root

# Prevent apt from asking the user questions like which time zone.
ARG DEBIAN_FRONTEND=noninteractive

# --------------------- Add docker user & set working dir -------------------- #
# * Set password to `docker`.
# * Provide sudo permissions.
# * Set docker uid to 1001 as that is what most people have their host uid set to.
RUN apt-get update --yes
RUN apt-get install --yes sudo
RUN useradd --shell /bin/bash --uid 1001 --create-home docker
RUN echo "docker:docker" | chpasswd
RUN adduser docker sudo
WORKDIR /home/docker/code
# ---------------------------------------------------------------------------- #


# ------------------------ Add Vyatta tools repository ----------------------- #
# TODO: This sometimes fails over vpn because the container cannot reach repos.eng.vyatta.net.
RUN echo 'deb [trusted=yes] http://repos.eng.vyatta.net/Vyatta:/Tools/Debian11/ ./' >> /etc/apt/sources.list
RUN echo 'deb [trusted=yes] http://repos.eng.vyatta.net/Tools/Debian11/ ./' >> /etc/apt/sources.list
RUN echo 'deb [trusted=yes] https://download.opensuse.org/repositories/openSUSE:/Tools/Debian_11/ ./' >> /etc/apt/sources.list
RUN apt-get update --yes
# ---------------------------------------------------------------------------- #


# ---------------------- Install useful developer tools ---------------------- #
# Generic tools
RUN apt-get install --yes iputils-ping openssh-client
RUN apt-get install --yes python3-autopep8

# Vyatta specific tools
RUN apt-get update --yes
RUN apt-get install --yes vyatta-dev-role-maintainer
# ---------------------------------------------------------------------------- #


# ---------------- Install Debian build/packaging dependencies --------------- #
# Install mk-build-deps program.
RUN apt-get install --yes devscripts equivs
# Only copy the debian control file as it describes the projects build/packaging dependencies.
COPY ./debian/control /tmp/control
# Install application's build/packaging dependencies.
RUN mk-build-deps --install --remove --tool='apt-get --yes' /tmp/control
# Remove generated files.
RUN rm *.buildinfo *.changes
# Install vyatta configuration for debian lintian tool.
RUN apt-get install --yes --fix-missing lintian-profile-vyatta
# ---------------------------------------------------------------------------- #


# ------------------- Install pip development dependencies ------------------- #
# TODO: Should this pip file just be deleted and these dependencies can live in the dockerfile?
COPY ./dev-requirements.txt /tmp/dev-requirements.txt
RUN apt-get update --yes
RUN apt-get install --yes python3-pip
RUN pip3 install --requirement /tmp/dev-requirements.txt
# ---------------------------------------------------------------------------- #


# ---------------------------- Jenkins work around --------------------------- #
# Jenkins mounts the directory at /var/lib/jenkins/workspace/DANOS_vplane-config-qos_PR-XXX.
# Non root users do not have write permissions in /var so cannot write above the mounted directory.
# dpkg-buildpackage deposits debs (and temp files) in the parent directory.
# Currently there is no way to specify a different directory (https://groups.google.com/g/linux.debian.bugs.dist/c/1KiGKfuFH3Y).
RUN mkdir -p /var/lib/jenkins/workspace/ \
 && chmod -R a+w /var/lib/jenkins/workspace/
# ---------------------------------------------------------------------------- #