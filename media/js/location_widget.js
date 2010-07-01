postcode_re = new RegExp('^[A-Za-z]{1,2}[0-9]{1,2}( ?[0-9][A-Za-z]{2})?$');
google.load("maps", "3", {'other_params':'sensor=true'});
google.load("search", "1")


function LocationWidget() {

    function rad2deg(radians) { return 360*radians/(2*Math.PI); }

    function place_marker(latLng) {
        // Put a marker on the map, centre and zoom appropriately
        user_marker = new google.maps.Marker( {position:latLng, map:user_map, draggable:true} )
        user_map.setCenter(latLng);
        user_map.setZoom(7);
        // Update the inputs when user drags the marker
        google.maps.event.addListener(user_marker, 'dragend', function() {
            update_latlng_inputs(this.getPosition());
        })
    }

    function update_latlng_inputs(latlng) {
        lat_input.val(latlng.lat());
        lng_input.val(latlng.lng());
    }

    function postcode_keydown(e) {
        // Submit the postcode when the user presses enter
        var key = e.keyCode ? e.keyCode:e.which;
        if (key==13) {
            return submit_postcode();
        } else return true;
    }

    function submit_postcode() {
        postcode = form.find('input#postal_code').val();
        if (postcode_re.test(postcode)) {
            var localSearch = new google.search.LocalSearch();
            localSearch.setSearchCompleteCallback(null,
                function() {
                    if (localSearch.results[0]) {
                        var latlng= new google.maps.LatLng(localSearch.results[0].lat, localSearch.results[0].lng);
                        if (user_marker) {
                            user_marker.setPosition(latlng);
                        } else {
                            place_marker(latlng);
                        }
                        update_latlng_inputs(latlng);
                        user_map.setCenter(latlng);
                        user_map.setZoom(7);
                    }else{
                        alert("Postcode not found!");
                    }
                });
            localSearch.execute(postcode + ", UK");
        } else {
            alert("Please enter a valid postcode.");
        }
        return false;
    }


    var lat_input=$('input#id_latitude');
    var lng_input=$('input#id_longitude');
    var lat = parseFloat(lat_input.val());
    var lng = parseFloat(lng_input.val());

    var user_map;
    var map_centre = new google.maps.LatLng(54.2, -2);
    var map_zoom = 5;
    var marker_position = null;
    var user_marker;

    if (isNaN(lat) || isNaN(lng)) {
        // Try to use browser based geolocation
        if(navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                marker_position = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
                if (!user_marker) {
                    place_marker(marker_position);
                    map_centre = marker_position;
                    map_zoom = 7;
                }
            })
        }
    } else {
        marker_position = new google.maps.LatLng(parseFloat(lat), parseFloat(lng))
        map_centre = marker_position;
        map_zoom = 7;
    }

    var form=$(lat_input.get(0).form);

    // Hide the lat and lon inputs and intro text
    lat_input.parent('p').hide();
    lng_input.parent('p').hide();
    form.find('p#latlon_text').hide();

    // Put up some appropriate text and the map widget
    if (lat_input.val()) {
        lat_input.parent('p').before('<p>The map below indicates your location. To change your location drag the marker to your preferred location, or enter your postcode in the box below.</p>');
    } else {
        lat_input.parent('p').before("<p>In order to allow you to find other people's items, and to allow other people to find your items, please place a marker on the map and drag it to your location, or enter your postcode in the box below.</p>");
    }
    lng_input.parent('p').after('<div id="map_canvas" style="width: 300px; height: 300px"></div>');
    lng_input.parent('p').after('<p><label for="postal_code">Postcode:</label><input id="postal_code" type="text" /><a href="" id="submit_postcode">Use postcode</a></p>');


    var myOptions = {
      zoom: map_zoom,
      center: map_centre,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      mapTypeControl: false
    };
    user_map = new google.maps.Map(form.find('#map_canvas').get()[0], myOptions);


    if (marker_position == null) {
        var clickListener = google.maps.event.addListenerOnce(user_map, 'click', function(event) {
            if (!user_marker) {
                place_marker(event.latLng);
                update_latlng_inputs(event.latLng);
            }
        });
    } else {
        // If we've got co-ordinates already, place the marker on the map
        place_marker(marker_position);
    }

    form.find('#submit_postcode').click(submit_postcode);
    form.find('input#postal_code').keydown(postcode_keydown);
}

google.setOnLoadCallback(function() {
    widget = new LocationWidget();
});

