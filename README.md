# F-Droid Downloader
---

Python script for downloading and uploading Android application `apk`
and `src` files.

Install requirements with `pip install -r requirements.txt`.

Usage guide:

```
python main.py <flags>

flags:
-d        turn on downloads
-h        help
-n <#>    search for up to # apps
-u        upload to amazon s3 bucket
-v <#>    ignore targetSdk versions less than #
-y <yyyy> ignore apps published before yyyy
```

Example: `python main.py -n 50 -v 29 -u` will upload the first 50
files of SDK version 29 or later to the Amazon S3 bucket specified in
`download.py`

You must have a `credentials` file in your `~/.aws` directory in order
to upload to S3.