def bulk_update(original_set, data, serializer_class, on_save_fn=None):
    
    need_delete_set = original_set.exclude(id__in=[o["id"] for o in data])
    need_create_set = []
    need_updated_set = []

    # validate
    for d in data:
        if d["id"] > 0:
            serializer = serializer_class(original_set.get(id=d["id"]), data=d)
            serializer.is_valid(raise_exception=True)
            need_updated_set.append((serializer, d))
            continue

        del d["id"]
        serializer = serializer_class(data=d)
        serializer.is_valid(raise_exception=True)
        need_create_set.append((serializer, d))

    # perform change
    need_delete_set.delete()
    for s in need_create_set:
        instance = s[0].save()
        if on_save_fn:
            on_save_fn(s[0], s[1], instance)
    for s in need_updated_set:
        instance = s[0].save()
        if on_save_fn:
            on_save_fn(s[1], s[1], instance)
