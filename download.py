from os.path import exists

import arrow, boto3, hashlib, json, os, shutil, urllib

# start an amazon s3 session
try:
    session     = boto3.Session(profile_name="default")
    s3          = session.client("s3")
    BUCKET_NAME = "mcgroum-corpus"
    use_s3 = True
except Exception:
    print("No s3 profile found, using local storage.")
    use_s3 = False

    
BUF_SIZE = 65536        # buffer for computing hash

with open("data/index/index.json", "r") as f:
    j_data = json.load(f)
    f.close()

packages = j_data["packages"] # dict, contains app data



def Download(packageName, download, upload, minVer, minYear, baseDir="data/apps/"):
    """
    :param packageName:
    :param download:
    :param upload:
    :param minVer:
    :param minYear:
    :param baseDir:
    :return: number of actual packages downloaded
    """
    if upload and not use_s3:
        raise Exception("S3 profile not found")
    downloaded = 0
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
            continue

        # skips packages older than the minimum year
        minimum = arrow.get(minYear, "YYYY")
        current = arrow.get(timeStamp)
        if current.year < minimum.year:
            continue
        downloadBase = os.path.join(baseDir, packageName, versionName)

        apkDir = os.path.join(downloadBase, "apk/")
        srcDir = os.path.join(downloadBase, "src/")

        completedFileName = os.path.join(downloadBase, "completed.txt")
        metaDataFileName = os.path.join(downloadBase,"meta.txt")

        # touch directories and
        # put application data in meta.txt
        if not os.path.exists(apkDir):
                os.makedirs(apkDir)
        if not os.path.exists(srcDir):
                    os.makedirs(srcDir)
        with open(metaDataFileName,"w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.close()

        # Don't re download if previous download succeeded
        if exists(completedFileName):
            with open(completedFileName,'r') as completedFile:
                observedHash = completedFile.readline()
                if observedHash == theHash:
                    print("Package %s %s already downloaded and valid." % (packageName, versionName))
                    continue
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
                res = urllib.urlretrieve("https://f-droid.org/repo/"\
                                   + srcName, srcDir + srcName)
                if 'content-length' in res[1].dict and int(res[1].dict['content-length'] > 0):
                    # Download succeeded
                    with open(completedFileName,'w') as completedFile:
                        completedFile.write(theHash)
                        downloaded += 1

                if upload:
                    raise Exception("Unimplemented, TODO: fix the following paths to use version name instead of "
                                    "target sdk")
                    # s3.upload_file(baseDir + packageName +\
                    #                "/" + targetSdkVersion + "/meta.txt",
                    #                BUCKET_NAME, baseDir + packageName +\
                    #                "/" + targetSdkVersion + "/meta.txt")
                    # s3.upload_file(apkDir + apkName,
                    #                BUCKET_NAME,
                    #                apkDir + apkName)
                    # s3.upload_file(srcDir + srcName,
                    #                BUCKET_NAME,
                    #                srcDir + srcName)
                if not download:
                    shutil.rmtree(os.path.join(baseDir, packageName))
                continue
            else:
                print("Project %s could not be retrieved."
                      % packageName)
                shutil.rmtree(downloadBase)
                continue
        else:
            print("Found (but did not download) %s" % packageName)
            continue
    return downloaded
