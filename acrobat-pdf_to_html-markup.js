<!--
/*
================ Status

This file is outdated!!!!!!!!
I am now using a python script to extract annotations from Zotero/Zotfile.
It is was not possible to get a good enough quality extraction with Acrobat Pro.

================ Concept

An Acrobat Pro JavaScript script that extract annotations from an pdf and write a html formatted txt file (only .txt can be written from within Acrobat Pro).

================ Inspiration

Main inspiration: <http://valeriobiscione.com/2014/07/22/copy-highlighted-text-into-comments-from-a-pdf-file/>
Save to file <https://stackoverflow.com/questions/35001831/how-to-check-multiple-pdf-files-for-annotations-comments>
Print all annots <https://franciscomorales.org/2012/10/18/how-to-extract-highlighted-text-from-a-pdf-file/>
Save file without dialogue <http://stackoverflow.com/questions/17422514/how-to-write-a-text-file-in-acrobat-javascript>

*/
//-->>

var annots = this.getAnnots({nSortBy: ANSB_Page});
var file = this.documentFileName
var segments = file.split(".");
segments.splice(segments.length-1, 1);
var fname = segments.join("."); 
fname = fname.replace(",", ";");
var rightNow = new Date();
var dateRun = util.printd("yyyymmdd",rightNow); 
var mDate = util.printd("yyyymmdd",this.info.modDate); 


var htmlString = "<html><head><meta pages=" + this.numPages + " dateRun=" + dateRun + " dateMod=" + mDate + " filePath='" + this.path + "' fileName='" + file + "'><title>" + file + "</title><link rel='stylesheet' type='text/css' href='http://ma3x.com/repo/style-lib.css'></head><body>";

htmlString = htmlString + "<div id='top'><p>file: <a href='" + file + "' target='_blank'>" + file + "</a><br/>pages: " + this.numPages + " / run date: " + dateRun + "</p></div>";

if ( annots != null ) {
	var annotList=[];
	for (var i = 0; i < annots.length;i++) {
				var pageNum= annots[i].page;
				var myNum = pageNum + 1;
				if (annots[i].type=="Text" && annots[i].subject=="Sticky Note") {
					htmlString = htmlString + "<div class='note' editor='"+ annots[i].author  +"' order="+ i +" page="+ myNum +"><p id='refString'>" + file + " : " + myNum + "</p><p id='comment'>" + annots[i].contents.replace(/^\s+|\s+$/gm,'') + "</p></div>";
					continue;
				}
        if (annots[i].type!="Highlight" && annots[i].type!="Underline") {
						continue;
        }
        var annotTxt="";
        var quadAN=annots[i].quads.toString();
        var qaAN=quadAN.split(",");
        for (var ii=0; ii<qaAN.length; ii++) {
            qaAN[ii]=parseFloat(qaAN[ii]);
        }
        for (var w=0; w<getPageNumWords(pageNum); w++) {
            var quadWD=getPageNthWordQuads(pageNum,w).toString();
            //console.println("QWD TYPE: " + typeof quadWD + ": " + quadWD)
            var qaWD=quadWD.split(",");
            for (var ii=0; ii<qaWD.length; ii++) {
                qaWD[ii]=parseFloat(qaWD[ii]);
            }
            var nlines=qaAN.length/8; counter=0;
            for (var nn=0; nn<nlines; nn++) {
                if (qaWD[0]>=qaAN[counter+0]-4.5 &&
                    qaWD[1]<=qaAN[counter+1]+0.5 &&
                    qaWD[2]<=qaAN[counter+2]+4.5 &&
                    qaWD[3]<=qaAN[counter+3]+0.5 &&
                    qaWD[4]>=qaAN[counter+4]-4.5 &&
                    qaWD[5]>=qaAN[counter+5]-0.5 &&
                    qaWD[6]<=qaAN[counter+6]+4.5 &&
                    qaWD[7]>=qaAN[counter+7]-0.5) {
                    annotTxt=annotTxt+" "+getPageNthWord(pageNum,w);
                }
            counter=counter+8;
            }
        counter=0;
        }
		annotTxt = annotTxt.replace(/^\s+|\s+$/gm,'');
		var orgContent = annots[i].contents.replace(/^\s+|\s+$/gm,'');
		htmlString = htmlString + "<div class='"+ annots[i].type +"' editor='"+ annots[i].author  +"' order="+ i +" page="+ myNum +" ><p id='refString'>" + file + " : " + myNum + "</p><p id='content" + annots[i].type + "'>" + annotTxt + "</p>";
		if (annots[i].contents  && (orgContent.substring(0, 6) != annotTxt.substring(0, 6))){
			//content is a personal note and should be brought forward
			htmlString = htmlString + "<p id='comment'>" + orgContent + "</p></div>";
		} else {
			//console.println("....");
			htmlString = htmlString + "</div>";
		}
        annotTxt="<hightlight: " + i + " PAGE NUM: " + (pageNum+1) + " : " + annotTxt;
        annotList[annotList.length] = annotTxt;
	}
	htmlString = htmlString + "</body></html>";
	var textValue = htmlString;
	var TEMP_FIELD_NAME = "<!DOCTYPE html>";
	var f = this.addField(TEMP_FIELD_NAME, "text", 0, [30,30,100,20]);
	f.value = textValue;
	this.exportAsText({aFields: TEMP_FIELD_NAME, cPath: fname + "_" + dateRun + "_mark.txt"});
}


