

$(

    function(){
	console.log("HELLO WORLD")
	/*
	$("input.time").timeAutocomplete({
	    increment:30,
	    formatter:"ampm",
	});
	*/
	
	$("#edit").click(function(){
	    console.log("EDITING")
	    $("#main-editable").removeClass("view-mode").addClass("edit-mode")
	    $("input:disabled").prop("disabled",false)
	    $("select:disabled").prop("disabled",false)
	    $("textarea:disabled").prop("disabled",false)

	})
	
	$("#edit-event").submit(function(ev){
	    var data = 	$( "#edit-event" ).serialize()
	    	    
	    $.post(
		$("#edit-event").attr("action"),
		data,
		function(data){
		    location.reload()
		}
	    )
	    
	   		
	    return false
	})

	
	$("#delete").click(function(){
	    c = confirm("Are you sure you want to delete this event?")
	    if(c){
		$.post(
		    $("#delete").attr("target"),
		    {},
		    function(data){
			window.location.href="/bookings/"
		    })
		
	    }
	})

	$("#new-event").submit(function(ev){
	    var data = 	$( "#new-event" ).serialize()
	    $.post(
		$("#new-event").attr("action"),
		data,
		function(data){
		    console.log("HELLO!!")
		    console.log(data)
		    window.location.href = '/bookings/event/'+data.id; //relative to domain
		}
		
	    )

	    
	    return false
	})
    });




