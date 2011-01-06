
 /**
 * @name BoundsBox
 * @author Esa
 * @copyright (c) 2009 Esa I Ojala
 * @fileoverview BoundsBox is an extension to Gmaps api v3 for creating rectangle overlays.
 * Facilities to create and change image overlays and control opacity and zIndex are provided.
 * Events: click, imageloaded and imageloaderror
 */

/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

 /**
 * @version 1.1b
 * 1.1b getPosition() added, get_position() deprecated
 * 1.1 KmBox constructor added
 * 1.0 image handling, opacity and zIndex were added
 * 0.1 first release
 */
var BOUNDS_BOX_VERSION = "1.1b";

/**
 * @constructor BoundsBox()
 * @extends OverlayView
 * @param {Map} map The map where the BoundsBox shall be overlayed
 * @param {LatLngBounds} bounds Bounds of the overlay
 * @param {Object} opt_options Optional object. Supported properties: html, className, fit, imageSrc, pane, zIndex
 */
function BoundsBox(map, bounds, opt_options) {
  this.bounds_ = bounds;
  this.setMap(map);
  this.opts = opt_options || {};
  if(this.opts.fit) map.fitBounds(bounds);
  this.map = map;
};
BoundsBox.prototype = new google.maps.OverlayView();
/**
 * @private Map calls draw() internally when needed
 */
BoundsBox.prototype.draw = function() {
  var me = this;
  var div = this.div_;
  var image = this.image_;
  if (!div) { // sets the div only when draw() is called first time
    div = this.div_ = document.createElement('div');
    div.style.position = "absolute";
    div.style.overflow = "hidden";
    this.zIndex = this.opts.zIndex || 0;
    div.style.zIndex = this.zIndex;
    div.className = this.opts.cssClass || this.opts.className || 'bounds-box';
    div.innerHTML = this.opts.html || "";
    google.maps.event.addDomListener(div, "click", function(event) {
      google.maps.event.trigger(me, "click", event);
    });
    var panes = this.getPanes();
    var paneId = this.opts.pane || "overlayLayer";
    panes[paneId].appendChild(div);
    if(this.opts.imageSrc){
      image = this.image_ = new Image();
      image.src = this.opts.imageSrc;
      image.alt = "";
      image.onload = function(){
        google.maps.event.trigger(me, "imageloaded");
      }
      image.onerror = function(){
        google.maps.event.trigger(me, "imageloaderror");
      }
      div.appendChild(image);
    }
    this.opacity = this.opts.opacity * 1 || 1;
    this.div_.style.filter = 'alpha(opacity:' + this.opacity*100 + ')';
    this.div_.style.opacity = this.opacity;
  } // Positions and dimensions the overlay every time draw() is called
  var pixSW = this.getProjection().fromLatLngToDivPixel(this.bounds_.getSouthWest());
  var pixNE = this.getProjection().fromLatLngToDivPixel(this.bounds_.getNorthEast());
  this.divSize = new google.maps.Size((pixNE.x-pixSW.x), (pixSW.y-pixNE.y));
  div.style.left = pixSW.x + 'px';
  div.style.top = pixNE.y + 'px';
  div.style.width = this.divSize.width + "px";
  div.style.height = this.divSize.height + "px";
  div.style.zIndex = this.zIndex;
  if(!!image){
    image.width = this.divSize.width;
    image.height = this.divSize.height;
  }
  this.image_ = image;
};


/**
 * Removes the div from DOM
 * @returns true if success, false if the div was not found
 */
BoundsBox.prototype.remove = function() {
  if(!this.div_) return false;
  this.div_.parentNode.removeChild(this.div_);
  this.div_ = null;
  return true;
};
/**
 * Overrides previous CSS className
 * @param {String}
 * @returns true if success, false if the div was not found
 */
BoundsBox.prototype.setClassName = function(cssClass) {
  if(!this.div_) return false;
  this.div_.className = cssClass;
  return true;
};
/**
 * Sets innerHTML of the div
 * @param {String}
 * @returns true if success, false if the div was not found
 */
BoundsBox.prototype.setContent = function(html) {
  if(!this.div_) return false;
  this.div_.innerHTML = html;
  return true;
};
/**
 * Sets src attribute of the optional image object
 * @param {String} URL of an image file
 * @returns true if success, false if the image was not found
 */
BoundsBox.prototype.setImageSrc = function(src) {
  if(!this.image_) return false;
  this.image_.src = src;
  return true;
};
/**
 * Sets a new opacity value for divs style object
 * @param number between 0...1
 * @returns true if success, false if the div was not found
 */
