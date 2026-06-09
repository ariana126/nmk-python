# SQLAlchemy Imperative Mapping: Relationship Examples

Domain classes are never SQLAlchemy declarative models. Tables are defined with `Table(...)` in `tables.py` and domain classes are wired to them via `mapper_registry.map_imperatively()` in `mapper.py`. Because domain attributes use Python's double-underscore name mangling (`self.__attr` becomes `_ClassName__attr` at the bytecode level), the keys in `properties={}` must use the mangled form — e.g. `"_Order__lines"` for `self.__lines` on `Order`.

---

## One-to-Many

An aggregate root owns a collection of child entities within the same aggregate boundary. The child table holds a foreign key back to the parent.

**Domain classes**

```python
# order/domain/order_line.py
from ddd import Entity, Identity

class OrderLine(Entity):
    def __init__(self, id_: Identity, product_name: str, quantity: int, unit_price: float):
        self.__product_name = product_name
        self.__quantity = quantity
        self.__unit_price = unit_price
        super().__init__(id_)

    @property
    def product_name(self) -> str: return self.__product_name

    @property
    def quantity(self) -> int: return self.__quantity

    @property
    def unit_price(self) -> float: return self.__unit_price
```

```python
# order/domain/order.py
from ddd import AggregateRoot, Identity
from order.domain.order_line import OrderLine

class Order(AggregateRoot):
    def __init__(self, id_: Identity):
        super().__init__(id_)
        self.__lines: list[OrderLine] = []

    @property
    def lines(self) -> list[OrderLine]: return list(self.__lines)

    def add_line(self, line: OrderLine) -> None:
        self.__lines.append(line)
```

**Tables**

```python
# order/infrastructure/persistence/tables.py
from sqlalchemy import Table, Column, String, Integer, Numeric, ForeignKey
from framework.infrastructure.persistence.mapper import mapper_registry
from framework.infrastructure.persistence.types import IdentityType

orders_table = Table(
    "orders",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
)

order_lines_table = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("order_id", IdentityType, ForeignKey("orders.id"), nullable=False),
    Column("product_name", String, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Numeric(10, 2), nullable=False),
)
```

**Mapper**

```python
# order/infrastructure/persistence/mapper.py
from sqlalchemy import event
from sqlalchemy.orm import relationship
from framework.infrastructure.persistence.mapper import mapper_registry
from order.domain.order import Order
from order.domain.order_line import OrderLine
from order.infrastructure.persistence.tables import orders_table, order_lines_table

_mappers_configured = False

def start_mappers() -> None:
    global _mappers_configured
    if _mappers_configured:
        return

    # Map the child first so SQLAlchemy can resolve the relationship target.
    mapper_registry.map_imperatively(
        OrderLine,
        order_lines_table,
        properties={
            "_id": order_lines_table.c.id,
            "_OrderLine__product_name": order_lines_table.c.product_name,
            "_OrderLine__quantity": order_lines_table.c.quantity,
            "_OrderLine__unit_price": order_lines_table.c.unit_price,
        },
    )

    mapper_registry.map_imperatively(
        Order,
        orders_table,
        properties={
            "_id": orders_table.c.id,
            "_Order__lines": relationship(
                OrderLine,
                cascade="all, delete-orphan",
                lazy="selectin",
            ),
        },
    )

    @event.listens_for(Order, "load")
    def _on_load(target: Order, context) -> None:
        target._AggregateRoot__events = []

    _mappers_configured = True
```

> **Notes:**
> - Map child entities (`OrderLine`) **before** the aggregate root (`Order`) so SQLAlchemy can resolve the relationship target.
> - `cascade="all, delete-orphan"` deletes orphaned `OrderLine` rows when they are removed from `Order.__lines` or when the `Order` itself is deleted.
> - `lazy="selectin"` loads the collection with a single extra `IN` query — avoids N+1 without needing a join.
> - The `_on_load` listener is registered only on `Order` (the `AggregateRoot`), not on `OrderLine` (an `Entity`). Only aggregate roots accumulate domain events.

