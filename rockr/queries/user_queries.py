import rockr.auth0.auth0_api_wrapper as auth0


# we should stop using this pattern. Just query through the ORM
def change_password(user):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.change_password(user)


def get_roles():
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.get_roles()


def create_auth0_account(user):
    api_wrapper = auth0.Auth0ApiWrapper()
    return api_wrapper.create_auth0_account(user)
