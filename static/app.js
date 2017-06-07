

$(

    function(){
	console.log("HELLO WORLD")
	/*
	$("input.time").timeAutocomplete({
	    increment:30,
	    formatter:"ampm",
	});
	*/

	$.each(group_defs,function(k,e){
	    if(e.triggertype=="selection"){
		var tgt = $('[name="'+e.triggername+'"]')
		var val = e.triggervalue
		var dst = $('.grp-'+k)

		tgt.on("change",function(){
		    if(tgt.val() == val){
			dst.toggleClass("hidden",false)
		    }else{
			dst .toggleClass("hidden",true)
		    }
		})
		tgt.trigger("change")
	    }
	    if(e.triggertype=="any"){
		var tgt = $('[name="'+e.triggername+'"]')
		var val = e.triggervalue
		dst = $('.grp-'+k)
		console.log(dst)

		tgt.on("change",function(){
		    if(tgt.val() != ""){
			dst.toggleClass("hidden",false)
			$(dst).find("input").val(tgt.val())
		    }else{
			dst.toggleClass("hidden",true)
		    }
		})
		tgt.trigger("change")
	    }
	})
	
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




