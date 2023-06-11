from products.models import HandlingUnit, HandlingUnitMovement


def create_HU(
    manufacturer,
    hu_issued_by,
    company,
    location,
    product,
    qty,
    qty_units,
    batch_nr,
    release_date,
):
    HandlingUnit.objects.create(
        manufacturer=manufacturer,
        hu_issued_by=hu_issued_by,
        company=company,
        location=location,
        product=product,
        qty=qty,
        qty_units=qty_units,
        batch_nr=batch_nr,
        release_date=release_date,
    )

    hu_made = HandlingUnit.objects.filter(
        manufacturer=manufacturer,
        hu_issued_by=hu_issued_by,
        company=company,
        location=location,
        product=product,
        qty=qty,
        qty_units=qty_units,
        batch_nr=batch_nr,
        release_date=release_date,
        ).last()
    return hu_made


def create_HU_Movement(
    old_hu,
    hu_made,
    new_hu,
    date,
    doc_nr,
    from_location,
    to_location,
    from_hu,
    to_hu,
    qty,
):
    if old_hu != "-":
        HandlingUnitMovement.objects.create(
            hu=hu_made,
            date=date,
            doc_nr=doc_nr,
            from_location=from_location,
            to_location=to_location,
            from_hu=from_hu,
            to_hu=to_hu,
            qty=qty,
        )
    if hu_made != "-":
        HandlingUnitMovement.objects.create(
            hu=hu_made,
            date=date,
            doc_nr=doc_nr,
            from_location=from_location,
            to_location=to_location,
            from_hu=from_hu,
            to_hu=to_hu,
            qty=qty,
        )
    if new_hu != "-":
        HandlingUnitMovement.objects.create(
            hu=hu_made,
            date=date,
            doc_nr=doc_nr,
            from_location=from_location,
            to_location=to_location,
            from_hu=from_hu,
            to_hu=to_hu,
            qty=qty,
        )
