import java.io.{File, PrintWriter}

import scala.collection.immutable.StringOps
import scala.io.Source
import scala.xml.{MetaData, Node, NodeSeq, XML}
object Downloader {
  def main(args: Array[String]): Unit = {
    downloadList("/Users/s/Documents/data/fdroid_manually_curated/fdroid_list.txt")
//    allAppNames()
  }
  def getCategories(): Set[String] = {
    val fdroid_index = XML.loadFile("/Users/s/Documents/data/fdroid_corpus/index/index.xml")
    val b: NodeSeq = fdroid_index \\ "fdroid" \\ "application"
    b.flatMap(a => {
      val text: String = ( a \\ "category").text
      Some(text)
    }).toSet
  }
  def downloadList(listfile: String): Unit = {
    val fdroid_index = XML.loadFile("/Users/s/Documents/data/fdroid_corpus/index/index.xml")
    val b: NodeSeq = fdroid_index \\ "fdroid" \\ "application"
    val file_contnets = Source.fromFile(listfile).foldLeft("")((acc,v) => {
      acc + v
    }).split("\n")
    val appsToDownload: Set[String] = file_contnets.toSet
    val games_with_no_native_code = b.flatMap((a : Node) => {
      val source = (a \\ "source").text
      val id = (a \\ "id").text
      val lastupdated = (a \\ "lastupdated").text
      val name = (a \\ "name").text
      val web = (a \\ "web").text
      val category = ( a \\ "category").text
      val seq: NodeSeq = a \\ "apkname"
      val apkname = seq.text
      val srcname = (a \\ "srcname").text
      val latest_package = (a \\ "package").sortBy( a => {(a \\ "versioncode").text}).reverse.head
      val latest_package_versioncode = (latest_package \\ "versioncode").text
      val native_code_latest_package = (latest_package \\ "nativecode").text
      val latest_package_apks = (latest_package \\ "apkname")
      assert(latest_package_apks.length == 1)
      val latest_package_apk = latest_package_apks.text
      val latest_package_srcs = (latest_package \\ "srcname")
      if(latest_package_srcs.length > 1){
        println(latest_package_srcs.length)
        ???
      }
      val latest_package_src = latest_package_srcs.text
      val latest_package_sha = (latest_package \\ "hash").text




      if(appsToDownload.contains(name) && latest_package_srcs.length != 0){
        println(name)
        downloadAPK("/Users/s/Documents/data/fdroid_manually_curated/apps", id, latest_package_versioncode, a, latest_package, latest_package_apk, latest_package_src, latest_package_sha)
        Some(1)
      }else{
        None
      }
    })
    println(games_with_no_native_code.length)

  }
  def allAppNames(): Unit = {
    val fdroid_index = XML.loadFile("/Users/s/Documents/data/fdroid_corpus/index/index.xml")
    val b: NodeSeq = fdroid_index \\ "fdroid" \\ "application"
    val games_with_no_native_code = b.flatMap((a : Node) => {
      val source = (a \\ "source").text
      val id = (a \\ "id").text
      val lastupdated = (a \\ "lastupdated").text
      val name = (a \\ "name").text
      val web = (a \\ "web").text
      val category = ( a \\ "category").text
      val seq: NodeSeq = a \\ "apkname"
      val apkname = seq.text
      val srcname = (a \\ "srcname").text
      val latest_package = (a \\ "package").sortBy( a => {(a \\ "versioncode").text}).reverse.head
      val latest_package_versioncode = (latest_package \\ "versioncode").text
      val native_code_latest_package = (latest_package \\ "nativecode").text
      val latest_package_apks = (latest_package \\ "apkname")
      assert(latest_package_apks.length == 1)
      val latest_package_apk = latest_package_apks.text
      val latest_package_srcs = (latest_package \\ "srcname")
      if(latest_package_srcs.length > 1){
        println(latest_package_srcs.length)
        ???
      }
      val latest_package_src = latest_package_srcs.text
      val latest_package_sha = (latest_package \\ "hash").text


      println(name)
      name
    })
    println(games_with_no_native_code.length)

  }
  def downloadCategory(fcategory: String): Unit = {
    val fdroid_index = XML.loadFile("/Users/s/Documents/data/fdroid_corpus/index/index.xml")
    val b: NodeSeq = fdroid_index \\ "fdroid" \\ "application"
    val games_with_no_native_code = b.flatMap((a : Node) => {
      val source = (a \\ "source").text
      val id = (a \\ "id").text
      val lastupdated = (a \\ "lastupdated").text
      val name = (a \\ "name").text
      val web = (a \\ "web").text
      val category = ( a \\ "category").text
      val seq: NodeSeq = a \\ "apkname"
      val apkname = seq.text
      val srcname = (a \\ "srcname").text
      val latest_package = (a \\ "package").sortBy( a => {(a \\ "versioncode").text}).reverse.head
      val latest_package_versioncode = (latest_package \\ "versioncode").text
      val native_code_latest_package = (latest_package \\ "nativecode").text
      val latest_package_apks = (latest_package \\ "apkname")
      assert(latest_package_apks.length == 1)
      val latest_package_apk = latest_package_apks.text
      val latest_package_srcs = (latest_package \\ "srcname")
      if(latest_package_srcs.length > 1){
        println(latest_package_srcs.length)
        ???
      }
      val latest_package_src = latest_package_srcs.text
      val latest_package_sha = (latest_package \\ "hash").text



      if(category == fcategory && native_code_latest_package == "" && latest_package_srcs.length != 0){
        println(id)
        //downloadAPK("/Users/s/Documents/data/fdroid_science_edu_corpus/apps", id, latest_package_versioncode, a, latest_package, latest_package_apk, latest_package_src, latest_package_sha)
        Some(1)
      }else{
        None
      }
    })
    println(games_with_no_native_code.length)

  }
  def makeDirIfNotExist(path: String): File ={
    val folder = new File(path)
    if(!folder.exists()){
      folder.mkdir()
    }
    folder
  }
  def downloadAPK(baseDir: String, id: String, versionCode: String, appNode: Node, packageNode: Node, apk: String, src: String, apkSha: String): Unit ={

    //make directory for application
    val applicationDir = baseDir + File.separator + id
    val folder = new File(applicationDir)
    if(!folder.exists()){
      folder.mkdir()
    }

    //write application data to meta.txt
    XML.save(applicationDir + File.separator + "meta.txt", appNode, "UTF-8")

    //make directory for package
    val packageDir = applicationDir + File.separator + versionCode
    val app_package = new File(packageDir)
    if(!app_package.exists()){
      app_package.mkdir()
    }

    //write complete package data
    XML.save(packageDir + File.separator + "meta.txt", packageNode, "UTF-8")

    val apkDir = packageDir + File.separator+ "apk"
    val apkDirFile = makeDirIfNotExist(apkDir)

    //download apk if not exist
    val apkPath = apkDir + File.separator + apk
    if(apkDirFile.listFiles().length == 0){
      Utils.downloadFile("https://f-droid.org/repo/" + apk, apkPath)
    }
    val filesha: String = Utils.sha256(apkPath)
    if(filesha != apkSha){
      println("sha different: " + apkPath)
      (new File(apkPath).delete())
    }

    val srcDir = packageDir + File.separator + "src"
    val srcDirFile = makeDirIfNotExist(srcDir)

    //download src if not exist
    if(srcDirFile.listFiles().length == 0){
      Utils.downloadFile("https://f-droid.org/repo/" + src, srcDir + File.separator + src)
    }
  }

}
