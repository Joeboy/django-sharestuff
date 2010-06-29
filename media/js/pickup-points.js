function update_latlng_inputs(latlng) {
    document.getElementById("id_latitude").value=latlng.latRadians();
    document.getElementById("id_longitude").value=latlng.lngRadians();
}

function rad2deg(radians) { return 360*radians/(2*Math.PI); }

$('document').ready(function() {
    if (GBrowserIsCompatible()) {
        var map = new GMap2(document.getElementById("map_canvas"));
        map.setCenter(new GLatLng(54.2, -2), 5);
        map.addControl(new GSmallMapControl());
        var marker;
        var lat = document.getElementById('id_latitude').value;
        var lng = document.getElementById('id_longitude').value;

        if (/[0-9.]+/.test(lat) && /[0-9.]+/.test(lng)) {
            marker = new GMarker(new GLatLng(rad2deg(parseFloat(lat)), rad2deg(parseFloat(lng))), {draggable: true});
            GEvent.addListener(marker, "dragend", function() {update_latlng_inputs(marker.getLatLng()); });
            map.addOverlay(marker);
        } else {
            var clickListener = GEvent.addListener(map, "click", function(overlay, latlng) {
                GEvent.removeListener(clickListener);
                update_latlng_inputs(latlng);
                marker = new GMarker(latlng, {draggable: true});
                GEvent.addListener(marker, "dragend", function() { update_latlng_inputs(marker.getLatLng()); });
                map.addOverlay(marker);
            });
        }


//        GEvent.addListener(map, "dragend", function() {
//alert("hi");
//          map.closeInfoWindow();
//        });

//        GEvent.addListener(marker, "dragstart", function() {
//          map.closeInfoWindow();
//        });
//

 //       map.addControl(new google.maps.LocalSearch(), new GControlPosition(G_ANCHOR_BOTTOM_RIGHT, new GSize(10,10)));
//        for (k in localsearch) {
//            alert(k+"="+localsearch[k]);
//        }
      }




//    $('#userprofile_form').submit(function() {
//        postcode = $('#id_postcode').attr('value');
//        if (/[A-Z]{1,2}[0-9]{1,2} ?[0-9][A-Z]{2}/i.test(postcode)) {
//            var localSearch = new google.search.LocalSearch();
//            localSearch.setSearchCompleteCallback(null,
//                function() {
//                    if (localSearch.results[0]) {
//                        somecallback(localSearch.results[0].lat, localSearch.results[0].lng)
//                    }else{
//                        alert("Postcode not found!");
//                    }
//                });
//            localSearch.execute(postcode + ", UK");
////        if (form_is_ready) {
////            form_is_ready=false;
////            $('postcode_submit').disabled="disabled";
////            use_point_from_postcode($('id_pickup1_postcode').value, somecallback);
////        }
//        } else {
//            alert("Please enter a valid postcode.");
//        }
//        return false;
//    });
});

$('document').unload(function() {GUnload();});
