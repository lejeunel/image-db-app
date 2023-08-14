# picasso-db-app


## Testing

Setup dummy database with SQLite
``` sh
flask --app app/test populate-test-db
```

Run server
``` sh
flask --app app/test --debug run --host=0.0.0.0
```

Run unit tests
``` sh
pytest app/tests
```

## Run app "locally"

Using docker image by mapping ports (this will use dev mode):
``` sh
docker build -t picasso-db-app .
docker run -p 8005:80 -it picasso-db-app
```

## Deployment

- Infrastructure has been setup following <https://docs.int.bayer.com/cloud/smart-aws/smart-2.0/fargate/>
- We use deployment script from <https://github.platforms.engineering/Pipeline-Principal-Engineers/fg-deploy-nextgen>
- Run deployment script (runs on amazon-linux)

``` sh
chmod +x deploy_fargate.sh
./deploy_farget.sh
```

## Database migrations

Initialize migrations repository if it doesn't exist
``` sh
flask --app app/dev db init
```

Upon changes in models:
``` sh
flask --app app/dev db migrate -m "commit message"
```

To apply migrations to database:
``` sh
flask --app app/dev db upgrade
```

## TODO
- Fix bug with tag join: 
- Set cascade behaviour as in <https://docs.sqlalchemy.org/en/14/orm/cascades.html>
- Through polymorphism, all objects (image, plate, compound, ...) can be assigned a tag. At the moment, only sections can be tagged.
- Setup multiple database so that each project/group gets its own database.
- Add an API dynamic filtering of images à la <https://github.com/elmkarami/sqlalchemy-filters-plus>
- Add more useful tables in UI to filter, sort, and search (images, ...)
- In plate details, images should show up without meta-data when no sections are defined
- This is currently deployed on us-east-1 because Ocelot cannot route to eu-central... Figure out an alternative (mulesoft?).
