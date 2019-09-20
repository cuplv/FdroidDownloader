import download, getopt, sys

def main(argv):
    d = False
    n = 20
    v = "0"
    try:
        opts, args = getopt.getopt(argv, "hdn:v:")
    except getopt.GetoptError:
        print("Bad usage. Try -h for more information.")
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-h":
            print("Flags:")
            print("-d        turn on downloads")
            print("-h        help")
            print("-n <#>    search for up to # apps")
            print("-v <#>    ignore targetSdk versions less"
                  " than #")
            sys.exit(0)
        if opt == "-d":
            d = True
        if opt == "-n":
            n = int(arg)
        if opt == "-v":
            v = int(arg)

    # download
    count = 0
    for packageName in download.packages:
        if count >= n:
            return 0
        try:
            r = download.Download(packageName, download=d,
                                  minVer=v)
            if r == 0:
                count += 1
        except:
            print("There was an issue with package %s."
                  " Ignoring..." % packageName)
            pass
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
