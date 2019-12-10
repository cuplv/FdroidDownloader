from time import sleep

import download, getopt, sys

def main(argv):
    d = False
    u = False
    n = 20
    v = 0
    y = "1990"
    delay = 0
    try:
        opts, args = getopt.getopt(argv, "hdn:uv:y:")
    except getopt.GetoptError:
        print("Bad usage. Try -h for more information.")
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-h":
            print("Flags:")
            print("-d        turn on downloads")
            print("-h        help")
            print("-n <#>    search for up to # apps")
            print("-u        upload to amazon s3 bucket")
            print("-v <#>    ignore targetSdk versions less"
                  " than #")
            print("-y <yyyy> ignore apps published before yyyy")
            print("--delay <#>   wait # seconds between downloads")
            sys.exit(0)
        if opt == "-d":
            d = True
        if opt == "-n":
            n = int(arg)
        if opt == "-u":
            u = True
        if opt == "-v":
            v = int(arg)
        if opt == "-y":
            y = arg
        if opt == "--delay":
            delay = float(arg)

    # download
    count = 0
    for packageName in download.packages:
        if count != 0:
            sleep(delay)
        if count >= n:
            return 0
        try:
            r = download.Download(packageName, download=d,
                                  upload=u, minVer=v, minYear=y)
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
