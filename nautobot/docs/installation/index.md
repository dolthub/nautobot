# Installation

The installation instructions provided here have been tested to work on Ubuntu 20.04 and CentOS 8.2. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the Nautobot maintainers. Please consult your distribution's documentation for assistance with any errors.

The following sections detail how to set up a new instance of Nautobot:

1. [PostgreSQL database](1-postgresql.md)
1. [Redis](2-redis.md)
3. [Nautobot components](3-nautobot.md)
4. [Gunicorn](4-gunicorn.md)
5. [HTTP server](5-http-server.md)
6. [External authentication](6-external-authentication.md) (optional)

## Requirements

| Dependency | Minimum Version |
|------------|-----------------|
| Python     | 3.6             |
| PostgreSQL | 9.6             |
| Redis      | 4.0             |

Below is a simplified overview of the Nautobot application stack for reference:

![Nautobot UI as seen by a non-authenticated user](../media/installation/nautobot_application_stack.png)

## Upgrading

If you are upgrading from an existing installation, please consult the [upgrading guide](upgrading.md).