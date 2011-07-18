google.load("maps", "2");
google.load("search", "1");


function doLocationWidget() {
    var postcodeRe = new RegExp('^[A-Za-z]{1,2}[0-9]{1,2} ?[0-9][A-Za-z]{2}$');
    var pointRe = new RegExp('^POINT *\\( *(-?[0-9]+\\.?[0-9]*) +(-?[0-9]+\\.?[0-9]*) *\\) *$');

    function updateLatLngInputs(latLng) {
        locInput.val("POINT ("+latLng.lng()+" "+latLng.lat()+")");
    }

    function rad2deg(radians) { return 360*radians/(2*Math.PI); }

    function postcodeKeydown(e) {
        var key = e.keyCode ? e.keyCode:e.which;
        if (key==13) {
            return submitPostcode();
        } else return true;
    }

    function submitPostcode() {
        var postcode = form.find('input#postal_code').val();
        if (postcodeRe.test(postcode)) {
            var localSearch = new google.search.LocalSearch();
            localSearch.setSearchCompleteCallback(null,
                function() {
                    if (localSearch.results[0]) {
                        var latLng= new GLatLng(localSearch.results[0].lat, localSearch.results[0].lng);
                        userMarker.setLatLng(latLng);
                        updateLatLngInputs(latLng);
                        if(userMarker.isHidden()) {
                            userMap.addOverlay(userMarker);
                        }
                        userMap.setCenter(latLng);
                    }else{
                        alert("Postcode not found!");
                    }
                });
            localSearch.execute(postcode + ", UK");
        } else {
            alert("Please enter a valid UK postcode.");
        }
        return false;
    }

    var locInput = $('textarea#id_location');
    var form=$(locInput.get(0).form);

    locInput.parent('p').hide();
    form.find('#location-intro').hide();
    locInput.parent('p').after('<div id="map_canvas" style="width: 300px; height: 300px"></div>');
    locInput.parent('p').after('<p><label for="postal_code">Postcode:</label><input id="postal_code" type="text" /><a href="" id="submit_postcode">Use postcode</a></p>');

    var userMarker = new GMarker(new GLatLng(0,0), {draggable: true});
    GEvent.addListener(userMarker, "dragend", function() {updateLatLngInputs(this.getLatLng()); });
    var userMap = new GMap2(form.find("#map_canvas").get()[0]);
    userMap.setCenter(new GLatLng(54.2, -2), 5);
    userMap.addControl(new GSmallMapControl());
    var loc = locInput.val()
    var z = pointRe.exec(loc);
    var lat, lng;
    if (z.length == 3) {
        lng = z[1];
        lat = z[2];
    } else lat = lng = '';

    if (/[0-9.]+/.test(lat) && /[0-9.]+/.test(lng)) {
        userMarker.setLatLng(new GLatLng(parseFloat(lat), parseFloat(lng)));
        userMap.addOverlay(userMarker);
    } else {
        var clickListener = GEvent.addListener(userMap, "click", function(overlay, latLng) {
            GEvent.removeListener(clickListener);
            userMarker.setLatLng(latLng);
            updateLatLngInputs(latLng);
            userMap.addOverlay(userMarker);
        });
    }

    form.find('#submit_postcode').click(submitPostcode);
    form.find('input#postal_code').keydown(postcodeKeydown);
}

google.setOnLoadCallback(function() {
    $(document).unload(GUnload);
    doLocationWidget();
//    navigator.geolocation.getCurrentPosition(function(position) {alert(position.coords)})
});

