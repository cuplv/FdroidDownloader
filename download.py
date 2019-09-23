import arrow, boto3, hashlib, json, os, shutil, urllib

# start an amazon s3 session
session     = boto3.Session(profile_name="default")
s3          = session.client("s3")
BUCKET_NAME = "phillip-test"
    
BUF_SIZE = 65536        # buffer for computing hash
baseDir  = "data/apps/" # path to retrieved data

with open("data/index/index.json", "r") as f:
    j_data = json.load(f)
    f.close()

packages = j_data["packages"] # dict, contains app data

def Download(packageName, download, upload, minVer, minYear):
    for data in packages[packageName]:
        apkName          = str(data["apkName"])
        srcName          = str(data["srcname"])
        theHash          = str(data["hash"])
        packageName      = str(data["packageName"])
        hashType         = str(data["hashType"])
        versionCode      = str(data["versionCode"])
        versionName      = str(data["versionName"])
        minSdkVersion    = str(data["minSdkVersion"])
        targetSdkVersion = str(data["targetSdkVersion"])
        size             = str(data["size"])
        
        # dividing to eliminate the zeroes tacked on at the end
        timeStamp        = int(data["added"]) / 1000

        # skips packages older than the minimum SDK version
        if int(targetSdkVersion) < minVer:
            return 1

        # skips packages older than the minimum year
        minimum = arrow.get(minYear, "YYYY")
        current = arrow.get(timeStamp)
        if current.year < minimum.year:
            return 1
        
        apkDir = baseDir + packageName + "/" +\
            targetSdkVersion + "/apk/"

        srcDir = baseDir + packageName + "/" +\
            targetSdkVersion + "/src/"

        # touch directories and
        # put application data in meta.txt
        if not os.path.exists(apkDir):
                os.makedirs(apkDir)
        if not os.path.exists(srcDir):
                    os.makedirs(srcDir)
        with open(baseDir + packageName + "/meta.txt",
                  "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.close()

        if download or upload:
        # download apk
            print("Retrieving %s" % packageName)
            urllib.urlretrieve("https://f-droid.org/repo/"\
                               + apkName, apkDir + apkName)

            # compute hash
            with open(apkDir + apkName, "rb") as f:
                sha256 = hashlib.sha256()
                while True:
                    buf = f.read(BUF_SIZE)
                    if not buf:
                        f.close()
                        break
                    sha256.update(buf)

            if(sha256.hexdigest() == theHash):
                # download src
                urllib.urlretrieve("https://f-droid.org/repo/"\
                                   + srcName, srcDir + srcName)

                if upload:
                    s3.upload_file(baseDir + packageName +
                                   "/meta.txt", BUCKET_NAME,
                                   baseDir + packageName +
                                   "/meta.txt")
                    s3.upload_file(apkDir + apkName,
                                   BUCKET_NAME,
                                   apkDir + apkName)
                    s3.upload_file(srcDir + srcName,
                                   BUCKET_NAME,
                                   srcDir + srcName)
                if not download:
                    shutil.rmtree(baseDir + packageName + "/")
                return 0
            else:
                print("Project %s could not be retrieved."
                      % packageName)
                shutil.rmtree(baseDir + packageName + "/" +\
                              targetSdkVersion)
                return 2
        else:
            print("Found (but did not download) %s" % packageName)
            return 0
