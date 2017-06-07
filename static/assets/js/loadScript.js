function getData(query, date1, date2) {
	$.post("results", {query:query, date1:date1, date2:date2}, function(html));
	$("div#results").html(html);
}