import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, time, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.db import transaction
from apps.accounts.models import RoleChoices, ShiftSchedule, User
from apps.announcements.models import Announcement
from apps.inventory.models import Inventory, PurchaseOrder, PurchaseOrderStatusChoices, Store
from apps.medicine.models import Manufacturer, Medicine, MedicineCategory
from apps.sales.models import SaleOrder, SaleOrderItem, SaleOrderStatusChoices


def C(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


def ensure_user(username, full_name, role, store=None, phone="", email=""):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "full_name": full_name,
            "role": role,
            "store": store,
            "phone": phone,
            "email": email,
            "is_active": True,
        },
    )
    changed = False
    if created:
        user.set_password("Admin@123")
        changed = True
    for field, value in {
        "full_name": full_name,
        "role": role,
        "store": store,
        "phone": phone,
        "email": email,
        "is_active": True,
    }.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            changed = True
    if changed:
        if not user.password:
            user.set_password("Admin@123")
        user.save()
    return user


def ensure_announcement(title, content, created_by):
    Announcement.objects.get_or_create(
        title=title,
        defaults={"content": content, "is_published": True, "created_by": created_by},
    )


def ensure_manufacturer(name, contact_person, contact_phone):
    obj, created = Manufacturer.objects.get_or_create(
        name=name,
        defaults={"contact_person": contact_person, "contact_phone": contact_phone},
    )
    if not created:
        changed = False
        if obj.contact_person != contact_person:
            obj.contact_person = contact_person
            changed = True
        if obj.contact_phone != contact_phone:
            obj.contact_phone = contact_phone
            changed = True
        if changed:
            obj.save()
    return obj


def ensure_category(name, description):
    obj, created = MedicineCategory.objects.get_or_create(name=name, defaults={"description": description})
    if not created and obj.description != description:
        obj.description = description
        obj.save(update_fields=["description"])
    return obj


def ensure_medicine(code, name, specification, unit, purchase_price, retail_price, manufacturer, category, approval_number):
    obj, created = Medicine.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "specification": specification,
            "unit": unit,
            "purchase_price": Decimal(purchase_price),
            "retail_price": Decimal(retail_price),
            "manufacturer": manufacturer,
            "category": category,
            "approval_number": approval_number,
            "is_active": True,
        },
    )
    if not created:
        changed = False
        for field, value in {
            "name": name,
            "specification": specification,
            "unit": unit,
            "purchase_price": Decimal(purchase_price),
            "retail_price": Decimal(retail_price),
            "manufacturer": manufacturer,
            "category": category,
            "approval_number": approval_number,
            "is_active": True,
        }.items():
            if getattr(obj, field) != value:
                setattr(obj, field, value)
                changed = True
        if changed:
            obj.save()
    return obj


def ensure_inventory(store, medicine, quantity, warning_threshold):
    obj, _ = Inventory.objects.get_or_create(
        store=store,
        medicine=medicine,
        defaults={"quantity": quantity, "warning_threshold": warning_threshold},
    )
    changed = False
    if obj.quantity < quantity:
        obj.quantity = quantity
        changed = True
    if obj.warning_threshold != warning_threshold:
        obj.warning_threshold = warning_threshold
        changed = True
    if changed:
        obj.save()
    return obj


def ensure_purchase_order(order_no, store, manufacturer, purchaser_name, planned_date, total_amount, status, item_summary, remark):
    obj, created = PurchaseOrder.objects.get_or_create(
        order_no=order_no,
        defaults={
            "store": store,
            "manufacturer": manufacturer,
            "purchaser_name": purchaser_name,
            "planned_date": planned_date,
            "total_amount": Decimal(total_amount),
            "status": status,
            "item_summary": item_summary,
            "remark": remark,
        },
    )
    if not created:
        changed = False
        for field, value in {
            "store": store,
            "manufacturer": manufacturer,
            "purchaser_name": purchaser_name,
            "planned_date": planned_date,
            "total_amount": Decimal(total_amount),
            "status": status,
            "item_summary": item_summary,
            "remark": remark,
        }.items():
            if getattr(obj, field) != value:
                setattr(obj, field, value)
                changed = True
        if changed:
            obj.save()
    return obj


