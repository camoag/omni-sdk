The Omni SDK includes an easy-to-use REST API client that provides high-level methods for common tasks and low-level 
methods for making requests directly to the REST endpoints.

## Creating the client
Configuration of the client can be handled using kwargs or environment variables. Examples of both are below.

```python  title="Kwarg Configuration"
from omni import OmniApiClient

client = OmniApiClient(
    organization_name="acme", 
    api_key="omni_osk_r0dvvwTfLkOC1QP6eomT65yOIWtjfDsU5gZpvKNdKWxHSrDJPT1RAUyV",
)
```

```python  title="Environment Variable Configuration"
import os
from omni import OmniApiClient

# For demonstration purposes only. The assumption is that these env vars are already set.
os.environ["OMNI_ORGANIZATION_NAME"] = "acme"
os.environ["OMNI_API_KEY"] = "omni_osk_r0dvvwTfLkOC1QP6eomT65yOIWtjfDsU5gZpvKNdKWxHSrDJPT1RAUyV"

client = OmniApiClient()
```

## Usage (High-Level)
Below you'll find instructions on how to use the convenience methods to execute high-level, common tasks.

### Refresh a model
Refreshes a model to reflect the latest structures (schemas, views, fields) from the data source. This will remove any
structures that are no longer present in the source, but will not remove anything created by users.

```python
client.refresh_model("f0970eb8-785a-460b-9ced-cf603e160558")
```

## Usage (Low-Level)
Below you'll find instructions on how to use the low-level methods to interact directly with the Omni API.

### GET, POST, PUT, DELETE
There are methods available for making RESTful requests without having to deal with configuring the base url or 
authentication. The `path` argument for these methods should be the url path starting from `http://<OMNI_DOMAIN>/api`

```python title="RESTful Requests"

# GET 
client.get("/scim/v2/Users")

# POST
client.post("/scim/v2/Users", json_data={"displayName": "Somebody", "userName": "somebody"})

# PUT
client.put("/scim/v2/Groups/2208b2c2-ecc8-42ef-a576-caab9c1c58a7", json_data={"displayName": "Some Group"})

# DELETE
client.delete("/scim/v2/Users/2208b2c2-ecc8-42ef-a576-caab9c1c58a7")
```


