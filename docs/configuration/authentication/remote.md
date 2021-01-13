# Remote User Authentication

NetBox can be configured to support remote user authentication by inferring users from an HTTP header set by an authenticating reverse proxy (e.g. nginx or Apache). 

This document describes how to make use of an external authentication source (where the Web server sets the `REMOTE_USER` environment variable). This type of authentication solution is typically seen on intranet sites, with single sign-on solutions.

User authentication will still fall back to built-in Django users in the event of a failure in remote authentication.

## Installation

Enable the remote user authentication backend by adding the following to your `configuration.py`:

!!! note
    It is critical that you include the `ObjectPermissionsBackend` provided by
    NetBox after the `RemoteUserBackend` so that object-level permissions features can work properly.

```python
AUTHENTICATION_BACKENDS = [
    'netbox.authentication.RemoteUserBackend',
    'netbox.authentication.ObjectPermissionBackend',
]
```

## Configuration

The following configuration variables describe the default values and as long as `RemoteUserBackend` has been installed as described above, no changes are required.

If you do require customizing any of these settings, they must be set in your `configuration.py`.

### REMOTE_AUTH_AUTO_CREATE_USER

Default: `False`

If set to `True`, local accounts will be automatically created for users authenticated via a remote service.

---

### REMOTE_AUTH_DEFAULT_GROUPS

Default: `[]` (Empty list)

The list of groups to assign a new user account when created using remote authentication.

---

### REMOTE_AUTH_DEFAULT_PERMISSIONS

Default: `{}` (Empty dictionary)

A mapping of permissions to assign a new user account when created using remote authentication. Each key in the dictionary should be set to a dictionary of the attributes to be applied to the permission, or `None` to allow all objects.

---

### REMOTE_AUTH_ENABLED

!!! warning
    This setting is deprecated and will be removed in a future release.

    Toggling this setting to `False` will disable remote user authentication if
    it is installed as specified in this document.

Default: `True`

Set this to `False` to quickly disable this method of authentication. Local authentication will still take effect as a fallback.

---

### REMOTE_AUTH_HEADER

Default: `'HTTP_REMOTE_USER'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the currently authenticated user. For example, to use the request header `X-Remote-User` it needs to be set to `HTTP_X_REMOTE_USER`.