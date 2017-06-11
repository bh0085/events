

$(

    function(){

	$.each($(".typeahead"),function(i,e){
	    // Using YQL and JSONP
	    console.log("URL")
	    console.log( $(e).attr("typeahead"))
	    $.ajax({

		
		url: $(e).attr("typeahead"),
		
		// The name of the callback parameter, as specified by the YQL service
		jsonp: "callback",
		
		// Tell jQuery we're expecting JSONP
		dataType: "json",
		
		
		// Work with the response
		success: function( json ) {
		    // constructs the suggestion engine

		   
		    console.log(json)
		    var items = new Bloodhound({
			datumTokenizer: Bloodhound.tokenizers.whitespace,
			queryTokenizer: Bloodhound.tokenizers.whitespace,
			// `states` is an array of state names defined in "The Basics"
			local: json
		    });

		    $(e).typeahead({
			hint: true,
			highlight: true,
			minLength: 1
		    },
				   {
				       name: 'items',
				       source: items
				   });
		    

		}
	    });	    
	})



	    $.each($(".alternates"),function(i,e){
		var fieldname=$(e).attr("contains")
		var altfield = $(e).attr("alternates")
		var alttrigger = $(e).attr("alttrigger")

		var trigger_inp = $('[name="'+$(e).attr("alttrigger")+'"]')
		var alt_el = $('[contains="'+altfield+'"]')

		var trigger_val = $(e).attr("alttriggervalue")
		var thisfield = $(e)

		console.log(trigger_inp)
		console.log(altfield)
		
		
		$(trigger_inp).on("change",function(){
		    console.log("changing")
		    console.log($(trigger_inp).val())
		    console.log(trigger_val)
		    if($(trigger_inp).val() == trigger_val){
			thisfield.toggleClass("hidden",false)
			alt_el.toggleClass("hidden",true)
		    } else{
			thisfield.toggleClass("hidden",true)
			alt_el.toggleClass("hidden",false)
		    }
		})
		
		$(e).on("change",function(){

		    val = $(e).find("input").filter('[name="'+fieldname+'"]').val()
		    console.log(fieldname)
		    thisel=  $(e).find("input").filter('[name="'+fieldname+'"]')
		    console.log(val)
		    alt_el.find("input").val(val)
		    ae = alt_el.find("input")
		})
		$(trigger_inp).trigger("change")

	    })
		
		
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
		    window.location.href = '/bookings/event/'+data.id; //relative to domain
		}
		
	    )

	    
	    return false
	})
    });




