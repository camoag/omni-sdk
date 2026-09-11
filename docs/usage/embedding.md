The SDK provides a convenience class for generating the url to embed dashboards, workbooks and apps in external
pages and signing it.
For more information on the options see the [Omni Docs](https://docs.omni.co/embed/setup/url-parameters).

## Creating the embedder
Configuration of the client can be handled using kwargs or environment variables. There is also the option to create
the embedder using your organization name or a vanity domain, more info on these options is below.

```python title="Kwarg Configuration - Organization Name"
from omni import OmniEmbedder

embedder = OmniEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
```

```python  title="Kwarg Configuration - Vanity Domain"
from omni import OmniEmbedder

embedder = OmniEmbedder(vanity_domain="acme.example.com", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
```


```python title="Environment Variable Configuration - Organization Name"
import os
from omni import OmniEmbedder

# For demonstration purposes only. The assumption is that these env vars are already set.
os.environ["OMNI_ORGANIZATION_NAME"] = "acme"
os.environ["OMNI_EMBED_SECRET"] = "vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC"

embedder = OmniEmbedder()
```

```python title="Environment Variable Configuration - Vanity Domain"
import os
from omni import OmniEmbedder

# For demonstration purposes only. The assumption is that these env vars are already set.
os.environ["OMNI_VANITY_DOMAIN"] = "acme.example.com"
os.environ["OMNI_EMBED_SECRET"] = "vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC"

embedder = OmniEmbedder()
```

## Generating an embedding URL.
The embedder has a method for each type of content you can embed. Each one takes the content ID, where the
content type has one, and signs the URL it builds. For more information on the options available please see the
[API Documentation](../api/OmniEmbedder.md) for the class.

```python title="Dashboard"
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
)
```

```python title="Workbook"
url = embedder.build_workbook_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
)
```

```python title="App"
url = embedder.build_app_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
)
```

```python title="Chat"
# Chat has no content ID - it always lives at "/chat".
url = embedder.build_chat_url(
    external_id="1",
    name="Somebody",
)
```

Multi-page dashboards can be opened on a specific page by passing its
[page key](https://docs.omni.co/visualize-present/dashboards/pages#page-key). Omitting it opens the
dashboard's first page.

```python title="Dashboard page"
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
    page_key="revenue",
)
```

Page keys are validated against one of Omni's reserved system values (`chat`, `download`, `drill`,
`edit`, `layout`, `monitor`, `move`, `performance`, `preview`, `publish`, `run`, `save-as`, `schedules`, `share`,
`themes`, `transfer`).

They all accept the same optional keyword arguments, which are documented on
[build_url](../api/OmniEmbedder.md#omni.OmniEmbedder.build_url). `build_url` is also available
directly if you need to embed a content path these helpers do not cover - pass the full path, e.g.
`content_path="/dashboards/da24491e"`.

```python
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
    custom_theme={
        "dashboard-background": "#00FF00",
        "dashboard-tile-background": "#00FF00",
    },
    entity="Acme",
    link_access=True,
    filter_search_params='f--object.id=%7B"is_inclusive"%3Afalse%2C"is_negative"%3Afalse%2C"kind"%3A"EQUALS"%2C"type"%3A"number"%2C"values"%3A%5B"1"%5D%7D',
    prefers_dark=OmniEmbedder.PrefersDark.yes,
    theme=OmniEmbedder.Theme.dawn,
    user_attributes={"country": "USA"},
)
```

## Signing Formats

Omni signs embed URLs using one of two formats:

- **v1** (default) - All parameters are carried as JSON inside a single signed `payload` query parameter.
- **v0** (legacy) - Each parameter is sent as its own query parameter. Omni will stop supporting this format after
  October 1, 2026 and remove it by January 1, 2027.

See the [Omni migration guide](https://docs.omni.co/embed/setup/standard-sso/migrate-to-latest) for details on what
changed between the two.

```python title="v1 (default)"
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
)
# https://acme.embed-omniapp.co/embed/login?payload=<payload>&signature=<signature>
```

```python title="v0 (legacy)"
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
    signing_version="v0",
)
# https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&...&signature=<signature>
```

### URL Expiry

Every v1 payload carries an `exp` value - the absolute moment the URL stops being valid. It defaults to 24 hours from
the time the URL is generated. Use the `expires_in` kwarg to set a different lifetime in seconds, up to a maximum of 7
days (604800 seconds).

```python
url = embedder.build_dashboard_url(
    content_id="da24491e",
    external_id="1",
    name="Somebody",
    expires_in=3600,  # Valid for one hour.
)
```

Shorter expiries are better. Until an embed URL is redeemed it is a bearer credential - anyone who has it can start
the session it describes - and URLs leak through browser history, referer headers, screenshots, and proxy logs.
Generate URLs on demand where you can, and only use a longer lifetime when needed, such as a URL that is emailed or
built by a nightly job.

The `expires_in` kwarg is accepted and ignored when `signing_version="v0"`, since v0 URLs have nowhere to carry an
expiry.

## Organization Name vs. Vanity Domain

The OmniEmbedder can be instantiated using either the `organization_name` or `vanity_domain` kwargs.
Instantiating with `organization_name` uses the standard Omni endpoint for the embedded dashboard URL. Alternatively,
Omni supports configuring a vanity domain to host embedded dashboards. You can learn about its advantages and setup
instructions [here](https://docs.omni.co/embed/customization/vanity-domains). Once your vanity domain is
set up, you can instantiate the OmniEmbedder with it to generate the correct URLs.

## Generating Filter Search Params

!!! note
    Support for dynamically generating filter search parameters is in early development and currently supports a
    limited set of filtering options. If you need specific filters that are not yet available, please create an issue.

Omni dashboard embedding allows passing filter values in the query string for the embedded dashboard. These filters are
represented as complex JSON-encoded strings. If the filter values you want to set are static, you can simply copy the
query string value from the example above.

For dynamically generating filter sets, the SDK provides a helper class, `OmniFilterSet`. This class is designed to
translate simplified query string parameters from your application's requests into the correct Omni format.

### Example: Generating filter search params in a Flask API view

The following example demonstrates how a Flask API view can generate a signed Omni embed URL. It defines a set of
filters and uses the query string arguments from the request to create the appropriate filter search parameters for the
embedded dashboard URL. Using the same names for the query string params and filter names in the `OmniFilterSet`
allows you to pass the Flask `requests.args` directly.

```python title="myapp/views.py"
from myapp import app
from flask import request
from omni import OmniEmbedder, OmniFilterSet, OmniFilterDefinition


@app.route("/omni_dashboard_url/")
def get_omni_dashboard_url():
    filter_set = OmniFilterSet(
        latitude=OmniFilterDefinition(
            field="address.latitude_filter",
            type=OmniFilterDefinition.Type.number,
        ),
        longitude=OmniFilterDefinition(
            field="address.longitude_filter",
            type=OmniFilterDefinition.Type.number,
        ),
        distance=OmniFilterDefinition(
            field="address.distance_selected_to_address_in_miles",
            type=OmniFilterDefinition.Type.number,
            operator=OmniFilterDefinition.Operator.less_than,
        ),
    )

    # Query string for this GET request - ?latitude=33.555&longitude=-117.602&distance=10
    # request.args == {"latitude": 33.555, "longitude": -117.602, "distance": 10}
    filter_search_params = filter_set.get_filter_search_params(request.args)

    embedder = OmniEmbedder(organization_name="acme", embed_secret="vglUd1WblfyBSdBSMPj0KrxZcNUEZ1CC")
    url = embedder.build_dashboard_url(
        content_id="da24491e",
        external_id="1",
        name="Somebody",
        filter_search_params=filter_search_params
    )
    return {"url": url}, 200
```

### Defining Filters
To define a filter you instantiate an instance of the `OmniFilterDefinition` class with 3 arguments – field, type, and
operator.

**`field`**

- Name of the Omni field to be filtered. Generally a dot-path representing a dimension in a view.
- You must have already created a filter for this field in the Omni dashboard to be embedded.

**`type`**

- Value type of the filter.
- Must pass an option from the OmniFilterDefinition.Type enum.
- Currently supported types - `number` and `string`


**`operator`**

- Type of filter operation to perform.
- Defaults to EQUALS.
- Must pass an option from the OmniFilterDefinition.Operator enum.
- Currently supported operators - `equals`, `less_than`, `greater_than`, `greater_than_or_equal`, `less_than_or_equal`, `between`, `contains`, `starts_with`, `ends_with`


In Omni, not all types support all operators. While there are no conflicts with the currently limited set of supported
types and operators, this may change as more are added.

The following types are supported for `number`:

- ✅ Equals
- ✅ Less than
- ✅ Less than or equal
- ✅ Greater than
- ✅ Greater than or equal
- ✅ Between

The following types are supported for `string`:

- ✅ Equals
- ✅ Contains
- ✅ Starts with
- ✅ Ends with
