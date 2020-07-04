# Grendel Images

[![Documentation Status](https://readthedocs.org/projects/grendel/badge/?version=latest)](https://grendel.readthedocs.io/en/latest/?badge=latest)

[Grendel](https://github.com/ubccr/grendel) is a fast, easy to use bare metal
provisioning system for High Performance Computing (HPC) Linux clusters. This
repository contains the scripts for building bare-metal OS images for use with
Grendel. These images are geared towards HPC compute nodes that are PXE booted
but configs for building generic images are also provided. See
[mkosi](https://github.com/ubccr/mkosi) for more details on how images are
built. Note: we currently use a fork of mkosi which includes some bug fixes not
available in the upstream repo.

## Pre-build test images

You can find pre-build images for use with testing grendel 
[here](https://github.com/ubccr/grendel-images/releases). DO NOT use these
images in production. Default root password is: ilovelinux

## Requirements

- CentOS 8 / systemd 233 (or newer) 
- Python 3.6 
- mkosi (ccrdev branch [here](https://github.com/ubccr/mkosi/tree/ccrdev)) 
- [pylorax](https://github.com/weldr/lorax) 
- debootstrap (to build debian/ubuntu images)
- dnf
- systemd-nspawn

Install mkosi:

```
$ git clone https://github.com/ubccr/mkosi.git
$ cd mkosi
$ git checkout ccrdev
$ sudo python setup.py install --prefix=/usr
```

Install pylorax:

```
$ sudo yum install lorax
```

## Build images

Configurations for each image can be found in the `mkosi.files` directory.
These contain various settings passed to `mkosi` for building each image.

Follow these steps for building images:

1. Clone this repo:

```
$ git clone https://github.com/ubccr/grendel-images.git
$ cd grendel-images
```

2. Any files in `mkosi.extra` directory will be added to the image. You can
place anything in this directory and it will get copied directly into the final
image. At minimum, you'll want to add ssh keys for the root user so you can
login via ssh after the image boots. Create a directory named `mkosi.extra` and
add your ssh keys:

```
$ mkdir -p mkosi.extra/root/.ssh
$ chmod 700 mkosi.extra/root/.ssh
$ touch mkosi.extra/root/.ssh/authorized_keys
$ chmod 600 mkosi.extra/root/.ssh/authorized_keys
$ [Add ssh keys to the file above]
```

3. Optionally add a root password. Create a file named `mkosi.rootpw`
containing the hashed root password.

4. To build an image, simply run mkosi and provide the config file for the
image you want to build. Note: must be run as the root user:

```
# Build generic CentOS 7 image
$ sudo mkosi --default=./mkosi.files/mkosi.centos7 

# Build generic CentOS 8 image
$ sudo mkosi --default=./mkosi.files/mkosi.centos8

# Build generic Ubuntu Focal Fossa image
$ sudo mkosi --default=./mkosi.files/mkosi.ubuntu-focal

# Build generic Ubuntu Bionic Beaver image
$ sudo mkosi --default=./mkosi.files/mkosi.ubuntu-bionic
```

5. The resulting image files will be located in the `mkosi.output` directory.
Each image is built as a plain directory containing the OS tree. By default,
a `mkosi.postinst` script will be run inside the image that uses dracut to
build an initrd containing the livenet module for booting live images.
Additionally, a `mkosi.finalize` script will be run that packages the entire OS
directory tree as a LiveOS squashfs image that can be used for PXE booting.
These scripts can be found in the `bin/` directory.

## Boot images with Grendel

`mkosi` will produce 4 artifacts in the `mkosi.output` directory. For example,
after building the Centos 7 image, `mkosi.output` should look like this:

```
mkosi.output/centos7
mkosi.output/centos7-vmlinuz
mkosi.output/centos7-initramfs.img
mkosi.output/centos7-squashfs.img
```

Copy the image files to `/var/grendel/images` or where ever you've configured
Grendel to look for images. 

Configure the image in Grendel with the following json:

```json
{
    "name": "centos7-live",
    "kernel": "/var/grendel/images/centos7-live/centos7-vmlinuz",
    "initrd": [
        "/var/grendel/images/centos7-live/centos7-initramfs.img"
    ],
    "liveimg": "/var/grendel/images/centos7-live/centos7-squashfs.img",
    "cmdline": "console=tty0 console=ttyS0 root=live:$liveimg BOOTIF=$mac rd.neednet=1 ip=dhcp"
}
```
