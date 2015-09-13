import exifread
import string
import pprint
import getopt
from PIL import Image
import magic
import sys
import os

def main (argv):
    config = parse_args(argv)
    config["allowed_mime"] = ["image/png",
                              "image/tiff",
                              "image/tiff-fx",
                              "image/jpeg",
                              "image/pjpeg",
                              "image/gif"]
    img_coll = []
    if insanity(config):
        print "Config is not sane.  Exiting."
        sys.exit(2)
    img_coll = build_imglist(config)
    status = write_images(img_coll)
    print status
    sys.exit()

def build_imglist(config):
    imglist = []
    for f in os.listdir(config["indir"]):
        fpath = config["indir"] + "/" + str(f)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            fmime = m.id_filename(fpath)
        if fmime in config["allowed_mime"]:
            imglist.append(Pic(fpath, config))
    return imglist


def write_images(imgcoll):
    status = ""
    for img in imgcoll:
        if not does_file_exist(img.out_loc):
            img.img_sans_exif.save(img.out_loc)
        else:
            status = status + ("Destination file already exists: " + img.out_loc + "  Not overwriting!\n")
    if status == "":
        status = "All image files processed successfully!"
    return status

def does_file_exist(fpath):
    if os.path.isfile(fpath):
        return True
    else:
        return False

def is_empty_dir(directory):
    try:
        if not os.listdir(directory):
            return True
        else:
            return False
    except:
        return True

def not_writeable_dir(directory):
    if os.access(directory, os.W_OK):
        return False
    else:
        return True

def no_img_files(allowed_mime, indir):
    img_files = []
    exif_files = []
    try:
        for f in os.listdir(indir):
            fpath = str(indir) + '/' + str(f)
            with open(fpath, 'rb') as fh:
                tags = exifread.process_file(fh)
            if len(tags) > 0:
                exif_files.append(fpath)
                with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                    fmime = m.id_filename(fpath)
            if fmime in allowed_mime:
                img_files.append(fpath)
        if img_files == []:
            return True
        else:
            print "This script will attempt to copy every image file.\nThe following files were detected with EXIF metadata:\n"
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(exif_files)
            return False
    except:
        True

def insanity(config):
    insane = False
    if is_empty_dir(config["indir"]):
        print "Source dir is empty or does not exist!"
        insane = True
    if not_writeable_dir(config["outdir"]):
        print "Output dir is not writeable or does not exist!"
        insane = True
    if no_img_files(config["allowed_mime"], config["indir"]):
        print "No supported images in dest dir!"
        insane = True
    if insane:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(config)
    return insane

def parse_args(argv):
    config = {}
    config["usagetext"] = "epurge.py -s SRCDIR -d DSTDIR"
    try:
        opts, args = getopt.getopt(argv, "hs:d:", ["src_dir=", "dst_dir="])
    except getopt.GetoptError:
            print config["usagetext"]
            sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print config["usagetext"]
            sys.exit(2)
        elif opt in ("-s", "--src_dir"):
            config["indir"] = arg
        elif opt in ("-d", "--dst_dir"):
            config["outdir"] = arg
    return config

class Pic():
    def __init__(self, fs_loc, config):
        self.in_loc = fs_loc
        self.f_name = string.replace(fs_loc, config["indir"], "")
        self.out_loc = config["outdir"] + self.f_name
        self.img_file = open(fs_loc)
        self.img = Image.open(self.img_file)
        self.data = list(self.img.getdata())
        self.img_sans_exif = Image.new(self.img.mode, self.img.size)
        self.img_sans_exif.putdata(self.data)

if __name__ == "__main__":
    main(sys.argv[1:])
