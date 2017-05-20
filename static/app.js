console.log("HI")

$(
    function(){
	console.log("HELLO WORLD")
	$("#edit-event").submit(function(ev){
	    $.post($("#edit-event").attr("action"),$( "#edit-event" ).serialize())

	    return false
	})
    });