---

## Many-to-One

The inverse back-reference from a child entity to its parent aggregate. In DDD this is rarely necessary — children are always accessed through the aggregate root, not the other way around. Include it only when the ORM genuinely needs to traverse child → parent.

Add the back-reference attribute to `OrderLine` and link both sides with `back_populates`:

```python
# domain: add to OrderLine.__init__
self.__order: "Order | None" = None
```

```python
# mapper.py — replace the two map_imperatively calls
mapper_registry.map_imperatively(
    OrderLine,
    order_lines_table,
    properties={
        "_id": order_lines_table.c.id,
        "_OrderLine__product_name": order_lines_table.c.product_name,
        "_OrderLine__quantity": order_lines_table.c.quantity,
        "_OrderLine__unit_price": order_lines_table.c.unit_price,
        "_OrderLine__order": relationship(Order, back_populates="_Order__lines"),
    },
)

mapper_registry.map_imperatively(
    Order,
    orders_table,
    properties={
        "_id": orders_table.c.id,
        "_Order__lines": relationship(
            OrderLine,
            cascade="all, delete-orphan",
            lazy="selectin",
            back_populates="_OrderLine__order",
        ),
    },
)
```

> `back_populates` takes the ORM attribute name on the other class — the mangled key used in `properties={}` (`"_OrderLine__order"`, `"_Order__lines"`), not a Python identifier you'd write yourself.

---

## One-to-One

One aggregate root owns exactly one child entity. `uselist=False` tells SQLAlchemy the relationship returns a scalar rather than a list.

**Domain classes**

```python
# user/domain/user_profile.py
from ddd import Entity, Identity

class UserProfile(Entity):
    def __init__(self, id_: Identity, bio: str, avatar_url: str):
        self.__bio = bio
        self.__avatar_url = avatar_url
        super().__init__(id_)

    @property
    def bio(self) -> str: return self.__bio

    @property
    def avatar_url(self) -> str: return self.__avatar_url
```

```python
# user/domain/user.py
from ddd import AggregateRoot, Identity
from user.domain.user_profile import UserProfile

class User(AggregateRoot):
    def __init__(self, id_: Identity, profile: "UserProfile | None" = None):
        super().__init__(id_)
        self.__profile: UserProfile | None = profile

    @property
    def profile(self) -> "UserProfile | None": return self.__profile
```

**Tables**

```python
user_profiles_table = Table(
    "user_profiles",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("user_id", IdentityType, ForeignKey("app_user.id"), nullable=False, unique=True),
    Column("bio", String, nullable=True),
    Column("avatar_url", String, nullable=True),
)
```

**Mapper**

```python
mapper_registry.map_imperatively(
    UserProfile,
    user_profiles_table,
    properties={
        "_id": user_profiles_table.c.id,
        "_UserProfile__bio": user_profiles_table.c.bio,
        "_UserProfile__avatar_url": user_profiles_table.c.avatar_url,
    },
)

mapper_registry.map_imperatively(
    User,
    users_table,
    properties={
        "_id": users_table.c.id,
        # ... other column mappings ...
        "_User__profile": relationship(
            UserProfile,
            uselist=False,
            cascade="all, delete-orphan",
            lazy="joined",
        ),
    },
)

@event.listens_for(User, "load")
def _on_load(target: User, context) -> None:
    target._AggregateRoot__events = []
```

> `lazy="joined"` fetches the profile in the same query as the parent via a `LEFT JOIN` — suitable when the child is almost always needed alongside its parent, which is typical for one-to-one ownership.

---

## Many-to-Many

Two classes reference each other through a pure association table that holds only the two foreign keys. No domain class maps to the association table — SQLAlchemy manages it automatically via `secondary`.

**Domain classes**

