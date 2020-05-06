#!/usr/bin/python

# This script builds a LiveOS squashfs image for use with dracut livenet
# module. Meant to be run as a mkosi.finalize script. Uses pylorax to package
# the mkosi image (built as an OS directory tree) into a squashfs image.
#
# Copyright 2020 University at Buffalo. All rights reserved.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Author: Andrew E. Bruno <aebruno2@buffalo.edu>
#

import argparse
import logging
import os
import shutil
import sys
import tempfile
import pylorax.imgutils as imgutils

BOOT_ASSETS_PATH = '/srv/pxelive'

def copy_boot_assets(image, boot_assets_dir, out_dir):
    """
    Copy the kernel and initramfs.img (with livenet) from the image to the
    output directory.
    """
    vmlinuz_path = out_dir+'/'+image+'-vmlinuz'
    initrd_path = out_dir+'/'+image+'-initramfs.img'
    # Remove any existing initramfs/vmlinuz
    unlink(vmlinuz_path)
    unlink(initrd_path)

    shutil.copy(boot_assets_dir+'/vmlinuz', vmlinuz_path)
    shutil.copy(boot_assets_dir+'/initramfs.img', initrd_path)
    # TODO should we remove this?
    # unlink(boot_assets_dir)

def make_pxe_live(image, image_root, out_dir):
    """
    Use pylorax to generate a SquashFS image with an embedded ext4 rootfs.img
    used for PXE booting. 
    """
    squashfs_path =  out_dir+'/'+image+'-squashfs.img'
    # Remove any existing squashfs images
    unlink(squashfs_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(tmpdir+'/LiveOS', mode=0o700, exist_ok=True)

        imgutils.mkrootfsimg(image_root, tmpdir+'/LiveOS/rootfs.img', size=None, label="LiveOS")
        imgutils.mksquashfs(tmpdir, squashfs_path, 'xz', [])

def unlink(path):
    """Remove files/directories"""
    try:
        os.unlink(path)
    except:
        pass

    try:
        shutil.rmtree(path)
    except:
        pass

def main():
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING
    )

    parser = argparse.ArgumentParser(description='Generate PXE live image')
    parser.add_argument("verb", help="mkosi verb")
    parser.add_argument("-v", "--verbose", help="output debugging information", action="store_true")
    parser.add_argument("-o", "--output", help="path to mkosi.output directory")
    parser.add_argument("-i", "--image", help="image name")

    args = parser.parse_args()
    logging.getLogger().setLevel(logging.DEBUG)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)


    if args.verb != 'final':
        logging.critical("Unsupported verb: %s", args.verb)
        sys.exit(0)

    out_dir = os.getenv('OUTPUT_DIR', '')
    if args.output:
        out_dir = args.output

    if not out_dir:
        out_dir = os.getcwd() + '/mkosi.output'

    if not os.path.exists(out_dir):
        logging.critical("Output directory not found: %s", out_dir)
        sys.exit(1)

    image_root = os.getenv('OUTPUT', '')
    if args.image:
        image_root = os.path.join(out_dir, args.image)
    elif image_root:
        args.image = os.path.basename(image_root)

    if not args.image:
        logging.critical("Failed to find image name. Please provide an image name")
        sys.exit(1)

    if image_root == '' or not os.path.exists(image_root):
        logging.critical("Root image directory not found: %s", image_root)
        sys.exit(1)

    boot_assets_dir = image_root+BOOT_ASSETS_PATH
    if os.path.exists(boot_assets_dir):
        copy_boot_assets(args.image, boot_assets_dir, out_dir)
    else:
        logging.warning("Boot assets dir not found (skipping copy): %s", boot_assets_dir)
    
    make_pxe_live(args.image, image_root, out_dir)

if __name__ == "__main__":
    main()
