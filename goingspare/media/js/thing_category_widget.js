function CatBoxWidget(element) {
    function select_box_html(box_id, options, value) {
        var html = '<select id="id_category_'+box_id+'">';
        html+='<option value="">Select category</option>';
        for (var i=0;i<options.length;i++) {
            html+='<option value="'+options[i][0]+'"'+(options[i][0]==value ? ' selected="selected"':'')+'>'+options[i][1]+'</option>';
        }
        html +='</select>';
        return html;
    }

    function cleanup_end_boxes(start_index) {
        var z;
        for (var i=start_index;;i++) {
            z=$('#id_category_'+i);
            if (z.length>0) z.remove(); else break;
        }
    }

    function make_select_box(box_id, options, def) {
        if (options.length==0) {
            cleanup_end_boxes(box_id);
            return;
        }
        if ($('#id_category_'+box_id).length) cleanup_end_boxes(box_id);
        $('#category_selector').append(select_box_html(box_id, options, def));
        $('#id_category_'+box_id).change(function() {
            if (this.selectedIndex>0) {
                output_field.val($(this).val());
                $.getJSON('/stuff/categories/'+$(this).val()+'/', null, make_select_box_ajax_wrapper(box_id+1));
            } else {
                if (box_id>0) {
                    output_field.val($('#id_category_'+(box_id-1)).val());
                } else {
                    output_field.val('');
                }
                cleanup_end_boxes(box_id+1);
            }
        });
    }

    function make_select_box_ajax_wrapper(box_id, options, def) {
        return function(data) {
            make_select_box(box_id, data, def);
        }
    }

    var cat=$(element).val();
    var input_name=$(element).attr('name');
    $(element).replaceWith('<div id="category_selector"><input type="hidden" id="id_category" name="'+input_name+'" /></div>');
    var output_field=$("input[@name='"+input_name+"']");
    if (cat) {
        output_field.val(cat);
        $.getJSON('/stuff/categories/tree/'+cat+'/', null, function(data) {
            for (var i=0;i<data.length;i++) {
                var def;
                def=data[i].pop();
                make_select_box(i, data[i], def);
            }
            $.getJSON('/stuff/categories/'+def+'/', null, make_select_box_ajax_wrapper(i+1));
        });
    } else {
        $.getJSON('/stuff/categories/', null, make_select_box_ajax_wrapper(0));
    }
}

$(document).ready(function() {
    var widget = new CatBoxWidget('input#id_thing_category');
});