```python
# role/domain/role.py
from ddd import AggregateRoot, Identity

class Role(AggregateRoot):
    def __init__(self, id_: Identity, name: str):
        super().__init__(id_)
        self.__name = name

    @property
    def name(self) -> str: return self.__name
```

```python
# user/domain/user.py
from ddd import AggregateRoot, Identity
from role.domain.role import Role

class User(AggregateRoot):
    def __init__(self, id_: Identity):
        super().__init__(id_)
        self.__roles: list[Role] = []

    @property
    def roles(self) -> list[Role]: return list(self.__roles)

    def assign_role(self, role: Role) -> None:
        self.__roles.append(role)
```

**Tables**

```python
roles_table = Table(
    "roles",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("name", String, nullable=False, unique=True),
)

user_roles_table = Table(
    "user_roles",
    mapper_registry.metadata,
    Column("user_id", IdentityType, ForeignKey("app_user.id"), primary_key=True),
    Column("role_id", IdentityType, ForeignKey("roles.id"), primary_key=True),
)
```

**Mapper**

```python
mapper_registry.map_imperatively(
    Role,
    roles_table,
    properties={
        "_id": roles_table.c.id,
        "_Role__name": roles_table.c.name,
    },
)

@event.listens_for(Role, "load")
def _on_role_load(target: Role, context) -> None:
    target._AggregateRoot__events = []

mapper_registry.map_imperatively(
    User,
    users_table,
    properties={
        "_id": users_table.c.id,
        # ... other column mappings ...
        "_User__roles": relationship(
            Role,
            secondary=user_roles_table,
            lazy="selectin",
        ),
    },
)

@event.listens_for(User, "load")
def _on_user_load(target: User, context) -> None:
    target._AggregateRoot__events = []
```

> **Notes:**
> - `user_roles_table` is never passed to `map_imperatively()` — it is only referenced as `secondary`.
> - Because `Role` is its own aggregate root, the `_on_load` listener must be registered for it separately.
> - No `cascade` here: removing a `User` deletes the association rows in `user_roles`, but leaves the `Role` aggregates intact.

---

## Cross-Aggregate Reference

When one aggregate references another, do **not** use `relationship()`. Store only the referenced aggregate's `Identity` as a plain `IdentityType` column and load the referenced aggregate through its own repository when needed.

**Domain class**

```python
# post/domain/post.py
from ddd import AggregateRoot, Identity

class Post(AggregateRoot):
    def __init__(self, id_: Identity, author_id: Identity, title: str, body: str):
        super().__init__(id_)
        self.__author_id = author_id   # Identity only — no User object
        self.__title = title
        self.__body = body

    @property
    def author_id(self) -> Identity: return self.__author_id
```

**Table**

```python
# post/infrastructure/persistence/tables.py
posts_table = Table(
    "posts",
    mapper_registry.metadata,
    Column("id", IdentityType, primary_key=True),
    Column("author_id", IdentityType, nullable=False),
    Column("title", String, nullable=False),
    Column("body", String, nullable=False),
)
```

**Mapper**

```python
mapper_registry.map_imperatively(
    Post,
    posts_table,
    properties={
        "_id": posts_table.c.id,
        "_Post__author_id": posts_table.c.author_id,
        "_Post__title": posts_table.c.title,
        "_Post__body": posts_table.c.body,
    },
)

@event.listens_for(Post, "load")
def _on_load(target: Post, context) -> None:
    target._AggregateRoot__events = []
```

> Using `relationship()` across aggregate boundaries creates implicit coupling and can trigger accidental lazy-loading chains that violate transactional consistency. Store only the `Identity` and resolve the referenced aggregate through its `EntityRepository` at the application layer instead.
>
> A database-level `ForeignKey` constraint on `author_id` is a separate concern from the ORM relationship and is optional — some teams omit it across aggregate boundaries for operational flexibility (e.g. soft deletes, eventual consistency); others keep it for referential integrity.