def ensure_shift(store, salesperson, shift_date, shift_period, start_time, end_time, note, created_by):
    obj, _ = ShiftSchedule.objects.get_or_create(
        store=store,
        salesperson=salesperson,
        shift_date=shift_date,
        shift_period=shift_period,
        defaults={
            "start_time": start_time,
            "end_time": end_time,
            "note": note,
            "created_by": created_by,
        },
    )
    changed = False
    for field, value in {
        "start_time": start_time,
        "end_time": end_time,
        "note": note,
        "created_by": created_by,
    }.items():
        if getattr(obj, field) != value:
            setattr(obj, field, value)
            changed = True
    if changed:
        obj.save()
    return obj


def seed_orders(salespeople, medicine_map):
    customer_names = [
        C(r"\u5218\u5148\u751f"),
        C(r"\u4f55\u5973\u58eb"),
        C(r"\u90d1\u963f\u59e8"),
        C(r"\u5434\u5148\u751f"),
        C(r"\u5510\u5973\u58eb"),
        C(r"\u51af\u540c\u5b66"),
        C(r"\u9ad8\u5148\u751f"),
        C(r"\u9648\u963f\u59e8"),
        C(r"\u9646\u5973\u58eb"),
        C(r"\u80e1\u5148\u751f"),
        C(r"\u6731\u5973\u58eb"),
        C(r"\u9648\u5148\u751f"),
    ]
    order_statuses = [
        SaleOrderStatusChoices.PENDING_PAYMENT,
        SaleOrderStatusChoices.ORDERED,
        SaleOrderStatusChoices.COMPLETED,
    ]
    medicine_keys = list(medicine_map.keys())
    order_index = 300
    for idx, salesperson in enumerate(salespeople):
        for offset in range(2):
            order_no = f"SO20260403{order_index:03d}"
            order_index += 1
            if SaleOrder.objects.filter(order_no=order_no).exists():
                continue
            status = order_statuses[(idx + offset) % len(order_statuses)]
            customer_name = customer_names[(idx * 2 + offset) % len(customer_names)]
            phone = f"1390000{order_index:04d}"[-11:]
            med_a = medicine_map[medicine_keys[(idx + offset) % len(medicine_keys)]]
            med_b = medicine_map[medicine_keys[(idx + offset + 4) % len(medicine_keys)]]
            qty_a = 1 + ((idx + offset) % 3)
            qty_b = 1 + ((idx + offset + 1) % 2)
            total_amount = (med_a.retail_price * qty_a) + (med_b.retail_price * qty_b)
            order = SaleOrder.objects.create(
                order_no=order_no,
                store=salesperson.store,
                salesperson=salesperson,
                customer_name=customer_name,
                customer_phone=phone,
                order_status=status,
                total_amount=total_amount,
                remark=C(r"\u6f14\u793a\u9500\u552e\u8ba2\u5355\u6570\u636e"),
            )
            SaleOrderItem.objects.create(order=order, medicine=med_a, quantity=qty_a, unit_price=med_a.retail_price, amount=med_a.retail_price * qty_a)
            SaleOrderItem.objects.create(order=order, medicine=med_b, quantity=qty_b, unit_price=med_b.retail_price, amount=med_b.retail_price * qty_b)
            inv_a = ensure_inventory(salesperson.store, med_a, 120, 18)
            inv_b = ensure_inventory(salesperson.store, med_b, 120, 18)
            inv_a.quantity = max(inv_a.quantity - qty_a, 0)
            inv_b.quantity = max(inv_b.quantity - qty_b, 0)
            inv_a.save(update_fields=["quantity", "updated_at"])
            inv_b.save(update_fields=["quantity", "updated_at"])