BoundsBox.prototype.setOpacity = function(opacity) {
  if(!this.div_) return false;
  this.div_.style.filter = 'alpha(opacity:' + opacity*100 + ')';
  this.div_.style.opacity = opacity * 1;
  this.opacity = opacity * 1;
  return true;
};
/**
 * Gives a new zIndex value for divs style object
 * @param number
 * @returns true if success, false if the div was not found
 */
BoundsBox.prototype.setZIndex = function(zIndex) {
  if(!this.div_) return false;
  this.div_.style.zIndex = zIndex;
  this.zIndex = zIndex;
  return true;
};
/**
 * @returns The center point of the div
 * @type LatLng object (null if the div was not found)
 */
BoundsBox.prototype.getPosition = function() {
  if(!this.div_) return null;
  return this.bounds_.getCenter();
};
BoundsBox.prototype.get_position = function() {  // deprecated
  if(!this.div_) return null;
  return this.bounds_.getCenter();
};
/**
 * @returns innerHTML of the div (null if the div was not found)
 * @type String
 */
BoundsBox.prototype.getContent = function() {
  if(!this.div_) return null;
  return this.div_.innerHTML;
};
/**
 * @returns Reference to the div node (null if the div was not found)
 * @type html object
 */
BoundsBox.prototype.getDiv = function() {
  if(!this.div_) return null;
  return this.div_;
};
/**
 * @returns Pixel dimensions of of the div (null if the div was not found)
 * @type Size object
 */
BoundsBox.prototype.getSize = function() {
  if(!this.div_) return null;
  return this.divSize;
};
/**
 * @returns Reference to optional image node (null if the image was not found)
 * @type Image object
 */
BoundsBox.prototype.getImage = function() {
  if(!this.image_) return null;
  return this.image_;
};
/**
 * @returns The current CSS className of the div (null if the div was not found)
 * @type String
 */
BoundsBox.prototype.getClassName = function() {
  if(!this.div_) return null;
  return this.div_.className;
};
/**
 * @returns The current zIndex value (null if the div was not found)
 * @type number
 */
BoundsBox.prototype.getZIndex = function() {
  if(!this.div_) return null;
  return this.zIndex;
};
/**
 * @returns Bounds of the overlay
 * @type LatLngBounds object
 */
BoundsBox.prototype.getBounds = function() {
  return this.bounds_;
};
/////////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * destinationLatLng() method for LatLng
 * Calculates destination point from this point towards bearing (deg) in distance (km)
 * @param {number} bearing The direction in degrees
 * @param {number} dist Distance from this point in kilometers
 * @returns destination point
 * @type LatLng object
 */

google.maps.LatLng.prototype.destinationLatLng = function(bearing, dist) {
  var R = 6371; // earth's mean radius in km
  var toRad = Math.PI/180;
  var lat1 = this.lat() * toRad;
  var lng1 = this.lng() * toRad;
  bearing = bearing * toRad;
  var lat2 = Math.asin( Math.sin(lat1)*Math.cos(dist/R) +
                        Math.cos(lat1)*Math.sin(dist/R)*Math.cos(bearing) );
  var lng2 = lng1 + Math.atan2(Math.sin(bearing)*Math.sin(dist/R)*Math.cos(lat1),
                               Math.cos(dist/R)-Math.sin(lat1)*Math.sin(lat2));
  lng2 = (lng2+Math.PI)%(2*Math.PI) - Math.PI;  // normalise to -180...+180
  var pint = new google.maps.LatLng(lat2 / toRad, lng2 / toRad);
  return pint;
}
//////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * @constructor KmBox()
 * @extends OverlayView
 * @param {Map} map The map where the KmBox shall be overlayed
 * @param {number} kmX Width of the overlay in kilometers
 * @param {number} kmY Optional height of the overlay in kilometers. Default = kmX
 * @param {Object} opt_options Optional object. Supported properties: html, className, fit, imageSrc, pane, zIndex, kmX, kmY, miX, miY
 */

function KmBox(map, point, opt_options) {
  this.opts = opt_options || {};
  var kmX = this.opts.kmX || this.opts.miX * 1.609344 || 1;
  var kmY = this.opts.kmY || this.opts.miY * 1.609344 || kmX;
  var west = point.destinationLatLng(270, kmX / 2).lng();
  var east = point.destinationLatLng(90, kmX / 2).lng();
  var north = point.destinationLatLng(0, kmY / 2).lat();
  var south = point.destinationLatLng(180, kmY / 2).lat();
  this.bounds_ = new google.maps.LatLngBounds(); 
  this.bounds_.extend(new google.maps.LatLng(south, west));
  this.bounds_.extend(new google.maps.LatLng(north, east));
  this.setMap(map);
  if(this.opts.fit) map.fitBounds(this.bounds_);
  this.map = map;
};

/**
 * Clone all the methods of BoundsBox()
 */
KmBox.prototype = BoundsBox.prototype;