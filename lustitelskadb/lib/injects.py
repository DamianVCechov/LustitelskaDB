# -*- encoding: utf-8 -*-
'''
Created on 24. 8. 2024

@author: jarda
'''

from tg import lurl
from tw2.core import JSLink, JSSource

__all__ = ['tinymce_link', 'tinymce_init']

tinymce_version = '6.8.3'

tinymce_link = JSLink(location="bodybottom", link=lurl("/js/tinymce/tinymce.min.js", params={'v': tinymce_version}))

tinymce_init = """
//$('.tinymce-override').height($(document).innerHeight() - 150);
tinymce.init({
    selector: 'textarea.tinymce-override',
    language: '%(lang)s',
    width: '100%%',
    height: (window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight) - document.querySelector('body > nav').offsetHeight,
    //plugins: 'preview importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media template codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons',
    plugins: 'preview importcss searchreplace autolink directionality code visualblocks visualchars fullscreen image link media template codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons',
    toolbar: 'fullscreen preview save print | undo redo | blocks | bold italic underline strikethrough removeformat | fontsize |fontselect fontsizeselect formatselect | lineheight | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | forecolor backcolor removeformat | pagebreak | charmap emoticons | insertfile image media template link anchor codesample | ltr rtl',
    toolbar_sticky: false,
    importcss_append: true,
    entity_encoding : "raw",
    image_title: true,
    automatic_uploads: true,
    /*file_picker_types: 'file image media',
    file_picker_callback: (cb, value, meta) => {
        $('#file-picker-dlg').on('hide.bs.modal', (event) => {
            cb($('#file-picker-url').val(), {});
        });
        $('#file-picker-dlg').modal('show');
    },*/
    //importcss_exclusive: false,
    importcss_groups: [{title: '%(skin_styles_title)s'}],
    content_css: '%(content_css)s',
    content_css_cors: true,
    /*menu: {
        favs: {
            title: 'My Favorites',
            items: 'code visualaid | searchreplace | spellchecker | emoticons'
        }
    },*/
    //menubar: 'favs file edit view insert format tools table help',
    //menubar: 'file edit view insert format tools table help',
    menubar: true,
    image_class_list: [
        {title: 'None', value: ''},
        {title: 'Sensitive', value: 'img-sensitive'},
        {title: 'Bootstrap 3.x Responsive', value: 'img-responsive'},
        {title: 'Bootstrap 3.x Responsive + Sensitive', value: 'img-responsive img-sensitive'},
        {title: 'Bootstrap 4.x/5.x Responsive', value: 'img-fluid'},
        {title: 'Bootstrap 4.x/5.x Responsive + Sensitive', value: 'img-fluid img-sensitive'}
    ],
    table_class_list: [
        {title: 'None', value: ''},
        {title: 'Bootstrap (BS) Table', value: 'table'},
        {title: 'BS Table Striped', value: 'table table-striped'},
        {title: 'BS Table Bordered', value: 'table table-bordered'},
        {title: 'BS Table Borderless', value: 'table table-borderless'},
        {title: 'BS Table Hoverable', value: 'table table-hover'},
        {title: 'BS Table Small', value: 'table table-sm'},
        {title: 'BS Table Dark Responsive', value: 'table table-dark'},
        {title: 'BS Table Dark striped', value: 'table table-dark table-striped'},
        {title: 'BS Table Dark bordered', value: 'table table-dark table-bordered'},
        {title: 'BS Table Dark borderless', value: 'table table-dark table-borderless'},
        {title: 'BS Table Dark hoverable', value: 'table table-dark table-hover'},
        {title: 'BS Table Dark small', value: 'table table-dark table-sm'}
    ],
    table_cell_class_list: [
        {title: 'None', value: ''},
        {title: 'Max Width', value: 'w-100'},
    ],
    branding: false,
    promotion: false,
    /*setup: function(ed) {
        ed.on('init', function(e) {
            e.target.hide();
        });
    }*/
});
"""
