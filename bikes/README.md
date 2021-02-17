# Bike Rental

This demo utilizes:

* [Django](https://www.djangoproject.com/) (1.11)
* [Django Rest Framework](http://www.django-rest-framework.org/) (3.6.3)
* [DRFDocs](https://www.drfdocs.com)
* [Gunicorn](http://gunicorn.org/)
* [Nginx](https://nginx.org/)
* [Docker](https://www.docker.com/)
* [Alpine Linux](https://www.alpinelinux.org/)


## Design rationale

The idea behind this project is to provide a set of endpoints where users can rent bikes (daily, hourly, weekly) and apply a discount if it's for a family.
The users are divided in three groups: Admin, staff, end-users. End-Users can place orders but can't update / delete. Staff users can update / delete. Admin users can do everything (including the creating of staff users).
A practical scenario for this application would be self-service terminal where users can interact with the service placing an order of their liking, while the staff needs to approve / charge for the service and verify that bikes are indeed returned.
Something that is missing from this demo is the fact that users that return bikes before the `due_date` might have to pay a late fee, but since it wasn't defined, this feature simply wasn't added (yet this app can calculate how late a bike was returned, so it's possible to add this)

La idea detras de este proyecto es proveer una serie de endpoints donde los usuarios pueden alquilar bicicletas (por hora, dia, o semanalmente) y aplicar un descuento si es por grupo familiar.
Los usuarios estan divididos en tres grupos: Admin, staff, usuarios-finales. Los usuarios-finales pueden hacer pedidos pero no pueden actualizar / eliminar pedidos. El staff puede eliminar / eliminar. Admin puede hacer todo (incluido crear usuarios staff).
Un escenario practo para esta aplicacion seria terminal de auto-servicio donde los usuarios pueden interactuar con la aplicacion realizando un pedido, mientras que el staff necesita aprobar / cobrar por el servicio y verificar que las bicicletas hayan sido devueltas.
Algo que esta faltando de esta demo es el hecho de que si los usuarios devuelven las bicicletas luego de la fecha de entrega tengan que pagar un recargo, pero como no estaba definido, esta feature no fue agregada (sin embargo, la aplicacion puede calcular facilmente que tan tarde ha sido entregada, por lo que seria facil de extender)



## Deployment

```
$ docker build -t bikes-demo .
$ docker run -it -rm -p 81:81 -p 82:82 --name bikes-demo-app bikes-demo
```

## Django Admin

URL: http://{url}:{port}/

Username: admin
Password: 123qweasd

## API endpoints

URL: http://{url}:{port}/api/

### Registration

`POST /api/users/create`

args:

* field: username
* field: password

return:

* User OK: http 201 + Token
* User Exists: http 409 + Error msg
* Error: http 400 + Error msg

### Log in

`POST /api/users/login`

args:

* field: username
* field: password

return:

* Login OK: http 200 + Token
* Login BAD: http 401 + Error msg
* User not enabled: http 403 + Error msg

### Log out

`POST /api/users/logout`

args:

* auth token

return:

* http 202 + Friendly msg

### List Orders

`GET /api/orders/`
`GET /api/orders/{id}`

args:

* header: auth token

return:

* http 200 + Data

### Create Order

`POST /api/orders/`

args:

* header: auth token
* field: rentals (comma separated str)
* field: is_field (bool)

return:

* http 201 + Data

### Delete Order

`DELETE /api/orders/{id}`

args:

* header: auth token (for staff user)

return:

* http 204

### List Rentals

`GET /api/rentals/`
`GET /api/rentals/{id}`

args:

* header: auth token

return:

* http 200 + Data

### Update Rental

`PUT /api/rentals/{id}`

args:

* header: auth token (for staff user)
* field: returned (bool)

return:

* http 202 + Data

### Delete Rental

`DELETE /api/rentals/{id}`

args:

* header: auth token (for staff user)

return:

* http 204
