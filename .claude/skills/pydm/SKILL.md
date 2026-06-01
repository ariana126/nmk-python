---
name: pydm
description: >
  Helps work with pydm (PyPI: pydmpro), a Python dependency injection / IoC
  container library. Use when registering services, binding interfaces to
  implementations, wiring constructor dependencies, injecting runtime
  parameters from memory or environment variables, or resolving services from
  the container.
---

## Overview

`pydm` is a lightweight IoC container for Python (≥ 3.10). It automatically
resolves constructor dependencies using type hints, and all resolved services
are **singleton-scoped** (cached after first resolution).

Install:
```bash
pip install pydmpro
```

---

## Core concepts

| Concept | Description |
|---|---|
| `ServiceContainer` | Singleton IoC container — the entry point for everything |
| Interface binding | Map an abstract type to a concrete implementation |
| Factory binding | Delegate construction to a callable |
| Parameter binding | Inject scalar values (strings, ints, etc.) by argument name |
| `InMemoryParametersBag` | Parameter source backed by a plain dict |
| `EnvParametersBag` | Parameter source backed by `os.getenv()` |

---

## Usage patterns

### 1. Automatic resolution (zero config)

If all constructor arguments are typed services, no registration is needed:

```python
from pydm import ServiceContainer

class Database:
    pass

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

container = ServiceContainer.get_instance()
repo = container.get_service(UserRepository)  # Database resolved automatically
```

### 2. Binding an interface to an implementation

```python
from pydm import ServiceContainer

class PaymentGatewayInterface:
    pass

class StripeGateway(PaymentGatewayInterface):
    pass

container = ServiceContainer.get_instance()
container.bind(PaymentGatewayInterface, StripeGateway)

gateway = container.get_service(PaymentGatewayInterface)  # returns StripeGateway instance
```

### 3. Factory binding

Use when construction requires custom logic:

```python
container.bind_factory(SomeService, SomeServiceFactory, 'make') # Note that the third argument is string and the factory class should have a method by that name.
service = container.get_service(SomeService)
```

### 4. Injecting scalar parameters

Use when a constructor argument is a scalar (string, int, etc.) rather than a
service type:

```python
from pydm import ServiceContainer, InMemoryParametersBag

class ApiClient:
    def __init__(self, api_url: str, timeout: int):
        self.api_url = api_url
        self.timeout = timeout

bag = InMemoryParametersBag({"API_URL": "https://api.example.com", "API_TIMEOUT": 30})

container = ServiceContainer.get_instance()
container.bind_parameters(ApiClient, {
   'api_url': 'API_URL',
   'timeout': 'API_TIMEOUT',
})
# Keys are constructor argument names; values are ParametersBag var names.


client = container.get_service(ApiClient)
```

### 5. Injecting parameters from environment variables

```python
from pydm import ServiceContainer, EnvParametersBag

bag = EnvParametersBag()

container = ServiceContainer.get_instance()
container.bind_parameters(ApiClient, {
   'api_url': 'API_URL',
   'timeout': 'API_TIMEOUT',
})
# The EnvParametersBag will return os.getenv. So here there should be two envs named API_URL and API_TIMEOUT.
```

---

## Dependency resolution order

When `container.get_service(X)` is called:

1. Return cached instance if already resolved
2. Follow interface binding if one is registered for `X`
3. Delegate to factory if one is registered for `X`
4. Introspect `X.__init__` via `inspect.signature`:
   - Arguments mapped via `bind_parameters` → fetched from the `ParametersBag`
   - Everything else → resolved recursively as services

---

## Key constraints

- `ServiceContainer` is a **singleton** — always obtain it via `ServiceContainer.get_instance()`, never instantiate directly.
- All services are **singleton-scoped**: the container caches every resolved instance. There is no transient or scoped lifetime.
- `InMemoryParametersBag` is **immutable** after construction — pass all values at creation time.
- Constructor arguments must have **type annotations** for automatic resolution. Unannotated arguments must be covered by a `ParametersBag`.
- Circular dependencies are not resolved and will cause infinite recursion — design your graph accordingly.

---

## Common mistakes

| Mistake | Fix |
|---|---|
| `ServiceContainer()` directly | Use `ServiceContainer.get_instance()` |
| Missing type hint on constructor arg | Add type annotation or use `bind_parameters` |
| Mutating `InMemoryParametersBag` after creation | It is immutable — pass all values at construction |
| Expecting different instances per call | All services are singletons; the same instance is always returned |
| Forgetting to `bind` before `get_service` for interfaces | Call `container.bind(Interface, Impl)` first |
