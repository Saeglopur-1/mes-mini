from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from config import Config
from models import (
    db,
    Mold, Task, Report,
    Material, Inventory, Product, BOMItem, StockMove,
    TaskMaterialRequirement
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JSON_AS_ASCII"] = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    @app.get("/api/health")
    def health():
        return {"ok": True, "time": datetime.utcnow().isoformat()}

    # =========================
    # Phase 1: Molds CRUD
    # =========================
    @app.get("/api/molds")
    def list_molds():
        q = request.args.get("q", "").strip()
        query = Mold.query
        if q:
            query = query.filter((Mold.mold_code.contains(q)) | (Mold.mold_name.contains(q)))
        molds = query.order_by(Mold.id.desc()).all()
        return jsonify([m.to_dict() for m in molds])

    @app.post("/api/molds")
    def create_mold():
        data = request.get_json(force=True)
        m = Mold(
            mold_code=str(data.get("mold_code", "")).strip(),
            mold_name=str(data.get("mold_name", "")).strip(),
            total_life=int(data.get("total_life", 0) or 0),
            used_count=int(data.get("used_count", 0) or 0),
            status=str(data.get("status", "空闲")).strip(),
        )
        if not m.mold_code or not m.mold_name:
            return jsonify({"error": "mold_code 和 mold_name 必填"}), 400
        db.session.add(m)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "模具编号已存在"}), 409
        return jsonify(m.to_dict()), 201

    @app.put("/api/molds/<int:mold_id>")
    def update_mold(mold_id):
        m = Mold.query.get_or_404(mold_id)
        data = request.get_json(force=True)
        for k in ["mold_code", "mold_name", "status"]:
            if k in data and data[k] is not None:
                setattr(m, k, str(data[k]).strip())
        for k in ["total_life", "used_count"]:
            if k in data and data[k] is not None:
                setattr(m, k, int(data[k] or 0))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "模具编号已存在"}), 409
        return jsonify(m.to_dict())

    @app.delete("/api/molds/<int:mold_id>")
    def delete_mold(mold_id):
        m = Mold.query.get_or_404(mold_id)
        db.session.delete(m)
        db.session.commit()
        return "", 204

    # =========================
    # Phase 2: Materials CRUD
    # =========================
    @app.get("/api/materials")
    def list_materials():
        mats = Material.query.order_by(Material.id.desc()).all()
        return jsonify([m.to_dict() for m in mats])

    @app.post("/api/materials")
    def create_material():
        data = request.get_json(force=True)
        code = str(data.get("material_code", "")).strip()
        name = str(data.get("material_name", "")).strip()
        if not code or not name:
            return jsonify({"error": "material_code/material_name 必填"}), 400

        m = Material(
            material_code=code,
            material_name=name,
            drawing_no=str(data.get("drawing_no", "")).strip() or None,
            material_type=str(data.get("material_type", "")).strip() or None,
            remark=str(data.get("remark", "")).strip() or None,
            unit=str(data.get("unit", "pcs")).strip() or "pcs",
            safety_stock=int(data.get("safety_stock", 0) or 0),
        )
        db.session.add(m)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "物料编码已存在"}), 409

        # 自动建库存行
        if not Inventory.query.filter_by(material_id=m.id).first():
            db.session.add(Inventory(material_id=m.id, on_hand=0, reserved=0))
            db.session.commit()

        return jsonify(m.to_dict()), 201

    @app.put("/api/materials/<int:material_id>")
    def update_material(material_id):
        m = Material.query.get_or_404(material_id)
        data = request.get_json(force=True)

        if "material_code" in data and data["material_code"] is not None:
            m.material_code = str(data["material_code"]).strip()
        if "material_name" in data and data["material_name"] is not None:
            m.material_name = str(data["material_name"]).strip()
        if "drawing_no" in data:
            v = str(data.get("drawing_no", "")).strip()
            m.drawing_no = v or None
        if "material_type" in data:
            v = str(data.get("material_type", "")).strip()
            m.material_type = v or None
        if "remark" in data:
            v = str(data.get("remark", "")).strip()
            m.remark = v or None
        if "unit" in data and data["unit"] is not None:
            m.unit = str(data["unit"]).strip() or "pcs"
        if "safety_stock" in data and data["safety_stock"] is not None:
            m.safety_stock = int(data["safety_stock"] or 0)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "物料编码已存在"}), 409
        return jsonify(m.to_dict())

    @app.delete("/api/materials/<int:material_id>")
    def delete_material(material_id):
        m = Material.query.get_or_404(material_id)
        inv = Inventory.query.filter_by(material_id=m.id).first()
        if inv:
            db.session.delete(inv)
        db.session.delete(m)
        db.session.commit()
        return "", 204

    # =========================
    # Phase 2: Products CRUD
    # =========================
    @app.get("/api/products")
    def list_products():
        items = Product.query.order_by(Product.id.desc()).all()
        return jsonify([p.to_dict() for p in items])

    @app.post("/api/products")
    def create_product():
        data = request.get_json(force=True)
        code = str(data.get("product_code", "")).strip()
        name = str(data.get("product_name", "")).strip()
        if not code or not name:
            return jsonify({"error": "product_code/product_name 必填"}), 400

        p = Product(
            product_code=code,
            product_name=name,
            version=str(data.get("version", "")).strip() or None
        )
        db.session.add(p)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "产品编码已存在"}), 409
        return jsonify(p.to_dict()), 201

    @app.put("/api/products/<int:product_id>")
    def update_product(product_id):
        p = Product.query.get_or_404(product_id)
        data = request.get_json(force=True)
        if "product_code" in data and data["product_code"] is not None:
            p.product_code = str(data["product_code"]).strip()
        if "product_name" in data and data["product_name"] is not None:
            p.product_name = str(data["product_name"]).strip()
        if "version" in data:
            v = str(data.get("version", "")).strip()
            p.version = v or None
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "产品编码已存在"}), 409
        return jsonify(p.to_dict())

    @app.delete("/api/products/<int:product_id>")
    def delete_product(product_id):
        p = Product.query.get_or_404(product_id)
        BOMItem.query.filter_by(product_id=p.id).delete()
        db.session.delete(p)
        db.session.commit()
        return "", 204

    # =========================
    # Phase 2: BOM (product bom)
    # =========================
    @app.get("/api/products/<int:product_id>/bom")
    def get_product_bom(product_id):
        Product.query.get_or_404(product_id)
        items = BOMItem.query.filter_by(product_id=product_id).all()
        return jsonify([x.to_dict() for x in items])

    @app.post("/api/products/<int:product_id>/bom")
    def upsert_product_bom(product_id):
        Product.query.get_or_404(product_id)
        data = request.get_json(force=True)
        material_id = int(data.get("material_id") or 0)
        qty_per_unit = int(data.get("qty_per_unit") or 0)
        if material_id <= 0 or qty_per_unit <= 0:
            return jsonify({"error": "material_id/qty_per_unit 必填且 >0"}), 400

        Material.query.get_or_404(material_id)

        item = BOMItem.query.filter_by(product_id=product_id, material_id=material_id).first()
        if item:
            item.qty_per_unit = qty_per_unit
        else:
            db.session.add(BOMItem(product_id=product_id, material_id=material_id, qty_per_unit=qty_per_unit))
        db.session.commit()
        return jsonify({"ok": True})

    @app.delete("/api/bom_items/<int:item_id>")
    def delete_bom_item(item_id):
        item = BOMItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return "", 204

    # =========================
    # Phase 2: Inventory
    # =========================
    @app.get("/api/inventory")
    def list_inventory():
        invs = Inventory.query.order_by(Inventory.id.desc()).all()
        return jsonify([i.to_dict() for i in invs])

    @app.post("/api/inventory/in")
    def inventory_in():
        data = request.get_json(force=True)
        material_id = int(data.get("material_id") or 0)
        qty = int(data.get("qty") or 0)
        if material_id <= 0 or qty <= 0:
            return jsonify({"error": "material_id/qty 必填且 qty>0"}), 400

        inv = Inventory.query.filter_by(material_id=material_id).first()
        if not inv:
            return jsonify({"error": "库存行不存在"}), 404

        inv.on_hand += qty
        db.session.add(StockMove(material_id=material_id, qty=qty, move_type="IN", ref_type="MANUAL", ref_id=None))
        db.session.commit()
        return jsonify(inv.to_dict())

    # =========================
    # Tasks + requirements (MRP-lite)
    # =========================
    @app.get("/api/tasks")
    def list_tasks():
        tasks = Task.query.order_by(Task.id.desc()).all()
        return jsonify([t.to_dict() for t in tasks])

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(force=True)
        task_no = str(data.get("task_no", "")).strip()
        mold_id = int(data.get("mold_id") or 0)
        operator_name = str(data.get("operator_name", "")).strip()
        target_qty = int(data.get("target_qty", 0) or 0)

        product_id = data.get("product_id")
        product_id = int(product_id) if product_id else None

        if not task_no or mold_id <= 0 or not operator_name or target_qty <= 0:
            return jsonify({"error": "task_no/mold_id/operator_name 必填且 target_qty>0"}), 400

        mold = Mold.query.get(mold_id)
        if not mold:
            return jsonify({"error": "模具不存在"}), 404

        if product_id is not None and not Product.query.get(product_id):
            return jsonify({"error": "产品不存在"}), 404

        t = Task(
            task_no=task_no,
            mold_id=mold_id,
            product_id=product_id,
            operator_name=operator_name,
            target_qty=target_qty,
            done_qty=0,
            status="进行中",
        )
        db.session.add(t)
        mold.status = "使用中"

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "任务单号已存在"}), 409

        # 绑定产品：按 BOM 自动生成需求
        if t.product_id:
            bom = BOMItem.query.filter_by(product_id=t.product_id).all()
            for bi in bom:
                required = bi.qty_per_unit * t.target_qty
                exist = TaskMaterialRequirement.query.filter_by(task_id=t.id, material_id=bi.material_id).first()
                if exist:
                    exist.required_qty = required
                else:
                    db.session.add(TaskMaterialRequirement(
                        task_id=t.id, material_id=bi.material_id, required_qty=required, issued_qty=0
                    ))
            db.session.commit()

        return jsonify(t.to_dict()), 201

    @app.get("/api/tasks/<int:task_id>/materials")
    def task_materials(task_id):
        Task.query.get_or_404(task_id)
        items = TaskMaterialRequirement.query.filter_by(task_id=task_id).all()
        return jsonify([x.to_dict() for x in items])

    @app.post("/api/tasks/<int:task_id>/issue")
    def issue_to_task(task_id):
        data = request.get_json(force=True)
        material_id = int(data.get("material_id") or 0)
        qty = int(data.get("qty") or 0)
        if material_id <= 0 or qty <= 0:
            return jsonify({"error": "material_id/qty 必填且 qty>0"}), 400

        t = Task.query.get_or_404(task_id)
        inv = Inventory.query.filter_by(material_id=material_id).first()
        if not inv:
            return jsonify({"error": "库存行不存在"}), 404
        if inv.on_hand < qty:
            return jsonify({"error": "库存不足"}), 400

        req = TaskMaterialRequirement.query.filter_by(task_id=t.id, material_id=material_id).first()
        if not req:
            return jsonify({"error": "该任务未生成此物料需求"}), 400

        inv.on_hand -= qty
        req.issued_qty += qty
        db.session.add(StockMove(material_id=material_id, qty=-qty, move_type="OUT", ref_type="TASK", ref_id=t.task_no))
        db.session.commit()
        return jsonify({"inventory": inv.to_dict(), "requirement": req.to_dict()})
    
    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        # 如果任务是进行中，将模具状态改回空闲
        if task.status == "进行中":
            mold = Mold.query.get(task.mold_id)
            if mold and mold.status == "使用中":
                mold.status = "空闲"
        # 删除关联的用料需求（如果有外键级联可省略）
        TaskMaterialRequirement.query.filter_by(task_id=task.id).delete()
        db.session.delete(task)
        db.session.commit()
        return "", 204


    # =========================
    # Phase 1: Mobile report
    # =========================
    @app.post("/api/report")
    def report_work():
        data = request.get_json(force=True)
        task_no = str(data.get("task_no", "")).strip()
        qty = int(data.get("qty", 0) or 0)
        if not task_no or qty <= 0:
            return jsonify({"error": "task_no 必填且 qty>0"}), 400

        t = Task.query.filter_by(task_no=task_no).first()
        if not t:
            return jsonify({"error": "任务单号不存在"}), 404

        mold = Mold.query.get(t.mold_id)
        if not mold:
            return jsonify({"error": "关联模具不存在"}), 500

        t.done_qty += qty
        mold.used_count += qty

        if t.done_qty >= t.target_qty:
            t.done_qty = min(t.done_qty, t.target_qty)
            t.status = "已完成"
            mold.status = "空闲"

        db.session.add(Report(task_id=t.id, qty=qty))
        db.session.commit()
        return jsonify({"task": t.to_dict(), "mold": mold.to_dict()}), 201

    # =========================
    # Tree BOM Import (TSV)
    # =========================
    @app.post("/api/bom/import_tree")
    def import_bom_tree():
        """
        输入 TSV（制表符分隔），表头必须为：
        层级  物料编码  名称  图号  数量  单位  类型  备注

        层级：0 / .1 / ..2 / ...3 通过前导 '.' 个数确定 depth
        规则：每一行会 upsert Material；并将每个节点也 upsert 为 Product（用于展开）
             BOM：父节点(Product) -> 子节点(Material)，qty_per_unit=数量
        """
        data = request.get_json(force=True)
        tsv = str(data.get("tsv", "")).strip()
        if not tsv:
            return jsonify({"error": "tsv 不能为空"}), 400

        lines = [ln for ln in tsv.splitlines() if ln.strip()]
        if len(lines) < 2:
            return jsonify({"error": "至少包含表头+1行数据"}), 400

        header = [h.strip() for h in lines[0].split("\t")]
        expected = ["层级", "物料编码", "名称", "图号", "数量", "单位", "类型", "备注"]
        if header[:8] != expected:
            return jsonify({"error": f"表头必须为：{expected}"}), 400

        created_bom, updated_bom, skipped = 0, 0, 0
        stack = {}  # depth -> Product

        for ln in lines[1:]:
            cols = [c.strip() for c in ln.split("\t")]
            if len(cols) < 8:
                skipped += 1
                continue

            level_str, code, name, drawing_no, qty_str, unit, typ, remark = cols[:8]
            if not code or not name:
                skipped += 1
                continue

            # depth = leading '.' count
            depth = 0
            for ch in level_str:
                if ch == ".":
                    depth += 1
                else:
                    break

            try:
                qty = int(float(qty_str))
            except:
                skipped += 1
                continue
            if qty <= 0:
                skipped += 1
                continue

            # upsert material
            m = Material.query.filter_by(material_code=code).first()
            if not m:
                m = Material(
                    material_code=code,
                    material_name=name,
                    drawing_no=drawing_no or None,
                    material_type=typ or None,
                    remark=remark or None,
                    unit=unit or "pcs",
                    safety_stock=0
                )
                db.session.add(m)
                db.session.flush()
                # create inventory row
                if not Inventory.query.filter_by(material_id=m.id).first():
                    db.session.add(Inventory(material_id=m.id, on_hand=0, reserved=0))
            else:
                m.material_name = name
                m.drawing_no = drawing_no or None
                m.material_type = typ or None
                m.remark = remark or None
                m.unit = unit or m.unit

            # upsert product node (every node to allow expansion)
            p = Product.query.filter_by(product_code=code).first()
            if not p:
                p = Product(product_code=code, product_name=name, version=None)
                db.session.add(p)
                db.session.flush()
            else:
                p.product_name = name

            if depth == 0:
                stack[0] = p
                # clear deeper
                for k in list(stack.keys()):
                    if k > 0:
                        del stack[k]
                continue

            parent = stack.get(depth - 1)
            if not parent:
                skipped += 1
                continue

            item = BOMItem.query.filter_by(product_id=parent.id, material_id=m.id).first()
            if item:
                item.qty_per_unit = qty
                updated_bom += 1
            else:
                db.session.add(BOMItem(product_id=parent.id, material_id=m.id, qty_per_unit=qty))
                created_bom += 1

            stack[depth] = p
            for k in list(stack.keys()):
                if k > depth:
                    del stack[k]

        db.session.commit()
        return jsonify({"bom_created": created_bom, "bom_updated": updated_bom, "skipped": skipped})

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)
