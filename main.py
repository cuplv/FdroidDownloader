import random
from time import sleep

import download, argparse, sys

def main(argv):

    parser = argparse.ArgumentParser(description="Download Fdroid Applications.")
    parser.add_argument('-d', help="turn on downloads", default=False, action='store_true')
    parser.add_argument('-n', help="number of apps to download", default=20, type=int)
    parser.add_argument("--out_dir", help="directory to store apps", default=None)
    parser.add_argument("--delay", help="delay between downloads", default=0, type=int)
    parser.add_argument("-y", help="ignore apps published before yyyy", default="1990")
    parser.add_argument("-v", help="ignore targetSdk versions less", default=0, type=int)
    parser.add_argument("-u", help="upload to amazon s3 bucket", default=False, type=bool)
    parser.add_argument("--all_versions",
                        help="download all versions of each app instead of only the latest",
                        default=False, action='store_true')

    args = parser.parse_args(argv)

    # download
    count = 0

    # Shuffle downloads to get a random sampling of apps
    random.shuffle(download.packages)
    
    for packageName in download.packages:
        if count != 0:
            sleep(args.delay)
        if count >= args.n:
            return 0
        try:
            r = download.Download(packageName, download=args.d,
                                  upload=args.u, minVer=args.v,
                                  minYear=args.y, baseDir=args.out_dir,allVersions=args.all_versions)
            if r > 0:
                count += 1
        except Exception as e:
            print("There was an issue with package %s."
                  " Ignoring..." % packageName)
            print(e)
            pass
    sys.exit(3)
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
