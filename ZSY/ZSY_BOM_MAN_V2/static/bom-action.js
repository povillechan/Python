function modifyTdEditable() {
	$("td").unbind("dblclick")
	$("[level = 'level1'] td").dblclick(function() {
		TdEditable(this)
	});

	$("[level = 'level2']").each(function() {
		$(this).children("td:gt(0)").dblclick(function() {
			TdEditable(this)
		})
	});

	$("[level = 'level3']").each(function() {
		$(this).children("td:gt(1)").dblclick(function() {
			//	console.log($(this))
			TdEditable(this)
		})
	});
}

function TdEditable(self) {
	obj_text = $(self).find("input:text"); // 判断单元格下是否有文本框
	if (!obj_text.length) // 如果没有文本框，则添加文本框使之可以编辑
	{	        
		var html_text = "<input onBlur='TdEditBlur(this)' type='text' style='margin:0 0 0 0;height:" + ($(self).outerHeight() - 20 ) + "px' value='" + $(self).text() + "'></input>"
		$(self).html(html_text);
		$(self).children().focus()
		
	} else // 如果已经存在文本框，则将其显示为文本框修改的值
	{
		$(self).html(obj_text.val());
	}
}

function TdEditBlur(self) {
	$(self).parent().html($(self).val())
}

function addBomListLevel1(bomList) {
	for (key in bomList) {
		$("#content").append('<div class="clearfix clearsection"><table border="0px"></table></div>')
		addBomListLevel2(bomList[key])
	}

	modifyEditLine()
}

function addBomListLevel2(bomList) {
	for (key in bomList) {
		var strTableItem = ""
		if (key == "名称") {
			strTableItem += '<tr level="level1"><td>' + bomList[key] + '</td>'
		} else {
			strTableItem += '<tr level="level2"><td></td>'
			strTableItem += "<td>" + key + "</td>"
			strTableItem = addBomListLevel3(bomList[key], strTableItem, key)
		}
		strTableItem += "</tr>"
		$(".clearfix table").last().append(strTableItem);
	}
}

function addBomListLevel3(bomList, strTable, mainKey) {
	strTableModify = strTable
	var key_line = false
	for (key in bomList) {

		if (!key_line) {
			for (subKey in bomList[key]) {
				strTableModify += "<td>" + subKey + "</td>"
			}
			key_line = true
		}
		strTableModify += '<tr level="level3"><td></td><td></td>'
		for (subKey in bomList[key]) {
			strTableModify += "<td>" + bomList[key][subKey] + "</td>"
		}
		strTableModify += "</tr>"
	}
	return strTableModify
}

function modifyEditLine() {
	$("button").remove()
	$("[level = 'level1']").append('<button onclick="level1del(this)">-</button>')
	$("[level = 'level1']").last().append('<button onclick="level1add(this)">+</button>')

	$("[level = 'level2']").append('<button onclick="level2del(this)">-</button>')
	$("[level = 'level2']").append('<button onclick="level2addCol(this)">//</button>')
	$("[level = 'level2']").append('<button onclick="level2delCol(this)">\\\\</button>')
	$("[level = 'level2']").parent().each(function() {
		$(this).children("tr[level = 'level2']").last().append('<button onclick="level2add(this)">+</button>')
		$(this).children("tr[level = 'level2']").last().append('<button onclick="level2BomAdd(this)">B</button>')
		$(this).children("tr[level = 'level2']").last().append('<button onclick="level2PaperAdd(this)">P</button>')
	})

	$("[level = 'level3']").append('<button onclick="level3del(this)">-</button>')
	$("[level = 'level2']").prev("[level = 'level3']").append('<button onclick="level3add(this)">+</button>')
	$("[level = 'level3']").parent().each(function() {
		$(this).children("[level = 'level3']:last").append('<button onclick="level3add(this)">+</button>')
	})
}

function level1add(self) {
	$("#content").append('<div class="clearfix clearsection"></div>')
	$(".clearfix").last().append('<tr level="level1"><td>组</td></tr>').append(
		'<tr level="level2"><td></td><td>模块</td><td>模块名</td><td>属性</td></tr>' +
		'<tr level="level3"><td></td><td></td><td>模块名</td><td>属性值</td></tr>')
	modifyTdEditable()
	modifyEditLine()
}

function level1del(self) {
	$(self).parent().parent().remove()
	modifyTdEditable()
	modifyEditLine()
}

function level2add(self) {
	var td_count = $(self).prevAll("td").length - 3
	var td_html = ""
	for (var index = 0; index < td_count; index++) {
		td_html = td_html + '<td>属性值</td>'
	}

	$(self).parent().clone().appendTo($(self).parent().parent())
	$(self).parent().parent().append(
		'<tr level="level3"><td></td><td></td><td>模块名</td>' + td_html)

	modifyTdEditable()
	modifyEditLine()
}

