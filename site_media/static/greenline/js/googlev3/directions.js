  var directionDisplay;
  var directionsService = new google.maps.DirectionsService();
  var directionsDisplay = new google.maps.DirectionsRenderer();
  var origin = null;
  var destination = null;
  var waypoints = [];
  var markers = [];
  var directionsVisible = false;

  function initialize() {
    directionsDisplay = new google.maps.DirectionsRenderer();
    var chicago = new google.maps.LatLng(37.7749295, -122.4194155);
    var myOptions = {
      zoom:13,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      center: chicago
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    directionsDisplay.setMap(map);
    directionsDisplay.setPanel(document.getElementById("directionsPanel"));
    
    google.maps.event.addListener(map, 'click', function(event) {
      if (origin == null) {
        origin = event.latLng;
        addMarker(origin);
      } else if (destination == null) {
        destination = event.latLng;
        addMarker(destination);
      } else {
        if (waypoints.length < 9) {
          waypoints.push({ location: destination, stopover: true });
          destination = event.latLng;
          addMarker(destination);
        } else {
          alert("Maximum number of waypoints reached");
        }
      }
    });
  }

  function addMarker(latlng) {
    markers.push(new google.maps.Marker({
      position: latlng, 
      map: map,
      icon: "http://maps.google.com/mapfiles/marker" + String.fromCharCode(markers.length + 65) + ".png"
    }));    
  }

  function calcRoute() {
    if (origin == null) {
      alert("Click on the map to add a start point");
      return;
    }
    
    if (destination == null) {
      alert("Click on the map to add an end point");
      return;
    }
    
    var mode;
    switch (document.getElementById("mode").value) {
      case "bicycling":
        mode = google.maps.DirectionsTravelMode.BICYCLING;
        break;
      case "driving":
        mode = google.maps.DirectionsTravelMode.DRIVING;
        break;
      case "walking":
        mode = google.maps.DirectionsTravelMode.WALKING;
        break;
    }
    
    var request = {
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        travelMode: mode,
        optimizeWaypoints: document.getElementById('optimize').checked,
        avoidHighways: document.getElementById('highways').checked,
        avoidTolls: document.getElementById('tolls').checked
    };
    
    directionsService.route(request, function(response, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
      }
    });
    
    clearMarkers();
    directionsVisible = true;
  }
  
  function updateMode() {
    if (directionsVisible) {
      calcRoute();
    }
  }
  
  function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(null);
    }
  }
  
  function clearWaypoints() {
    markers = [];
    origin = null;
    destination = null;
    waypoints = [];
    directionsVisible = false;
  }
  
  function reset() {
    clearMarkers();
    clearWaypoints();
    directionsDisplay.setMap(null);
    directionsDisplay.setPanel(null);
    directionsDisplay = new google.maps.DirectionsRenderer();
    directionsDisplay.setMap(map);
    directionsDisplay.setPanel(document.getElementById("directionsPanel"));    
  }
</script>
