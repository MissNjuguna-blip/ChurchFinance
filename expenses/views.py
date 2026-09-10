from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Expense, AuditLog
from core.audit import create_audit_log
from expenses.serializer import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related(
        "recorded_by"
    ).all()

    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        expense = serializer.save(
            recorded_by=self.request.user
        )

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            instance=expense,
            description=(
                f"Created expense '{expense.description}' "
                f"of {expense.amount}"
            )
        )

    def perform_update(self, serializer):

        expense = serializer.save()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=expense,
            description=(
                f"Updated expense #{expense.id}"
            )
        )

    def perform_destroy(self, instance):

        expense_id = instance.id
        description = instance.description
        amount = instance.amount

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            instance=instance,
            description=(
                f"Deleted expense #{expense_id}: "
                f"{description} ({amount})"
            )
        )

        instance.delete()
