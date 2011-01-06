// Google Maps Javascript API version 3 

function createGeocoderControl() {
    var control = document.createElement('input');
    control.style.fontSize = '10pt';
    control.style.margin = '5px';
    control.onkeyup = submitGeocode(control);
    control.style.color = "#808080";
    control.value = "Enter location...";
    control.onfocus = function() {
      control.style.color = "#000000";
      control.value = "";
    }
    control.onblur = function() {
      control.style.color = "#808080";
      control.value = "Enter location...";
    }
    map.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(control);
  }
  
function submitGeocode(control) {
    return function(e) {
      var keyCode;
    
      if (window.event) {
        keyCode = window.event.keyCode;
      } else if (variable) {
        keyCode = e.which;
      }
    
      if (keyCode == 13) {
        geocoder.geocode( { address: control.value }, function(results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
            map.fitBounds(results[0].geometry.viewport);
          } else {
            alert("The location entered could not be found");
          }
        })
      }
    }
  }

function codeAddress() {
  var address = document.getElementById("address").value;
  if (geocoder) {
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
            map: map, 
            position: results[0].geometry.location
        });
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
  }
}

function codeLatLng() {
  var input = document.getElementById("latlng").value;
  var latlngStr = input.split(",",2);
  var lat = parseFloat(latlngStr[0]);
  var lng = parseFloat(latlngStr[1]);
  var latlng = new google.maps.LatLng(lat, lng);
  
  if (geocoder) {
    geocoder.geocode({'latLng': latlng}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        if (results[1]) {
          map.setZoom(11);
          marker = new google.maps.Marker({
              position: latlng, 
              map: map
          }); 
          infowindow.setContent(results[1].formatted_address);
          infowindow.open(map, marker);
        } else {
          alert("No results found");
        }
      } else {
        alert("Geocoder failed due to: " + status);
      }
    });
  }
}
