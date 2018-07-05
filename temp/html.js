/**
 *
 */

/*
 * function adda(a, b) { alert(a + b) } var a = 1; var b = 2;
 *
 * adda(a, b); console.log(a); console.log(b); document.write(a);
 *
 * function printstr(a) {
 *
 * if (a instanceof String) { alert("String") } else { alert("No String") } }
 *
 * printstr(String("hehi"))
 *
 * var s = "hahaE1E2E3"; console.log(s.search("1")); console.log(s.match("E"));
 * console.log(s.match("E")[0]);
 */

function getTime() {
	var data_obj = new Date();
	return data_obj.getMinutes() + ":" + data_obj.getSeconds();
}

function begin() {
	var stime = getTime();
	var ret = document.getElementById("clock");
	ret.value = stime;
}

function funmouseover() {
	console.log("mmp");
	if (!document.getElementById("imageContent")) {
		var ky = document.getElementById("imageShow");
		var image = document.createElement("img");
		image.src = "1.jpg";
		image.id = "imageContent"
		ky.appendChild(image);
	}
}

function funmouseremove() {
	if (document.getElementById("imageContent")) {
		var ky = document.getElementById("imageShow");
		var image = document.getElementById("imageContent");
		ky.removeChild(image);
	}
}
/*

var ID = setInterval(begin, 1000);
var ele = document.getElementById("alexid");
console.log(ele.innerHTML);
*/

function funOnFocus() {
	var ky = document.getElementById("username");
	ky.value = "";
}

function funOnFlur() {
	var ky = document.getElementById("username");
	var content = ky.value;
	if (ky.value.length == 0) {
		ky.value = "请输入用户名";
	}
}

function show() {
	var eles = docment.getElementsByClassName("domodelDlg");
	for (var index = 0; index < eles.length; index++) {
		eles.classList.remove("hide");
	}
}