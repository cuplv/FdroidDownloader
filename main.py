import random
from time import sleep

import download, argparse, sys

def main(argv):

    parser = argparse.ArgumentParser(description="Download Fdroid Applications.")
    #parser.add_argument('-d', help="turn on downloads", default=False, action='store_true')
    #parser.add_argument('-n', help="number of apps to download", default=20, type=int)
    parser.add_argument("--out_dir", help="directory to store apps", default=None)
    parser.add_argument("--delay", help="delay between downloads", default=5, type=int)
    #parser.add_argument("-y", help="ignore apps published before yyyy", default="1990")
    #parser.add_argument("-v", help="ignore targetSdk versions less", default=0, type=int)
    #parser.add_argument("-u", help="upload to amazon s3 bucket", default=False, type=bool)
    # parser.add_argument("--all_versions",
    #                     help="download all versions of each app instead of only the latest",
    #                     default=False, action='store_true')
    parser.add_argument("--package", help="download a specific package", default=None)
    parser.add_argument("--packagefile", help="download a specific package", default=None)

    args = parser.parse_args(argv)

    # download
    if args.package is not None:
        packages_to_download = [args.package]
        if args.package not in download.packages:
            raise Exception("Package: %s does not exist" % args.package)
    if args.packagefile is not None:
        with open(args.packagefile,'r') as package_file:
            packages = package_file.readlines()

            packages_to_download = []
            for pkg in packages:
                tpkg = pkg.strip()
                packages_to_download.append(tpkg)
                assert(pkg in download.packages, "pkg %s not found" % pkg)

            downloadPackages(packages_to_download, args.delay, args.out_dir)
    else:
        # Shuffle downloads to get a random sampling of apps
        packages_to_download = list(download.packages)
        random.shuffle(packages_to_download)
    downloadPackages(packages_to_download, args.delay, args.out_dir)


def downloadPackages(packages_to_download, delay, out_dir):
    count = 0
    for packageName in packages_to_download:
        if count != 0:
            sleep(delay)
        # if count >= args.n:
        #     return 0
        # try:
        r = download.Download(packageName, download=True,
                              upload=False, minVer=0, baseDir=out_dir)
        if r > 0:
            count += 1
        # except Exception as e:
        #     print("There was an issue with package %s."
        #           " Ignoring..." % packageName)
        #     print(e)
        #     raise e
        #     # pass
    sys.exit(3)
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
