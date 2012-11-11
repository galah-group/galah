# Wrapper around User to allow Flask-Login to work with it
from types import MethodType
def FlaskUser(user):
    "Decorates a given User instance with the methods in the UserMixin class"
    
    methodize = lambda func: MethodType(func, user)
    
    # Too many problems were occuring transplanting the UserMixin class so I
    # remade the methods here.
    user.is_active = methodize(lambda self: True)
    user.is_authenticated = methodize(lambda self: True)
    user.is_anonymous = methodize(lambda self: True)
    user.get_id = methodize(lambda self: self.id)
    
    return user

# All users must have an account_type variable in order for the 
# account_type_required decorator to work
from flask.ext.login import AnonymousUser
class Anonymous(AnonymousUser):
    account_type = None

## Decorator that enforces account_type based permissions ##
from functools import wraps
from flask.ext.login import current_user
from flask import current_app, flash
from types import StringType
from galah.base.pretty import pretty_list
def account_type_required(account_type):
    """
    A decorator that can be applied to views to only allow access to users with
    certain account types.

    :param account_type: The account types that are allowed. May either be a
                         single string (meaning only one account type is
                         allowed) or a tuple, in which case any account type
                         within that tuple will be allowed access.

    """

    # We allow the user of this function to specify a string for account_type
    # signaling that only one type of user is allowed. The rest of the function
    # except account_type to be a tuple however, so convert it here.
    if isinstance(account_type, StringType):
        account_type = (account_type, )

    # Form a nicely formatted string that we will use to provide an error
    # message to the end-user if they try to access a restricted page.
    allowed = pretty_list(account_type, none_string = "magical")

    def internal_decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated() or \
                    current_user.account_type not in account_type:
                flash("Only %s users are permitted to access this page."
                          % allowed, category = "error")
                return current_app.login_manager.unauthorized()
                
            return func(*args, **kwargs)
        
        return decorated_view
        
    return internal_decorator

# Set up the login manager
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = None
    
# Loads a user useable by Flask-Login from a user id (email)
from galah.db.models import User
@login_manager.user_loader
def load_user(email):
    return FlaskUser(User.objects.get(email = email))
