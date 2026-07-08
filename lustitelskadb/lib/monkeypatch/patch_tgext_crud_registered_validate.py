'''
Created on 8. 7. 2026

@author: jarda
'''

def patch_tgext_crud_registered_validate():
    """
    Compatibility patch for tgext.crud registered_validate with TurboGears 2.5+.

    TG2 2.4 called:
        validators.validate(controller_method, params, state)

    TG2 2.5 calls:
        validators.validate(controller_method, params)

    Old tgext.crud still expects the third argument, so make it optional.
    Also patch already-created CrudRestController post/put validation objects.
    """

    import tgext.crud.decorators as crud_decorators
    from tgext.crud._compat import im_func, im_self, string_type

    registered_validate = crud_decorators.registered_validate

    if getattr(registered_validate, "_tg25_compat_patched", False):
        return

    def make_compat_validators():

        class Validators(object):

            def validate(self, controller, params, state=None):
                func_name = im_func(controller).__name__
                controller_self = im_self(controller)

                validators = getattr(controller_self, "__validators__", {})
                validator = validators.get(func_name)

                if validator is None:
                    return params

                return validator.validate(params, state)

        return Validators()

    def fixed_init(self, error_handler=None, *args, **kw):
        if not isinstance(error_handler, string_type):
            raise ValueError(
                "error_handle must be a string containing method name."
            )

        self._error_handler = error_handler
        self.needs_controller = True
        self.chain_validation = False
        self.validators = make_compat_validators()

    registered_validate.__init__ = fixed_init
    registered_validate._tg25_compat_patched = True

    # Patch validation objects that already exist on tgext.crud controller methods.
    # This matters because CrudRestController.post/put are decorated at import time.
    try:
        import tgext.crud.controller as crud_controller
    except Exception:
        return

    def patch_existing_method(method):
        decoration = getattr(method, "decoration", None)
        if decoration is None:
            return

        for validation in getattr(decoration, "validations", []):
            if isinstance(validation, registered_validate):
                validation.needs_controller = True
                validation.validators = make_compat_validators()

    for controller_class_name in ("CrudRestController", "EasyCrudRestController"):
        controller_class = getattr(crud_controller, controller_class_name, None)
        if controller_class is None:
            continue

        for method in controller_class.__dict__.values():
            patch_existing_method(method)
