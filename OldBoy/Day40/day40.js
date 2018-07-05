function hello() {
	alert("hello world");
}

function func1() {
	history.forward();
}

function func2() {
	history.back();
}

function func3() {
}

function funcOnAdd() {
	var ele = document.getElementById("main");
	var elep = document.createElement("p");
	elep.innerHTML = "helloWorld";
	ele.appendChild(elep);
}

for (var i = 1; i <= 9; i++) {
	setTimeout(function timer() {
		console.log(i);
	}, 1000)
}