function level2BomAdd(self) {
	$(self).parent().parent().append(
		'<tr level="level2"><td></td><td>Bom</td><td>Bom名</td><td>版本</td></tr>' +
		'<tr level="level3"><td></td><td></td><td>Bom名称</td><td>Bom版本</td></tr>')

	modifyTdEditable()
	modifyEditLine()
}

function level2PaperAdd(self) {
	$(self).parent().parent().append(
		'<tr level="level2"><td></td><td>图纸</td><td>图纸名</td><td>版本</td></tr>' +
		'<tr level="level3"><td></td><td></td><td>图纸名称</td><td>图纸版本</td></tr>')

	modifyTdEditable()
	modifyEditLine()
}

function level2del(self) {
	$(self).parent().nextUntil('[level="level2"]').remove()
	$(self).parent().remove()

	modifyTdEditable()
	modifyEditLine()
}


function level2addCol(self) {
	$(self).parent().children("td").last().after('<td>属性</td>')
	$(self).parent().nextUntil('[level="level2"]').each(function() {
		$(this).children("td").last().after('<td>属性值</td>')
	})
	modifyTdEditable()
	modifyEditLine()
}

function level2delCol(self) {
	$(self).parent().children("td").last().remove()
	$(self).parent().nextUntil('[level="level2"]').each(function() {
		$(this).children("td").last().remove()
	})
	modifyTdEditable()
	modifyEditLine()
}

function level3add(self) {
	var item = '<tr level="level3">' + $(self).parent()[0].innerHTML + '</tr>'
	$(self).parent().after(item)

	modifyTdEditable()
	modifyEditLine()
}

function level3del(self) {
	$(self).parent().remove()

	modifyTdEditable()
	modifyEditLine()
}

function checkBomEdit() {
	$(".clearsection td").css("color", "")
	var level2_items = $('[level="level2"]')

	// level 2 names
	for (var index = 0; index < level2_items.length; index++) {
		var level2_td_items = $(level2_items.get(index)).children("td:gt(1)")
		for (var td_index = 0; td_index < level2_td_items.length; td_index++) {
			var i = $(level2_td_items.get(td_index))
			if (i.text() == "") {
				i.css("color", "red")
				$("#msg")[0].innerHTML = "属性名不能为空值";
				return false;
			}

			for (var sibling_index = td_index + 1; sibling_index < level2_td_items.length; sibling_index++) {
				var j = $(level2_td_items.get(sibling_index))
				if (i.text() == j.text()) {
					i.css("color", "red")
					j.css("color", "red")
					$("#msg")[0].innerHTML = "属性名不能重复";
					return false;
				}
			}
		}
	}

	// level 2 cols
	var level1_items = $('[level="level1"]')
	for (var index = 0; index < level1_items.length; index++) {
		var level2_items = $(level1_items.get(index)).parent().children('[level="level2"]')

		for (var td_index = 0; td_index < level2_items.length; td_index++) {
			var i = $(level2_items.get(td_index)).children("td:eq(1)")

			if (i.text() == "") {
				i.css("color", "red")
				$("#msg")[0].innerHTML = "项目名不能为空值";
				return false;
			}


			for (var sibling_index = td_index + 1; sibling_index < level2_items.length; sibling_index++) {
				var j = $(level2_items.get(sibling_index)).children("td:eq(1)")
				if (i.text() == j.text()) {
					i.css("color", "red")
					j.css("color", "red")
					$("#msg")[0].innerHTML = "项目名不能重复";
					return false;
				}
			}
		}
	}

	return true;
}

function getBomEdit() {
	var json_string = []
	var level1_items = $('[level="level1"]')
	for (var index = 0; index < level1_items.length; index++) {
		var item_json = JSON.parse("{}");
		item_json["名称"] = $(level1_items.get(index)).children("td").text()

		var level2_items = $(level1_items.get(index)).siblings('[level="level2"]')
		for (var index_2 = 0; index_2 < level2_items.length; index_2++) {
			//item_json[$(level2_items.get(index_2)).children('td:eq(1)').text()] = "haha"
			var item2_json = []
			var level2_td_items = $(level2_items.get(index_2)).children("td:gt(1)")
			var level3_items = $(level2_items.get(index_2)).nextUntil('[level="level2"]')
			for (var index_3 = 0; index_3 < level3_items.length; index_3++) {
				var item_3_json = JSON.parse("{}");
				var level3_td_items = $(level3_items.get(index_3)).children("td:gt(1)")
				for (var index_3_td = 0; index_3_td < level3_td_items.length; index_3_td++) {
					item_3_json[$(level2_td_items.get(index_3_td)).text()] = $(level3_td_items.get(index_3_td)).text()
				}
				item2_json.push(item_3_json)
			}
			item_json[$(level2_items.get(index_2)).children('td:eq(1)').text()] = item2_json
		}
		json_string.push(item_json)
	}
	console.log(JSON.stringify(json_string))
	return JSON.stringify(json_string)
} 