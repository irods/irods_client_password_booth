# iRODS Password Booth

The iRODS Password Booth is a *very small* web application with one job - to allow visitors to change their native iRODS password.

This CherryPy application uses the Python iRODS Client to connect to iRODS and execute `modify_password`.

## Configuration

```
cp app.config.template app.config
vi app.config
```

The `[password_booth]` section requires updates to point to your iRODS Zone:
```
[password_booth]
#irods_host = 'host.docker.internal'
irods_host = 'irods.example.org'
irods_zone = 'tempZone'
irods_port = 1247
```

## Building and Running with Docker Compose

Docker Compose has been configured to volume mount the local `app.config`.

```
docker compose up
```

Connecting to localhost:8000 (by default) will open the Password Booth.
