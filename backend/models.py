from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================
# Phase 2: Material / Inventory / Product / BOM / StockMove
# =========================

class Material(db.Model):
    __tablename__ = "materials"
    id = db.Column(db.Integer, primary_key=True)

    material_code = db.Column(db.String(64), unique=True, nullable=False)
    material_name = db.Column(db.String(128), nullable=False)

    drawing_no = db.Column(db.String(128), nullable=True)    # 图号
    material_type = db.Column(db.String(64), nullable=True)  # 自制/外购/标准件
    remark = db.Column(db.String(255), nullable=True)        # 备注

    unit = db.Column(db.String(16), nullable=False, default="pcs")
    safety_stock = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "drawing_no": self.drawing_no,
            "material_type": self.material_type,
            "remark": self.remark,
            "unit": self.unit,
            "safety_stock": self.safety_stock,
        }


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)

    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), unique=True, nullable=False)
    on_hand = db.Column(db.Integer, nullable=False, default=0)
    reserved = db.Column(db.Integer, nullable=False, default=0)

    material = db.relationship("Material")

    def to_dict(self):
        available = self.on_hand - self.reserved
        return {
            "id": self.id,
            "material_id": self.material_id,
            "material_code": self.material.material_code if self.material else None,
            "material_name": self.material.material_name if self.material else None,
            "unit": self.material.unit if self.material else None,
            "safety_stock": self.material.safety_stock if self.material else 0,
            "on_hand": self.on_hand,
            "reserved": self.reserved,
            "available": available,
        }


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)

    product_code = db.Column(db.String(64), unique=True, nullable=False)
    product_name = db.Column(db.String(128), nullable=False)
    version = db.Column(db.String(32), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "product_code": self.product_code,
            "product_name": self.product_name,
            "version": self.version,
        }


class BOMItem(db.Model):
    __tablename__ = "bom_items"
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    qty_per_unit = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship("Product")
    material = db.relationship("Material")

    __table_args__ = (
        db.UniqueConstraint("product_id", "material_id", name="uq_bom_product_material"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_code": self.product.product_code if self.product else None,
            "product_name": self.product.product_name if self.product else None,
            "material_id": self.material_id,
            "material_code": self.material.material_code if self.material else None,
            "material_name": self.material.material_name if self.material else None,
            "unit": self.material.unit if self.material else None,
            "qty_per_unit": self.qty_per_unit,
        }


class StockMove(db.Model):
    __tablename__ = "stock_moves"
    id = db.Column(db.Integer, primary_key=True)

    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)              # +入库 / -出库
    move_type = db.Column(db.String(16), nullable=False)     # IN / OUT / ADJUST
    ref_type = db.Column(db.String(32), nullable=True)       # TASK / MANUAL
    ref_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship("Material")

    def to_dict(self):
        return {
            "id": self.id,
            "material_id": self.material_id,
            "material_code": self.material.material_code if self.material else None,
            "qty": self.qty,
            "move_type": self.move_type,
            "ref_type": self.ref_type,
            "ref_id": self.ref_id,
            "created_at": self.created_at.isoformat(),
        }


# =========================
# Phase 1: Mold / Task / Report
# =========================

class Mold(db.Model):
    __tablename__ = "molds"
    id = db.Column(db.Integer, primary_key=True)

    mold_code = db.Column(db.String(64), unique=True, nullable=False)
    mold_name = db.Column(db.String(128), nullable=False)
    total_life = db.Column(db.Integer, nullable=False, default=0)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(16), nullable=False, default="空闲")  # 使用中/空闲/维修
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "mold_code": self.mold_code,
            "mold_name": self.mold_name,
            "total_life": self.total_life,
            "used_count": self.used_count,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)

    task_no = db.Column(db.String(64), unique=True, nullable=False)
    mold_id = db.Column(db.Integer, db.ForeignKey("molds.id"), nullable=False)

    # Phase2: 可选绑定产品
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    operator_name = db.Column(db.String(64), nullable=False)
    target_qty = db.Column(db.Integer, nullable=False, default=0)
    done_qty = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(16), nullable=False, default="进行中")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mold = db.relationship("Mold")
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "task_no": self.task_no,
            "mold_id": self.mold_id,
            "mold_code": self.mold.mold_code if self.mold else None,
            "mold_name": self.mold.mold_name if self.mold else None,
            "product_id": self.product_id,
            "product_code": self.product.product_code if self.product else None,
            "product_name": self.product.product_name if self.product else None,
            "operator_name": self.operator_name,
            "target_qty": self.target_qty,
            "done_qty": self.done_qty,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class TaskMaterialRequirement(db.Model):
    __tablename__ = "task_material_requirements"
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    required_qty = db.Column(db.Integer, nullable=False, default=0)
    issued_qty = db.Column(db.Integer, nullable=False, default=0)

    task = db.relationship("Task")
    material = db.relationship("Material")

    __table_args__ = (
        db.UniqueConstraint("task_id", "material_id", name="uq_task_material"),
    )

    def to_dict(self):
        shortage = max(self.required_qty - self.issued_qty, 0)
        return {
            "id": self.id,
            "task_id": self.task_id,
            "material_id": self.material_id,
            "material_code": self.material.material_code if self.material else None,
            "material_name": self.material.material_name if self.material else None,
            "unit": self.material.unit if self.material else None,
            "required_qty": self.required_qty,
            "issued_qty": self.issued_qty,
            "shortage_qty": shortage,
        }


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship("Task")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_no": self.task.task_no if self.task else None,
            "qty": self.qty,
            "created_at": self.created_at.isoformat(),
        }
