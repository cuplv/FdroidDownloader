from os.path import exists

import arrow, boto3, hashlib, json, os, shutil, urllib
from requests.exceptions import MissingSchema

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


def sortBy(x):
    if "versionCode" in x:
        return x["versionCode"]
    else:
        print("Version code not found in: %s" % str(x))
        return 99999
def latestVersion(all_packages):
    packageValues = all_packages['versions']
    mostRecentDate = 0
    mostRecent = None

    for hash in packageValues:
        curr = packageValues[hash]
        added = curr['added']
        if mostRecentDate < added:
            mostRecentDate = added
            mostRecent = curr
    return mostRecent

# import module
import requests

# create a function
# pass the url
def url_ok(url):

    # exception block
    try:

        # pass the url into
        # request.hear
        response = requests.head(url)

        # check the status code
        if response.status_code == 200:
            return True
        elif response.status_code == 301:
            newUrl = response.headers['Location']
            return url_ok(newUrl)
        else:
            return False
    except requests.ConnectionError as e:
        return False
    except MissingSchema as e:
        return False


def Download(packageName, download, upload, minVer, baseDir=None, allVersions=False):
    """
    :param packageName:
    :param download: boolean, download to directory
    :param upload: boolean, upload to amazon s3 bucket
    :param minVer: ignore min versions less than this
    :param baseDir: directory to download apps to
    :return: number of actual packages downloaded
    """
    if baseDir is None:
        baseDir = "data/apps/"
    if upload and not use_s3:
        raise Exception("S3 profile not found")
    downloaded = 0
    all_packages = packages[packageName]
    packages_to_download = []
    if allVersions:
        raise Exception("TODO:implement me if needed")
    else:
        packages_to_download = [latestVersion(all_packages)]
        # packageValues.sort(key=sortBy)
        # all_packages.reverse()
        # download_packages = all_packages[:1]
    for data in packages_to_download:
        apkName          = str(data['file']["name"])
        if 'src' not in data:
            print("skipping malformed %s " % packageName)
            continue
        srcName          = str(data['src']['name'])
        theHash          = str(data['file']["sha256"])
        versionName      = str(data['manifest']["versionName"])
        targetSdkVersion = str(data['manifest']['usesSdk']["targetSdkVersion"])

        # dividing to eliminate the zeroes tacked on at the end

        # skips packages older than the minimum SDK version
        if int(targetSdkVersion) < minVer:
            continue

        # skips packages older than the minimum year
        # minimum = arrow.get(minYear, "YYYY")
        # current = arrow.get(timeStamp)
        # if current.year < minimum.year:
        #     continue
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
            urllib.request.urlretrieve("https://f-droid.org/repo/"\
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
                res = urllib.request.urlretrieve("https://f-droid.org/repo/"\
                                   + srcName, srcDir + srcName)
                if int(res[1].get('content-length')) > 0:
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