with transaction.atomic():
    stores = {store.code: store for store in Store.objects.order_by("id")}
    system_admin = User.objects.filter(role=RoleChoices.SYSTEM_ADMIN).order_by("id").first()

    pharmacy_admin_specs = [
        ("centeradmin2", C(r"\u5e02\u4e2d\u5fc3\u526f\u5e97\u957f"), stores["ST001"], "13821010001", "centeradmin2@example.com"),
        ("eastadmin2", C(r"\u4e1c\u533a\u503c\u73ed\u7ecf\u7406"), stores["ST002"], "13821010002", "eastadmin2@example.com"),
        ("campusadmin2", C(r"\u5927\u5b66\u57ce\u526f\u5e97\u957f"), stores["ST006"], "13821010003", "campusadmin2@example.com"),
    ]
    for username, full_name, store, phone, email in pharmacy_admin_specs:
        ensure_user(username, full_name, RoleChoices.PHARMACY_ADMIN, store=store, phone=phone, email=email)

    salesperson_specs = [
        ("sales07", C(r"\u9500\u552e\u545807"), stores["ST001"], "13921010007"),
        ("sales08", C(r"\u9500\u552e\u545808"), stores["ST002"], "13921010008"),
        ("sales09", C(r"\u9500\u552e\u545809"), stores["ST003"], "13921010009"),
        ("sales10", C(r"\u9500\u552e\u545810"), stores["ST004"], "13921010010"),
        ("sales11", C(r"\u9500\u552e\u545811"), stores["ST005"], "13921010011"),
        ("sales12", C(r"\u9500\u552e\u545812"), stores["ST006"], "13921010012"),
        ("sales13", C(r"\u9500\u552e\u545813"), stores["ST001"], "13921010013"),
        ("sales14", C(r"\u9500\u552e\u545814"), stores["ST002"], "13921010014"),
    ]
    for username, full_name, store, phone in salesperson_specs:
        ensure_user(username, full_name, RoleChoices.SALESPERSON, store=store, phone=phone, email=f"{username}@example.com")

    announcement_specs = [
        (C(r"\u6e05\u660e\u8282\u95e8\u5e97\u8f6e\u73ed\u5b89\u6392\u901a\u77e5"), C(r"\u8bf7\u5404\u95e8\u5e97\u7ba1\u7406\u5458\u5728\u4e0b\u73ed\u524d\u786e\u8ba4\u8282\u5047\u65e5\u8425\u4e1a\u65f6\u95f4\u548c\u503c\u73ed\u540d\u5355\u3002")),
        (C(r"\u6162\u75c5\u836f\u54c1\u5e93\u5b58\u9884\u8b66\u63d0\u9192"), C(r"\u964d\u538b\u5e73\u7247\u3001\u4e8c\u7532\u53cc\u80cd\u7247\u7b49\u6162\u75c5\u836f\u54c1\u9700\u91cd\u70b9\u5173\u6ce8\u5e93\u5b58\u53d8\u52a8\u3002")),
        (C(r"\u51b7\u94fe\u836f\u54c1\u6e29\u5ea6\u8bb0\u5f55\u68c0\u67e5"), C(r"\u8bf7\u5404\u95e8\u5e97\u6309\u65f6\u5b8c\u6210\u51b7\u94fe\u836f\u54c1\u6e29\u5ea6\u767b\u8bb0\uff0c\u907f\u514d\u9057\u6f0f\u3002")),
        (C(r"\u4f1a\u5458\u65e5\u6d3b\u52a8\u5ba3\u4f20\u8981\u6c42"), C(r"\u672c\u5468\u672b\u5c06\u5f00\u5c55\u4f1a\u5458\u65e5\u6ee1\u51cf\u6d3b\u52a8\uff0c\u8bf7\u9500\u552e\u4eba\u5458\u4e3b\u52a8\u5f15\u5bfc\u3002")),
        (C(r"\u6708\u672b\u9500\u552e\u5bf9\u8d26\u63d0\u9192"), C(r"\u8bf7\u5404\u95e8\u5e97\u4e8e\u6bcf\u6708\u6700\u540e\u4e00\u4e2a\u5de5\u4f5c\u65e5\u4e0b\u5348\u5b8c\u6210\u9500\u552e\u5bf9\u8d26\u4e0e\u4ea4\u73ed\u3002")),
    ]
    for title, content in announcement_specs:
        ensure_announcement(title, content, system_admin)

    manufacturer_specs = [
        (C(r"\u534e\u5317\u5236\u836f\u4f9b\u5e94\u94fe"), C(r"\u9ec4\u4e3b\u4efb"), "020-76110001"),
        (C(r"\u5cad\u5357\u4e2d\u836f\u5382"), C(r"\u6881\u7ecf\u7406"), "020-76110002"),
        (C(r"\u767e\u6c47\u5eb7\u590d\u836f\u4e1a"), C(r"\u8d75\u4e3b\u7ba1"), "020-76110003"),
        (C(r"\u6676\u76db\u836f\u4e1a\u516c\u53f8"), C(r"\u5434\u4e13\u5458"), "020-76110004"),
    ]
    manufacturer_map = {m.name: m for m in Manufacturer.objects.all()}
    for name, person, phone in manufacturer_specs:
        manufacturer_map[name] = ensure_manufacturer(name, person, phone)

    category_specs = [
        (C(r"\u4e2d\u6210\u836f"), C(r"\u4ee5\u4e2d\u836f\u6210\u5206\u4e3a\u4e3b\u7684\u5e38\u7528\u836f\u54c1\u3002")),
        (C(r"\u547c\u5438\u7528\u836f"), C(r"\u7528\u4e8e\u54b3\u55fd\u3001\u54bd\u75db\u7b49\u547c\u5438\u9053\u75c7\u72b6\u3002")),
        (C(r"\u513f\u79d1\u7528\u836f"), C(r"\u9002\u7528\u4e8e\u513f\u7ae5\u5e38\u89c1\u75c5\u75c7\u7684\u836f\u54c1\u3002")),
    ]
    category_map = {c.name: c for c in MedicineCategory.objects.all()}
    for name, description in category_specs:
        category_map[name] = ensure_category(name, description)

    medicine_specs = [
        ("MED016", C(r"\u677f\u84dd\u6839\u9897\u7c92"), "10g*20\u888b", C(r"\u76d2"), "12.50", "18.00", C(r"\u5cad\u5357\u4e2d\u836f\u5382"), C(r"\u4e2d\u6210\u836f"), "ZC202604016"),
        ("MED017", C(r"\u8fde\u82b1\u6e05\u761f\u80f6\u56ca"), "0.35g*24\u7c92", C(r"\u76d2"), "19.80", "29.00", C(r"\u534e\u5317\u5236\u836f\u4f9b\u5e94\u94fe"), C(r"\u4e2d\u6210\u836f"), "ZC202604017"),
        ("MED018", C(r"\u5ddd\u8d1d\u6797\u6777\u818f"), "120ml", C(r"\u74f6"), "15.00", "22.00", C(r"\u6676\u76db\u836f\u4e1a\u516c\u53f8"), C(r"\u547c\u5438\u7528\u836f"), "ZC202604018"),
        ("MED019", C(r"\u590d\u65b9\u6c28\u915a\u70f7\u80fa\u7247"), "12\u7247*2\u677f", C(r"\u76d2"), "8.60", "13.50", C(r"\u5eb7\u5065\u751f\u7269\u6709\u9650\u516c\u53f8"), C(r"\u611f\u5192\u836f"), "ZC202604019"),
        ("MED020", C(r"\u53cc\u9ec4\u8fde\u53e3\u670d\u6db2"), "10ml*10\u652f", C(r"\u76d2"), "14.20", "21.00", C(r"\u5cad\u5357\u4e2d\u836f\u5382"), C(r"\u4e2d\u6210\u836f"), "ZC202604020"),
        ("MED021", C(r"\u76d0\u9178\u5de6\u6c27\u6c1f\u6c99\u661f\u7247"), "0.5g*6\u7247", C(r"\u76d2"), "16.50", "24.00", C(r"\u534e\u5357\u5236\u836f\u80a1\u4efd\u6709\u9650\u516c\u53f8"), C(r"\u6297\u751f\u7d20"), "ZC202604021"),
        ("MED022", C(r"\u6c28\u6c2f\u5730\u5e73\u7247"), "5mg*28\u7247", C(r"\u76d2"), "11.80", "18.50", C(r"\u767e\u6c47\u5eb7\u590d\u836f\u4e1a"), C(r"\u6162\u75c5\u7528\u836f"), "ZC202604022"),
        ("MED023", C(r"\u963f\u53f8\u5339\u6797\u80a0\u6eb6\u7247"), "100mg*30\u7247", C(r"\u76d2"), "9.80", "15.00", C(r"\u4e1c\u5357\u767d\u836f"), C(r"\u6162\u75c5\u7528\u836f"), "ZC202604023"),
        ("MED024", C(r"\u85ff\u9999\u6b63\u6c14\u53e3\u670d\u6db2"), "10ml*10\u652f", C(r"\u76d2"), "13.00", "19.80", C(r"\u5eb7\u5065\u751f\u7269\u6709\u9650\u516c\u53f8"), C(r"\u80a0\u80c3\u7528\u836f"), "ZC202604024"),
        ("MED025", C(r"\u5f00\u585e\u9732"), "20ml*2\u652f", C(r"\u76d2"), "5.60", "9.00", C(r"\u5b89\u548c\u5065\u5eb7\u836f\u4e1a"), C(r"\u80a0\u80c3\u7528\u836f"), "ZC202604025"),
        ("MED026", C(r"\u5c0f\u513f\u67f4\u6842\u9000\u70ed\u9897\u7c92"), "5g*10\u888b", C(r"\u76d2"), "10.20", "16.00", C(r"\u6676\u76db\u836f\u4e1a\u516c\u53f8"), C(r"\u513f\u79d1\u7528\u836f"), "ZC202604026"),
        ("MED027", C(r"\u5c0f\u513f\u6c28\u916c\u9ec4\u90a3\u654f\u9897\u7c92"), "6g*10\u888b", C(r"\u76d2"), "13.20", "19.00", C(r"\u767e\u6c47\u5eb7\u590d\u836f\u4e1a"), C(r"\u513f\u79d1\u7528\u836f"), "ZC202604027"),
    ]
    medicine_map = {m.code: m for m in Medicine.objects.all()}
    for code, name, specification, unit, purchase_price, retail_price, manufacturer_name, category_name, approval_number in medicine_specs:
        manufacturer = manufacturer_map[manufacturer_name]
        category = category_map[category_name]
        medicine_map[code] = ensure_medicine(code, name, specification, unit, purchase_price, retail_price, manufacturer, category, approval_number)

    inventory_plan = {
        "ST001": ["MED001", "MED002", "MED003", "MED004", "MED016", "MED017", "MED018", "MED022", "MED023", "MED026"],
        "ST002": ["MED001", "MED005", "MED006", "MED007", "MED017", "MED019", "MED020", "MED022", "MED024", "MED027"],
        "ST003": ["MED002", "MED004", "MED008", "MED009", "MED016", "MED018", "MED021", "MED023", "MED024", "MED026"],
        "ST004": ["MED003", "MED005", "MED010", "MED011", "MED017", "MED019", "MED020", "MED021", "MED025", "MED027"],
        "ST005": ["MED001", "MED006", "MED012", "MED013", "MED016", "MED018", "MED022", "MED023", "MED024", "MED025"],
        "ST006": ["MED002", "MED007", "MED014", "MED015", "MED017", "MED020", "MED021", "MED024", "MED026", "MED027"],
    }
    for store_code, codes in inventory_plan.items():
        store = stores[store_code]
        for idx, code in enumerate(codes):
            ensure_inventory(store, medicine_map[code], 60 + idx * 9, 12 + (idx % 4) * 3)

    pharmacy_admins = {user.store_id: user for user in User.objects.filter(role=RoleChoices.PHARMACY_ADMIN).order_by("id") if user.store_id and user.store_id not in []}
    purchase_specs = [
        ("PO2026040301", "ST001", C(r"\u5e7f\u5dde\u533b\u836f\u96c6\u56e2"), C(r"\u95e8\u5e97\u6625\u5b63\u8865\u8d27\u8ba1\u5212"), PurchaseOrderStatusChoices.ORDERED, "1380.00", 3, C(r"\u611f\u5192\u836f\u3001\u9000\u70e7\u836f\u8865\u8d27")),
        ("PO2026040302", "ST002", C(r"\u6676\u76db\u836f\u4e1a\u516c\u53f8"), C(r"\u4e1c\u533a\u95e8\u5e97\u5468\u5ea6\u91c7\u8d2d"), PurchaseOrderStatusChoices.PENDING, "920.00", 5, C(r"\u54b3\u55fd\u7c7b\u548c\u80a0\u80c3\u7528\u836f\u8865\u8d27")),
        ("PO2026040303", "ST003", C(r"\u767e\u6c47\u5eb7\u590d\u836f\u4e1a"), C(r"\u5357\u7ad9\u95e8\u5e97\u6708\u4e2d\u91c7\u8d2d"), PurchaseOrderStatusChoices.RECEIVED, "1560.00", 2, C(r"\u6162\u75c5\u836f\u548c\u513f\u79d1\u7528\u836f\u5230\u8d27")),
        ("PO2026040304", "ST004", C(r"\u5eb7\u5065\u751f\u7269\u6709\u9650\u516c\u53f8"), C(r"\u897f\u533a\u95e8\u5e97\u5047\u65e5\u5907\u8d27"), PurchaseOrderStatusChoices.ORDERED, "1040.00", 4, C(r"\u611f\u5192\u836f\u548c\u4e2d\u6210\u836f\u589e\u8865")),
        ("PO2026040305", "ST005", C(r"\u4e1c\u5357\u767d\u836f"), C(r"\u5317\u57ce\u95e8\u5e97\u4f1a\u5458\u65e5\u5907\u8d27"), PurchaseOrderStatusChoices.PENDING, "1188.00", 6, C(r"\u5fc3\u8840\u7ba1\u548c\u80a0\u80c3\u7528\u836f\u8865\u8d27")),
        ("PO2026040306", "ST006", C(r"\u5cad\u5357\u4e2d\u836f\u5382"), C(r"\u5927\u5b66\u57ce\u95e8\u5e97\u5468\u672b\u5907\u8d27"), PurchaseOrderStatusChoices.ORDERED, "980.00", 3, C(r"\u513f\u79d1\u7528\u836f\u4e0e\u547c\u5438\u7528\u836f\u91c7\u8d2d")),
        ("PO2026040307", "ST001", C(r"\u534e\u5317\u5236\u836f\u4f9b\u5e94\u94fe"), C(r"\u5e02\u4e2d\u5fc3\u95e8\u5e97\u6162\u75c5\u836f\u8865\u8d27"), PurchaseOrderStatusChoices.PENDING, "1420.00", 7, C(r"\u9ad8\u8840\u538b\u3001\u7cd6\u5c3f\u75c5\u836f\u54c1\u91c7\u8d2d")),
        ("PO2026040308", "ST002", C(r"\u5b89\u548c\u5065\u5eb7\u836f\u4e1a"), C(r"\u4e1c\u533a\u95e8\u5e97\u5916\u7528\u836f\u5907\u8d27"), PurchaseOrderStatusChoices.RECEIVED, "760.00", 1, C(r"\u5916\u7528\u836f\u53ca\u6d88\u6bd2\u7528\u54c1\u5230\u8d27")),
    ]
    for order_no, store_code, manufacturer_name, remark, status, total_amount, days_offset, summary in purchase_specs:
        store = stores[store_code]
        admin = User.objects.filter(role=RoleChoices.PHARMACY_ADMIN, store=store).order_by("id").first()
        ensure_purchase_order(
            order_no,
            store,
            manufacturer_map[manufacturer_name],
            admin.full_name if admin else C(r"\u95e8\u5e97\u7ba1\u7406\u5458"),
            date.today() + timedelta(days=days_offset),
            total_amount,
            status,
            summary,
            remark,
        )

    shift_note_cycle = [
        C(r"\u65e9\u73ed\u5f00\u67b6\u503c\u5b88"),
        C(r"\u4e2d\u73ed\u5ba2\u6d41\u9ad8\u5cf0\u652f\u63f4"),
        C(r"\u665a\u73ed\u7ed3\u5e10\u4e0e\u4ea4\u63a5\u73ed"),
    ]
    shift_periods = [
        ("morning", time(8, 0), time(12, 0)),
        ("afternoon", time(13, 0), time(17, 30)),
        ("evening", time(17, 30), time(22, 0)),
    ]
    all_salespeople = list(User.objects.filter(role=RoleChoices.SALESPERSON).select_related("store").order_by("id"))
    for idx, salesperson in enumerate(all_salespeople):
        admin = User.objects.filter(role=RoleChoices.PHARMACY_ADMIN, store=salesperson.store).order_by("id").first()
        for day_offset in range(2):
            period_name, start_time, end_time = shift_periods[(idx + day_offset) % len(shift_periods)]
            ensure_shift(
                salesperson.store,
                salesperson,
                date.today() + timedelta(days=day_offset),
                period_name,
                start_time,
                end_time,
                shift_note_cycle[(idx + day_offset) % len(shift_note_cycle)],
                admin,
            )

    order_medicine_map = {
        "cold": medicine_map["MED001"],
        "antibiotic": medicine_map["MED002"],
        "vitamin": medicine_map["MED003"],
        "fever": medicine_map["MED004"],
        "stomach": medicine_map["MED005"],
        "herbal": medicine_map["MED016"],
        "capsule": medicine_map["MED017"],
        "chronic": medicine_map["MED022"],
        "heart": medicine_map["MED023"],
        "child": medicine_map["MED026"],
    }
    seed_orders(all_salespeople, order_medicine_map)

    print("store:", Store.objects.count())
    print("sys_user:", User.objects.count())
    print("announcement:", Announcement.objects.count())
    print("manufacturer:", Manufacturer.objects.count())
    print("medicine_category:", MedicineCategory.objects.count())
    print("medicine:", Medicine.objects.count())
    print("inventory:", Inventory.objects.count())
    print("purchase_order:", PurchaseOrder.objects.count())
    print("shift_schedule:", ShiftSchedule.objects.count())
    print("sale_order:", SaleOrder.objects.count())
    print("sale_order_item:", SaleOrderItem.objects.count())
