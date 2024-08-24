# -*- coding: utf-8 -*-
"""LibriCipher Administration controller module."""

import logging
log = logging.getLogger(__name__)

from tg import expose, redirect, validate, flash, url, require, request, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import has_permission, has_any_permission
from tg.decorators import paginate

from lustitelskadb import model
from lustitelskadb.lib.base import BaseController
from lustitelskadb.model import DBSession

import lustitelskadb.lib.forms as appforms

try:
    from webhelpers2 import html
except (ImportError, ModuleNotFoundError, SyntaxError):
    try:
        from webhelpers import html
    except:
        log.error("WebHelpers(2) helpers not available with this Python Version")

import tw2.core as twc
import tw2.forms as twf

__all__ = ['LibriCipherController']


class LibriCipherController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = not_anonymous()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "LustitelskaDB"
        tmpl_context.pager_params = dict(
            format=u"$link_first $link_previous ~2~ $link_next $link_last",
            symbol_first=u"«",
            symbol_last=u"»",
            symbol_previous=u"‹",
            symbol_next=u"›",
            dotdot_attr={'class': 'page-item'},
            link_attr={'class': 'page-link'},
            curpage_attr={'class':'page-item active', 'aria-current': 'page'},
            page_link_template=u'<li class="page-item"><a%s>%s</a></li>',
            page_plain_template=u'<li%s><a class="page-link">%s</a></li>'
        )

    @expose('lustitelskadb.templates.administration.libricipher.index')
    @paginate("data", items_per_page=5)
    @require(has_any_permission('manage', 'libricipher', msg=l_('Only for users with appropriate permissions')))
    def index(self, **kw):
        """Libri Cipher table view"""
        fields = [
            (
                html.literal(
                    u'<a role="button" class="btn btn-sm btn-outline-secondary d-print-none" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="glyphicon glyphicon-option-vertical" aria-hidden="true" title="{}"></i></a>'.format(l_(u"Actions")) +
                    u'<div class="dropdown-menu d-print-none" aria-labelledby="dropdownMenuLink">' +
                        u'<a class="dropdown-item" href="{}"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i> {}</a>'.format(url('/admin/libricipher/edit'), l_(u'Add Libri Ciphers item')) +
                        u'<a class="dropdown-item" href="{}"><i class="glyphicon glyphicon-refresh" aria-hidden="true"></i> {}</a>'.format(url('/admin/libricipher'), l_('Refresh Libri Ciphers')) +
                    u'</div>'
                ),
                lambda obj: html.literal(
                    u'<div class="btn-group btn-group-sm d-none d-md-inline-flex d-print-none">' +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s"><i class="glyphicon glyphicon-pencil"></i></a>' % (url('/admin/libricipher/edit/%d' % (obj.uid or 0)), l_(u"Edit")) +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s"><i class="glyphicon glyphicon-search"></i></a>' % (url('/admin/libricipher/detail/%d' % (obj.uid or 0)), l_(u"Detail")) +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s" onclick="return confirm(\'%s\')"><i class="glyphicon glyphicon-trash"></i></a>' % (url('/admin/libricipher/delete/%d' % (obj.uid or 0)), l_(u"Delete"), l_(u"Really delete?")) +
                    u'</div>' +
                    u'<div class="btn-group-vertical btn-group-sm d-inline-flex d-md-none d-print-none">' +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s"><i class="glyphicon glyphicon-pencil"></i></a>' % (url('/admin/libricipher/edit/%d' % (obj.uid or 0)), l_(u"Edit")) +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s"><i class="glyphicon glyphicon-search"></i></a>' % (url('/admin/libricipher/detail/%d' % (obj.uid or 0)), l_(u"Detail")) +
                        u'<a role="button" class="btn btn-outline-secondary" href="%s" title="%s" onclick="return confirm(\'%s\')"><i class="glyphicon glyphicon-trash"></i></a>' % (url('/admin/libricipher/delete/%d' % (obj.uid or 0)), l_(u"Delete"), l_(u"Really delete?")) +
                    u'</div>'
                )
            ),
            (
                l_(u"Part"),
                lambda obj: html.literal('<div class="text-end">{}</div>'.format(obj.part))
            ),
            (
                l_(u"Question"),
                lambda obj: html.literal(
                    u'<h5>{}</h5>'.format(obj.question) +
                    u'<div>{}</div>'.format(obj.description)
                )
            ),
            (
                l_(u"Answer"),
                'answer'
            )
        ]

        data = DBSession.query(model.LibriCipher).order_by(model.LibriCipher.uid.desc())

        tmpl_context.datagrid = twf.DataGrid(
            css_class="table table-striped table-hover table-bordered table-sm",
            fields=fields
        )

        return dict(page='libricipher-administration-index', data=data)

    @expose('lustitelskadb.templates.administration.libricipher.edit')
    @require(has_any_permission('manage', 'libricipher-edit', msg=l_('Only for users with appropriate permissions')))
    def edit(self, uid=None, *args, **kw):
        """Save Libri Cipher item"""
        tmpl_context.form = appforms.LibriCipherForm()

        if request.validation.errors:
            tmpl_context.form.value = kw
            tmpl_context.form.error_msg = l_("Form filled with errors!")
            for key, value in request.validation.errors.items():
                if value:
                    getattr(tmpl_context.form.child.children, key).error_msg = value

        if uid:
            libricipher = DBSession.query(model.LibriCipher).filter(model.LibriCipher.uid == uid).first()
            if not libricipher:
                flash(_("Requested Libri Cipher not found"))
                redirect('/admin/libricipher')

            tmpl_context.form.value = libricipher.__dict__

        return dict(page='libricipher-administration-edit')

    @expose()
    @validate(form=appforms.LibriCipherForm(), error_handler=edit)
    @require(has_any_permission('manage', 'libricipher-edit', msg=l_('Only for users with appropriate permissions')))
    def save(self, uid=None, *args, **kw):
        """Save Libri Cipher item"""
        if uid:
            libricipher = DBSession.query(model.LibriCipher).filter(model.LibriCipher.uid == uid).first()
            if not libricipher:
                flash(_("Requested Libri Cipher not found"))
                redirect('/admin/libricipher')

            for k, v in kw.items():
                setattr(libricipher, k, v)

            flash(_("Libri Cipher item successfully modified"))
        else:
            libricipher = model.LibriCipher(**kw)
            DBSession.add(libricipher)

            flash(_("Libri Cipher item successfully created"))

        DBSession.flush()

        return redirect('/admin/libricipher')

    @expose()
    @require(has_any_permission('manage', 'libricipher', msg=l_('Only for users with appropriate permissions')))
    def detail(self, uid=None, *args, **kw):
        """Libri Cipher detail view"""
        if not uid:
            flash(_("Missing unique ID of Libri Cipher"))
            redirect('/admin/libricipher')

        libricipher = DBSession.query(model.LibriCipher).filter(model.LibriCipher.uid == uid).first()
        if not libricipher:
            flash(_("Requested Libri Cipher not found"))
            redirect('/admin/libricipher')

        return dict(page='libricipher-administration-detail', libricipher=libricipher)

    @expose()
    @require(has_any_permission('manage', 'libricipher-delete', msg=l_('Only for users with appropriate permissions')))
    def delete(self, uid=None, *args, **kw):
        """Libri Cipher delete item"""
        if not uid:
            flash(_("Missing unique ID of Libri Cipher"))
            redirect('/admin/libricipher')

        libricipher = DBSession.query(model.LibriCipher).filter(model.LibriCipher.uid == uid).first()
        if not libricipher:
            flash(_("Requested Libri Cipher not found"))
            redirect('/admin/libricipher')

        DBSession.delete(libricipher)
        DBSession.flush()

        flash(_("Libri Cipher item successfully deleted"))
        return redirect('/admin/libricipher')
