  var route16coords = [
  new google.maps.LatLng(42.375058118208337,-71.082567161457703),
  new google.maps.LatLng(42.376686696906638,-71.084174182559735),
  new google.maps.LatLng(42.378120131319051,-71.08553374327937),
  new google.maps.LatLng(42.380889456537993,-71.087926074861315),
  new google.maps.LatLng(42.382984768644228,-71.090116202893768),
  new google.maps.LatLng(42.384656812877196,-71.091643519727683),
  new google.maps.LatLng(42.385464820331102,-71.092460210892241),
  new google.maps.LatLng(42.385946091472022,-71.09301491286828),
  new google.maps.LatLng(42.386512255085229,-71.093657819921134),
  new google.maps.LatLng(42.387098596024479,-71.094693614269005),
  new google.maps.LatLng(42.387372791347687,-71.095358868326116),
  new google.maps.LatLng(42.388426403939761,-71.097594670541397),
  new google.maps.LatLng(42.389477713297907,-71.099920743378505),
  new google.maps.LatLng(42.390208867609395,-71.101538927654858),
  new google.maps.LatLng(42.390720434931893,-71.102714786595513),
  new google.maps.LatLng(42.391098715438872,-71.103397042498429),
  new google.maps.LatLng(42.391750579502755,-71.104381877744856),
  new google.maps.LatLng(42.392403771007025,-71.105208241891916),
  new google.maps.LatLng(42.393198910798077,-71.105877718833568),
  new google.maps.LatLng(42.394533440888686,-71.106868581003795),
  new google.maps.LatLng(42.398114649718167,-71.10950272721864),
  new google.maps.LatLng(42.399272654926499,-71.110321512765012),
  new google.maps.LatLng(42.401344760133853,-71.111993500633702),
  new google.maps.LatLng(42.404485666186062,-71.114244132083556),
  new google.maps.LatLng(42.40562574680235, -71.115112183807312),
  new google.maps.LatLng(42.406878377621389,-71.116153921106203),
  new google.maps.LatLng(42.408259217475837,-71.117118898540141),
  new google.maps.LatLng(42.409180990701998,-71.117912281158922),
  new google.maps.LatLng(42.41025655826212, -71.119174001173747),
  new google.maps.LatLng(42.411369996156417,-71.120524313705062),
  new google.maps.LatLng(42.413076716251219,-71.122501558784563),
  new google.maps.LatLng(42.417136075601142,-71.127711763304205)
  ];

  var unionSqcoords = [
  new google.maps.LatLng(42.37505812, -71.08256716), 
  new google.maps.LatLng(42.37553115, -71.08658398), 
  new google.maps.LatLng(42.37582245, -71.08919319), 
  new google.maps.LatLng(42.37598757, -71.09069415),
  new google.maps.LatLng(42.37610332, -71.09152998), 
  new google.maps.LatLng(42.37630364, -71.09236526), 
  new google.maps.LatLng(42.37670262, -71.09356686), 
  new google.maps.LatLng(42.37746364, -71.09521194)
  ];

var route16 = new google.maps.Polyline({
  path: route16coords,
  strokeColor: "#022706",
  strokeOpacity: .6,
  strokeWeight: 3
});

var unionSq = new google.maps.Polyline({
  path: unionSqcoords,
  strokeColor: "#022706",
  strokeOpacity: .6,
  strokeWeight: 3
});