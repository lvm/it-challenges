# twitter scrapper

## Primeros pasos

Los requerimientos utilizados en esta aplicacion se encuentran en el archivo `requirements.pip`.  
Como pre-requerimiento es importante tener `virtualenv` instalado.  
  
De cualquier manera, (a grandes razgos) los pasos a reproducir para comenzar a trabajar/testear la aplicacion son:

```
$ virtualenv twitterscrapper
$ cd !$
$ (clonar el repositorio | descomprimir al codigo)
$ pip install -r requirements.pip
$ fab init_django_local
```

`init_django_local` simplemente ejecutara las migraciones iniciales y luego creara un usuario `admin` con el password `123qweasd`.  
Luego es necesario ejecutar `manage.py runserver` para iniciar el servidor integrado de Django. Adicionalmente, es necesario ejecutar `fab q_cluster` o `manage.py qcluster` para poder encolar las tareas eventualmente creadas.  
Nota: Por ser un proyecto de *prueba* utilizo SQLite y al ORM de Django como broker.

## Endpoints

Existe solo un endpoint: `/users`  
Acepta `GET` y `POST`. Dependiendo del metodo utilizado devolvera uno o mas usuarios de Twitter o disparara la tarea para agregarlo a la DB.  

### Crear un nuevo usuario

```
POST /users/:username
```

Esto nos devuelve `{'status': 'ok', 'message': 'processing request'}`. Cabe aclarar que es necesario pasar un `:username` en el request de lo contrario devolvera `{'status': 'err', 'message': 'missing username'}` (nota: El el unico error que devuelve).

### Listar usuarios

```
GET /users/:username?
```

El parametro `:username` es opcional. Si lo pasamos nos devolvera los datos de este, en caso contrario nos devolvera una lista de usuarios disponibles (no paginado).

## Admin

Tambien es posible ingresar al admin de Django para observar los usuarios cargados / visualizar las tareas existentes.  
El usuario:password es el descripto anteriormente y el *path* `/manage`


## Tests

Por falta de imaginacion solamente se testea que se posteen correctamente los usuarios.
