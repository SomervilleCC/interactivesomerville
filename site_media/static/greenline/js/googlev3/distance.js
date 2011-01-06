/**
 * A distance widget that will display a circle that can be resized and will
 * provide the radius in km.
 *
 * @param {google.maps.Map} map The map on which to attach the distance widget.
 *
 * @constructor
 */
function DistanceWidget(map) {
  this.set('map', map);
  this.set('position', map.getCenter());

  var marker = new google.maps.Marker({
    draggable: true,
    title: 'Move me!'
  });

  // Bind the marker map property to the DistanceWidget map property
  marker.bindTo('map', this);

  // Bind the marker position property to the DistanceWidget position
  // property
  marker.bindTo('position', this);
}
DistanceWidget.prototype = new google.maps.MVCObject();