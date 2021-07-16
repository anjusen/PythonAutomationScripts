#this code downloads the rootfs.tar.gz
#input is the date to be compared, it downloads the next successful build from the given date 

import urllib2
import time

linkUseful = "";
response = urllib2.urlopen("http://ma35ccs02.arrisi.com:8080/view/EOSBuildView/job/EOSBuild_7252x_multi/")
page_source = response.read()
#just taking the part which has build history
page_source = page_source.split("build-row-cell", 1)[1];
parts = page_source.split("build-row-cell");
for p in parts:
	p=p.split("<img")[1];
	icon = p.split("/>", 1)[0];
	if(icon.split("alt=\"", 1)[1].split(" ", 1)[0].lower() != "failed"):
		linkFull = p.split("build-link\"", 1)[1].split("</a>", 1)[0];
		linkParts = linkFull.split(">");
		date = linkParts[1];
		link = linkParts[0].split("=\"", 1)[1].split("\"", 1)[0];
		date = date.replace(",", "");
		date = time.strptime(date, "%d %b %y %H:%M %p")
		dateToComp = time.strptime("Sep 22 2015 9:42 AM", "%d %b %y %H:%M %p") #change this date according your requirement
		if(dateToComp.tm_year < date.tm_year or dateToComp.tm_mon<date.tm_mon or dateToComp.tm_mon<date.tm_mon or dateToComp.tm_hour<date.tm_hour or dateToComp.tm_min<date.tm_min):
			linkUseful = link
		else:
			break
print linkUseful	

response = urllib2.urlopen("http://ma35ccs02.arrisi.com:8080" + linkUseful)
page_source = response.read()
page_source = page_source.split("configuration-matrix", 1)[1];
parts = page_source.split("</tr>");
for p in parts:
	cols = p.split("<td");
	if("alt=\"Success\"" in cols[4]):  #cols[4] is rescueloader column
		linkUseful = linkUseful + cols[4].split("href=\"", 1)[1].split("\"", 1)[0]
		break
print linkUseful

response = urllib2.urlopen("http://ma35ccs02.arrisi.com:8080" + linkUseful)
page_source = response.read()
page_source = page_source.split("class=\"fileList\"", 1)[1].split("</table>", 1)[0];
parts = page_source.split("</tr>");
for p in parts:
	cols = p.split("<td");
	if(".pkg" in cols[2]):
		pkg = linkUseful + cols[2].split("href=\"")[1].split("\"")[0]
	if("rootfs.tar.gz" in cols[2]):
		root = linkUseful + cols[2].split("href=\"")[1].split("\"")[0]
		break

print pkg
print root

#downloading part
#download path is not defined, deafault - bin folder of python in Automoto
url = "http://ma35ccs02.arrisi.com:8080" + root #change root to pkg to download the pkg file.

file_name = url.split('/')[-1]
u = urllib2.urlopen(url)
f = open(file_name, 'wb')
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0])
print "Downloading: %s Bytes: %s" % (file_name, file_size)

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    #status = status + chr(8)*(len(status)+1)
    #print status,

print "Download completed"
f.close()
