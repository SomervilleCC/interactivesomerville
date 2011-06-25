// global greenline object
var greenline = {
	infobubble: {
		station: new InfoBubble({maxWidth: 400, minborderWidth: 2, borderColor: '#4F7B41'}),
		photo: new InfoBubble({maxWidth: 400, minborderWidth: 2, borderColor: '#4F7B41'})
	}
};

greenline.createBasemap = function () {
	
	// map
	greenline.map = new google.maps.Map(document.getElementById("map"));

	// simple map style
	var simple_style =  [
		{
			featureType: "administrative",
			elementType: "geometry",
			stylers: [
				{ visibility: "off" }
			]
		},{
			featureType: "administrative",
			elementType: "labels",
			stylers: [
				{ visibility: "on" },
				{ hue: "#d70000" },
				{ lightness: 10 },
				{ saturation: -95 }
			]
		},{
			featureType: "landscape",
			elementType: "all",
			stylers: [
				{ visibility: "off" }
			]
		},{
			featureType: "poi",
			elementType: "geometry",
			stylers: [
				{ visibility: "off" }
			]
		},{
			featureType: "poi",
			elementType: "labels",
			stylers: [
				{ visibility: "on" },
				{ hue: "#d70000" },
				{ lightness: 10 },
				{ saturation: -95 }
			]
		},{
			featureType: "transit",
			elementType: "all",
			stylers: [
				{ visibility: "off" }
			]
		},{
			featureType: "transit.line",
			elementType: "geometry",
			stylers: [
				{ hue: "#ff0000" },
				{ visibility: "on" },
				{ lightness: -20 }
			]
		},{
			featureType: "road",
			elementType: "geometry",
			stylers: [
				{ hue: "#d70000" },
				{ visibility: "simplified" },
				{ lightness: 10 },
				{ saturation: -95 }
			]
		},{
			featureType: "road",
			elementType: "labels",
			stylers: [
				{ visibility: "off" }
			]
		},{
			featureType: "water",
			elementType: "geometry",
			stylers: [
				{ visibility: "on" },
				{ hue: "#0091ff" },
				{ lightness: 30 },
				{ saturation: -100 }
			]
		},{
			featureType: "water",
			elementType: "labels",
			stylers: [
				{ visibility: "off" }
			]
		}
	];
	
	var simple_options = {
		name: "Simple"
	}
	
	var simple = new google.maps.StyledMapType(simple_style, simple_options);
	
	greenline.map.mapTypes.set("simple", simple);
	greenline.map.setMapTypeId("simple");
	greenline.map.streetViewControl = false;
	greenline.map.setOptions({
		mapTypeControlOptions: {
			position: google.maps.ControlPosition.TOP_RIGHT,
			mapTypeIds: ["simple",google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.SATELLITE],
			style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
		},
		panControl: false,
		zoomControlOptions: {
			style: google.maps.ZoomControlStyle.SMALL
		},
	});
	
}

// requires 3rd party infobubble lib http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobubble/
greenline.createInfoBubble = function (type, marker, contentstring) {
	google.maps.event.addListener(marker, 'click', function() {
		greenline.infobubble[type].setContent(contentstring);
		greenline.infobubble[type].open(greenline.map, marker);
	});
}

// encoded polylines for google maps
greenline.decodeLevels = function (encodedLevelsString) {
	var decodedLevels = [];
	for (var i = 0; i < encodedLevelsString.length; ++i) {
		var level = encodedLevelsString.charCodeAt(i) - 63;
		decodedLevels.push(level);
	}
	return decodedLevels;
}

