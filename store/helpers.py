from store.models import Store


def update_store_services(employee_details):
    skills = employee_details.get("employee_skills")
    print("skills", skills)
    store_id = employee_details.get("store_id")

    if not skills or not store_id:
        return

    store = None
    if Store.objects.filter(store_id=store_id, is_deleted=False).exists():
        store = Store.objects.get(
            store_id=store_id,
            is_deleted=False
        )

    if store.store_services == None:
        store.store_services = {"service_list": skills}
        store.save()
    else:
        existing_services = list(store.store_services["service_list"])
        updated_services = list(set(existing_services + skills))
        store.store_services = {"service_list": updated_services}
        store.save()


def updpate_store_langauges(employee_details):
    langauges = employee_details.get("employee_langauges")
    print("langauges", langauges)
    store_id = employee_details.get("store_id")

    if not langauges or not store_id:
        return

    store = None
    if Store.objects.filter(store_id=store_id, is_deleted=False).exists():
        store = Store.objects.get(
            store_id=store_id,
            is_deleted=False
        )

    if store.store_langauges == None:
        store.store_langauges = {"langauge_list": langauges}
        store.save()
    else:
        existing_langauges = list(store.store_langauges["langauge_list"])
        updated_langauges = list(set(existing_langauges + langauges))
        store.store_langauges = {"langauge_list": updated_langauges}
        store.save()
