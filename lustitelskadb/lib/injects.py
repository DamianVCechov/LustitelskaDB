# -*- encoding: utf-8 -*-
'''
Created on 24. 8. 2024

@author: jarda
'''

from tg import lurl
from tw2.core import JSLink, JSSource

__all__ = ['tinymce_link', 'tinymce_init', 'closing_deadline_jssrc']

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

closing_deadline_jssrc = JSSource(src='''"use strict";
function milisecsToTimeString(timeInMilisecs) {
    let h, m, s;

    h = Math.floor(timeInMilisecs / 1000 / 60 / 60);
    m = Math.floor((timeInMilisecs / 1000 / 60 / 60 - h) * 60);
    s = Math.floor(((timeInMilisecs / 1000 / 60 / 60 - h) * 60 - m) * 60);

    s < 10 ? s = `0${s}`: s = `${s}`;
    m < 10 ? m = `0${m}`: m = `${m}`;
    h < 10 ? h = `0${h}`: h = `${h}`;

    return `${h}:${m}:${s}`;
}

function setClosingProgressBar() {
    const now = new Date();
    let target = new Date(now);
    let dayInMillisec = 24 * 60 * 60 * 1000;
    let leftPercent = 0;

    target.setHours(18);
    target.setMinutes(0);
    target.setSeconds(0);
    target.setMilliseconds(0);

    if (now.getHours() >= 18) {
        target = new Date(target.getTime() + dayInMillisec);
    }

    leftPercent = ((target - now) / dayInMillisec) * 100;

    $('#closingDeadlineProgress.progress').attr('aria-value-now', Math.round(leftPercent));
    $('#closingDeadlineProgress.progress>.progress-bar').width(String(100 - Math.round(leftPercent)) + '%');
    if (leftPercent > 50) {
        $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-success').removeClass('bg-warning').removeClass('bg-danger');
    } else if (leftPercent > 25) {
        $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-warning').removeClass('bg-success').removeClass('bg-danger');
    } else {
        $('#closingDeadlineProgress.progress>.progress-bar').addClass('bg-danger').removeClass('bg-success').removeClass('bg-warning');
    }
    $('#closingDeadlineProgress.progress>.progress-bar').text(milisecsToTimeString(target - now));

    setTimeout(setClosingProgressBar, 1000);
}

$(() => {
    setClosingProgressBar();
});''')
