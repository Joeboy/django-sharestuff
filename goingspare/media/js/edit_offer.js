
var editOffer = function() {
    jQuery('<p id="add-image">').append(jQuery('<a href="">Add an image</a>').click(editOffer.imageSelector)).insertAfter(jQuery('#id_live_status').parent());
    editOffer.image_list_container = jQuery('<p></p>');
    jQuery("#id_live_status").parent().after(editOffer.image_list_container);
    jQuery("#id_live_status").parent().after("<h4>Images</h4>");
    editOffer.displayImages(images);
};

updateImageInput = function() {
    var ids = [];
    for (var im in images) ids.push(images[im].id);
    jQuery('input#id_image_list').val(ids.join(','));
};

editOffer.showImage = function() {
    jQuery(this).find('img').each(function() {
        jQuery('<div id="image-dialog"><img src="'+this.src+'" /></div>').dialog({modal:true,
                    title: "Image",
                    position:'top',
                    width:600,
                    draggable:true});
    });
    return false;
}

editOffer.displayImages = function(images) {
    editOffer.image_list_container.empty();
    for (k in images) {
        editOffer.image_list_container.append('<div class="thumb"><a href=""><img title="'+images[k].caption+'" src="'+images[k].url+'"></a></div>')
    }
    jQuery(".thumb a").click(editOffer.showImage);
}

editOffer.imageSelector = function() {
    var con;

    var imageFormSubmitted = function(data, textStatus, jqXHR) {
        con.dialog('close');
        if (data[0] == '{') { // This is lame, but it's late
            jsonData = jQuery.parseJSON(data);
            images.push(jsonData);
            updateImageInput()
            editOffer.displayImages(images);
        } else {
            create_dialog(data);
        }
    };

    var create_dialog = function(data) {
        con = jQuery('<div></div>');
        con.append(data);
        con.find('form').ajaxForm({success: imageFormSubmitted});
        con.dialog({modal:true,
                    title: "Upload an image",
                    position:'top',
                    width:600,
                    draggable:true});
        return false;
    }

    var url;
    if (isNaN(offer_id)) url = '/offers/images/add/'
    else url = '/offers/'+offer_id+'/images/add/';
    jQuery.ajax(url, { success: function(data, textStatus, jqXHR) {
        create_dialog(data);
    } })

    return false;
};


jQuery(editOffer)
