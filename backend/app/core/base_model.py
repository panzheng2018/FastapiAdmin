from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship

from app.utils.common_util import uuid4_str


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类

    `AsyncAttrs <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs>`__

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__

    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__

    兼容 SQLite、MySQL 和 PostgreSQL
    """

    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class ModelMixin(MappedBase):
    """模型混入类 - 提供通用字段和功能

    基础模型混合类 Mixin: 一种面向对象编程概念, 使结构变得更加清晰

    数据隔离设计原则：
    ==================
    数据权限 (created_id/updated_id):
        - 配合角色的data_scope字段实现精细化权限控制
        - 1:仅本人
        - 2:本部门
        - 3:本部门及以下
        - 4:全部数据
        - 5:自定义

    SQLAlchemy加载策略说明:
    - select(默认): 延迟加载,访问时单独查询
    - joined: 使用LEFT JOIN预加载
    - selectin: 使用IN查询批量预加载(推荐用于一对多)
    - subquery: 使用子查询预加载
    - raise/raise_on_sql: 禁止加载
    - noload: 不加载,返回None
    - immediate: 立即加载
    - write_only: 只写不读
    - dynamic: 返回查询对象,支持进一步过滤
    """

    __abstract__: bool = True

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        table_name = cls.__tablename__ if hasattr(cls, '__tablename__') else cls.__name__.lower()
        return (
            Index(f"ix_{table_name}_status_deleted", "status", "is_deleted"),
            Index(f"ix_{table_name}_created_deleted", "created_time", "is_deleted"),
        )

    # 基础字段
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
        index=True,
    )
    uuid: Mapped[str] = mapped_column(
        String(64),
        default=uuid4_str,
        nullable=False,
        unique=True,
        comment="UUID全局唯一标识",
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已删除(0:未删除 1:已删除)",
        index=True,
    )
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        comment="创建时间",
        index=True,
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        comment="更新时间",
    )
    deleted_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        comment="删除时间",
    )


class UserMixin(MappedBase):
    """用户审计字段 Mixin

    CRUD（base_crud.py）会自动检测并预加载 created_by/updated_by（使用 joinedload，一对一关系最高效），
    无需在 service 层显式声明。deleted_by 仅在回收站等特定场景需要时通过 preload 参数显式获取。
    """

    __abstract__: bool = True

    created_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="SET NULL", onupdate="CASCADE"),
        default=None,
        nullable=True,
        index=True,
        comment="创建人ID",
    )
    updated_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="SET NULL", onupdate="CASCADE"),
        default=None,
        nullable=True,
        index=True,
        comment="更新人ID",
    )

    deleted_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="SET NULL", onupdate="CASCADE"),
        default=None,
        nullable=True,
        index=True,
        comment="删除人ID",
    )

    @declared_attr
    def created_by(self):
        """创建人关联关系"""
        return relationship(
            "UserModel",
            foreign_keys=lambda: self.created_id,  # pyright: ignore[reportArgumentType]
            uselist=False,
        )

    @declared_attr
    def updated_by(self):
        """更新人关联关系"""
        return relationship(
            "UserModel",
            foreign_keys=lambda: self.updated_id,  # pyright: ignore[reportArgumentType]
            uselist=False,
        )

    @declared_attr
    def deleted_by(self):
        """删除人关联关系"""
        return relationship(
            "UserModel",
            foreign_keys=lambda: self.deleted_id,  # pyright: ignore[reportArgumentType]
            uselist=False,
        )


class ModelMy(MappedBase):
    """自定义通用业务模型类（无软删除物理字段，以 status='1' 标识停用/删除）

    包含字段：
    - id: int 主键自增
    - uuid: varchar(64) UUID全局唯一标识
    - status: varchar(8) 是否启用(0:启用 1:禁用)
    - description: text 备注/描述
    - created_time: datetime 创建时间
    - updated_time: datetime 更新时间
    - created_id: int 创建人ID
    - updated_id: int 更新人ID
    - created_by: 关联创建人模型 (joinedload)
    - updated_by: 关联更新人模型 (joinedload)

    删除行为：
    - 调用 delete() 时不执行真正的 SQL 物理删除，而是将 status 更新为 '1'（禁用），并记录 updated_time 与 updated_id。
    查询行为：
    - list() / page() / get() 无任何额外的隐式过滤条件，直接查表中现存的真实数据，由前端展示启用/禁用状态。
    """

    __abstract__: bool = True
    __status_delete__: bool = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
        index=True,
    )
    uuid: Mapped[str] = mapped_column(
        String(64),
        default=uuid4_str,
        nullable=False,
        unique=True,
        comment="UUID全局唯一标识",
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(8),
        default="0",
        nullable=False,
        comment="是否启用(0:启用 1:禁用)",
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        default=None,
        nullable=True,
        comment="备注/描述",
    )
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间",
        index=True,
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间",
    )
    created_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="创建人ID",
    )
    updated_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="更新人ID",
    )

    @declared_attr
    def created_by(self):
        """创建人关联关系"""
        return relationship(
            "UserModel",
            foreign_keys=lambda: self.created_id,  # pyright: ignore[reportArgumentType]
            uselist=False,
        )

    @declared_attr
    def updated_by(self):
        """更新人关联关系"""
        return relationship(
            "UserModel",
            foreign_keys=lambda: self.updated_id,  # pyright: ignore[reportArgumentType]
            uselist=False,
        )

