from core.models import AuditLog


def create_audit_log(
    user,
    action,
    instance,
    description=None
):
    """
    Create an audit log for an object/action.
    """

    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        description=description
    )
