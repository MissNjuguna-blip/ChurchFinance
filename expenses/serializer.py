# finances/serializer.py
from datetime import timedelta
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import Expense

class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ["recorded_by"]

    def validate(self, attrs):
        """
        Validates that an expense of the same type hasn't already been 
        recorded during the current Sunday-to-Saturday cycle.
        """
        # Adjust 'expense_type' or 'category' to match the exact field name on your Expense model
        expense_type = attrs.get('expense_type') 
        expense_date = attrs.get('expense_date')   # Adjust if your field is named 'date' or 'created_at'

        if not expense_type or not expense_date:
            return attrs

        # Calculate the start of the week (Sunday)
        # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
        days_since_sunday = (expense_date.weekday() + 1) % 7
        start_of_week = expense_date - timedelta(days=days_since_sunday)
        end_of_week = start_of_week + timedelta(days=6)  # The following Saturday

        # Check for existing entries within this specific Sunday-to-Saturday bracket
        duplicate_query = Expense.objects.filter(
            expense_type=expense_type,
            expense_date__range=[start_of_week, end_of_week]
        )

        # Exclude the current instance if editing an existing entry
        if self.instance:
            duplicate_query = duplicate_query.exclude(id=self.instance.id)

        # Block duplicate entries within the same Sunday-to-Saturday cycle
        if duplicate_query.exists():
            raise ValidationError({
                "expense_date": (
                    f"An expense of type '{expense_type}' has already "
                    f"been recorded for the week starting Sunday, "
                    f"{start_of_week.strftime('%Y-%m-%d')}."
                )
            })

        return attrs
